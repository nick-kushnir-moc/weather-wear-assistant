from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from configs import config
from typing import Dict, Any
from sqlalchemy.orm import Session
import psycopg2
import logging
import json
import re
from openai import OpenAI
from langchain_community.llms import OpenAI as LangchainOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from db import get_db
from datetime import datetime
import sys
import whisper
import tempfile
import os
from dotenv import load_dotenv
model = whisper.load_model("base")

load_dotenv()


class AppointmentSchema(BaseModel):
    employee_id: int
    title: str
    description: str = None
    start_time: datetime
    end_time: datetime
    status: str = 'scheduled'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

router = APIRouter()

# Database connection details
POSTGRES_HOST = "localhost"
POSTGRES_DBNAME = "postgres"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "mocAi"
POSTGRES_PORT = 5432
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Request body model
class Request(BaseModel):
    action: str
    parameters: Dict[str, Any] = {}

# Establish a connection to PostgreSQL database
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DBNAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        return conn
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error while connecting to PostgreSQL: {e}")

# Execute SQL query and fetch results
def execute_sql_query(sql_query):
    try:
        conn = connect_to_postgres()
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        return rows
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error executing SQL query: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
# need to check appointment for each employee and show me all appointments of artem from august from september so add llm here            
def fetch_appointments(db: Session):
    langchain_openai_client = LangchainOpenAI(openai_api_key=OPENAI_API_KEY)
    cursor = db.cursor()
    cursor.execute("SELECT title, description, start_time, end_time FROM appointments")
    appointments = cursor.fetchall()
    cursor.close()
    appointment_data = [
        {
            "title": app[0],
            "description": app[1],
            "start_time": app[2].strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": app[3].strftime("%Y-%m-%dT%H:%M:%S")
        }
        for app in appointments
    ]
    prompt_template = PromptTemplate(
        input_variables=["appointments"],
        template="Given the following list of appointment data: {appointments}, convert it into a structured JSON format suitable for a calendar application."
    )
    llm_chain = LLMChain(llm=langchain_openai_client, prompt=prompt_template)
    json_response = llm_chain.run({"appointments": json.dumps(appointment_data)})
    processed_appointments = json.loads(json_response.strip())
    return processed_appointments

def create_appointment(appointment_data: Dict[str, Any], db: Session):
    sql = """
    INSERT INTO appointments (employee_id, title, description, start_time, end_time, status)
    VALUES (%(employee_id)s, %(title)s, %(description)s, %(start_time)s, %(end_time)s, %(status)s) RETURNING *
    """
    cursor = db.cursor()
    try:
        cursor.execute(sql, appointment_data)
        appointment = cursor.fetchone()
        db.commit()
        if appointment:
            return dict(appointment)
        else:
            logger.error("No data was returned after inserting the appointment.")
            raise HTTPException(status_code=500, detail="No appointment data was returned after the insert.")
    except psycopg2.Error as e:
        logger.error("SQL Error during appointment creation: %s", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"SQL Error during appointment creation: {str(e)}")
    finally:
        cursor.close()

def determine_intent(action, langchain_client):
    prompt_template = PromptTemplate(
        input_variables=["action"],
        template=(
            """Given the action description: '{action}', identify its intent based on the following categories and respond with only the intent name:
	1.	Viewing: For actions that directly request to see appointments (e.g., 'show me tomorrow's appointments').
	2.	Booking: For actions that request to create appointments (e.g., 'I want to book an appointment').
	3.	Querying Employee Data: For actions involving questions about employee schedules or details (e.g., 'show me Artem's schedule' or 'how many employees work on Friday?').
	4.	Unrelated: For any other actions not fitting the above categories.
Respond with only the intent: 'Viewing', 'Booking', 'Querying Employee Data', or 'Unrelated'."""
        )
    )
    chain = LLMChain(llm=langchain_client, prompt=prompt_template)
    response = chain.run({"action": action})
    determined_intent = response.strip().lower()

    # Add more specific checks for keywords related to employee data queries
    if "schedule" in action.lower() or "employee" in action.lower() or "work" in action.lower():
        determined_intent = 'querying employee data'

    logger.debug("Action: '%s' was determined as Intent: '%s'", action, determined_intent)

    return determined_intent

def generate_sql_query(request: Request, db: Session):
    try:
        langchain_openai_client = LangchainOpenAI(openai_api_key=OPENAI_API_KEY)
        
        intent_template = PromptTemplate(
            input_variables=["action"],
            template="Determine the intent for this action: {action}. Is it related to viewing or setting appointments?"
        )
        intent_chain = LLMChain(llm=langchain_openai_client, prompt=intent_template)
        intent_response = intent_chain.run({"action": request.action})
        action_intent = intent_response.strip().lower()

        
        # prompt template
        prompt_template = PromptTemplate(
            input_variables=["schemas", "action"],
            template=config.SQL_GENERATION_PROMPT
        )
        
        chain = LLMChain(llm=langchain_openai_client, prompt=prompt_template)
        
        response = chain.run({"schemas": config.DATABASE_SCHEMAS, "action": request.action})
        
        response_text = response.strip()

        # Validate SQL query
        forbidden_commands = ["delete", "remove", "drop", "alter"]
        for command in forbidden_commands:
            if command in response_text.lower():
                raise HTTPException(status_code=400, detail="Generated query contains forbidden operations.")
        
        # Extract SQL query from the response
        sql_query_match = re.search(r"```sql\n(.*?)```", response_text, re.DOTALL)
        if sql_query_match:
            sql_query = sql_query_match.group(1).strip()
        else:
            # another pattern or handle different format
            sql_query_match = re.search(r"```(.*?)```", response_text, re.DOTALL)
            if sql_query_match:
                sql_query = sql_query_match.group(1).strip()
            else:
                sql_query = response_text
        
        return sql_query.strip()
    except HTTPException:
        raise  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL query: {e}")

# Generate user-friendly message using OpenAI
def generate_user_friendly_message(action: str, result: any):
    try:
        langchain_openai_client = LangchainOpenAI(openai_api_key=OPENAI_API_KEY)
        
        prompt_template = PromptTemplate(
            input_variables=["result", "action"],
            template=config.USER_FRIENDLY_MESSAGE_PROMPT
        )
        
        chain = LLMChain(llm=langchain_openai_client, prompt=prompt_template)
        
        response = chain.run({"result": result, "action": action})
        
        response_text = response.strip()
        return response_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating user-friendly message: {e}")
    
def improve_prompt_quality(prompt_template: PromptTemplate, input_data: dict, llm_chain: LLMChain, iterations: int = 3):
    best_prompt = prompt_template.template
    best_response = ""
    best_score = -float('inf')

    for i in range(iterations):
        print(f"Iteration {i+1}: Current best prompt -> {best_prompt}")
        
        # Generate response using the current best prompt
        response = llm_chain.run({"input_data": json.dumps(input_data)})
        print(f"Generated Response: {response}")

        score = evaluate_response_quality(response)
        print(f"Response Quality Score: {score}")

        # If the new score is better, update the best prompt and best score
        if score > best_score:
            best_score = score
            best_response = response
        else:
            # Modify the prompt to improve quality (customize this logic)
            best_prompt = refine_prompt(best_prompt, response)
            prompt_template = PromptTemplate(input_variables=["input_data"], template=best_prompt)
            llm_chain = LLMChain(llm=llm_chain.llm, prompt=prompt_template)

    print(f"Final Best Prompt: {best_prompt}")
    return best_response

def evaluate_response_quality(response: str) -> float:
    score = 0.0

    # Check if certain keywords or phrases are present
    if "expected_keyword" in response:
        score += 1.0
    if "another_important_keyword" in response:
        score += 1.0
    
    # Check response length (not too short or too long)
    if 50 <= len(response.split()) <= 150:
        score += 1.0

    return score

def refine_prompt(current_prompt: str, last_response: str) -> str:
    if "unexpected result" in last_response:
        current_prompt += " Ensure the response is detailed and addresses all aspects."

    if "missing_keyword" not in last_response:
        current_prompt += " Be sure to include 'missing_keyword' in the response."

    return current_prompt


@router.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Create a temporary file to store the uploaded audio data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        audio = whisper.load_audio(temp_file_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # Detect the language
        _, probs = model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        print(f"Detected language: {detected_language}")

        options = whisper.DecodingOptions()
        result = whisper.decode(model, mel, options)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return {
            "text": result.text,
            "language": detected_language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the audio: {e}")


@router.post("/create-appointment/")
async def new_appointment(appointment_data: AppointmentSchema, db: Session = Depends(get_db)):
    try:
        # This should automatically validate and parse `appointment_data` including `employee_id`
        new_appointment = create_appointment(appointment_data.dict(), db)
        return {"appointment": new_appointment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-message/")
async def generate_message(request: Request, db: Session = Depends(get_db)):
    try:
        action_type = request.action.lower()
        langchain_openai_client = LangchainOpenAI(api_key=OPENAI_API_KEY)

        # Determine the user intent using LangChain
        user_intent = determine_intent(request.action, langchain_openai_client)
        if user_intent == "viewing":
            appointments = fetch_appointments(db)
            return {"appointments": appointments}
        elif user_intent == "booking":
            return {"intent": "booking"}
        else:
            # Handle non-appointment related actions using SQL queries
            response_query = generate_sql_query(request, db)
            pattern = r"```sql\n(.*?)```"
            matches = re.search(pattern, response_query, re.DOTALL)
            if not matches:
                pattern = r"```(.*?)```"
                matches = re.search(pattern, response_query, re.DOTALL)
                sql_query = matches.group(1).strip() if matches else response_query.strip()

            # Execute the SQL query
            result = execute_sql_query(sql_query)

            # Generate the user-friendly message using another LangChain prompt
            user_friendly_message = generate_user_friendly_message(request.action, result)
        
            # Improve the prompt quality before generating the final message
            improved_response = improve_prompt_quality(prompt_template, {"result": result, "action": request.action}, llm_chain)
            return {"user_friendly_message": user_friendly_message}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")