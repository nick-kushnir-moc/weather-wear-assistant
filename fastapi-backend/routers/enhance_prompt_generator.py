# enhance_prompt_generator.py

import os
import re
import json
import logging
import sys
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel
from langchain_community.llms import OpenAI as LangchainOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Configure Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


class EnhancePromptGenerator:
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.llm = LangchainOpenAI(openai_api_key=api_key, model=model)

    def determine_intent(self, action: str) -> str:
        """
        Determine the intent of a given action description.
        """
        try:
            prompt_template = PromptTemplate(
                input_variables=["action"],
                template=(
                    """Given the action description: '{action}', identify its intent based on the following categories and respond with only the intent name:
1. Viewing: For actions that directly request to see appointments (e.g., 'show me tomorrow's appointments').
2. Booking: For actions that request to create appointments (e.g., 'I want to book an appointment').
3. Querying Employee Data: For actions involving questions about employee schedules or details (e.g., 'show me Artem's schedule' or 'how many employees work on Friday?').
4. Unrelated: For any other actions not fitting the above categories.
Respond with only the intent: 'Viewing', 'Booking', 'Querying Employee Data', or 'Unrelated'."""
                )
            )
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            response = chain.run({"action": action})
            determined_intent = response.strip().lower()

            # Add more specific checks for keywords related to employee data queries
            if (
                "schedule" in action.lower()
                or "employee" in action.lower()
                or "work" in action.lower()
            ):
                determined_intent = "querying employee data"

            logger.debug(
                f"Action: '{action}' was determined as Intent: '{determined_intent}'"
            )

            return determined_intent

        except Exception as e:
            logger.error(f"Error determining intent: {e}")
            raise

    def generate_sql_query(self, action: str, schemas: str) -> str:
        """
        Generate an SQL query based on the action description and database schemas.
        """
        try:
            prompt_template = PromptTemplate(
                input_variables=["schemas", "action"],
                template=config.SQL_GENERATION_PROMPT  # Ensure this is defined in your configs
            )
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            response = chain.run({"schemas": schemas, "action": action})
            response_text = response.strip()

            # Validate SQL query
            forbidden_commands = ["delete", "remove", "drop", "alter"]
            for command in forbidden_commands:
                if command in response_text.lower():
                    raise ValueError("Generated query contains forbidden operations.")

            # Extract SQL query from the response
            sql_query = self.extract_sql_query(response_text)

            return sql_query

        except ValueError as ve:
            logger.error(f"Validation Error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise

    @staticmethod
    def extract_sql_query(response_text: str) -> str:
        """
        Extract the SQL query from the response text.
        """
        try:
            pattern = r"```sql\n(.*?)```"
            matches = re.search(pattern, response_text, re.DOTALL)
            if matches:
                sql_query = matches.group(1).strip()
                return sql_query
            else:
                # Fallback pattern
                pattern = r"```(.*?)```"
                matches = re.search(pattern, response_text, re.DOTALL)
                if matches:
                    sql_query = matches.group(1).strip()
                    return sql_query
                else:
                    # If no code block, return the entire response
                    return response_text.strip()
        except Exception as e:
            logger.error(f"Error extracting SQL query: {e}")
            raise

    def generate_user_friendly_message(self, action: str, result: Any) -> str:
        """
        Generate a user-friendly message based on the action and result.
        """
        try:
            prompt_template = PromptTemplate(
                input_variables=["result", "action"],
                template=config.USER_FRIENDLY_MESSAGE_PROMPT  # Ensure this is defined in your configs
            )
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            response = chain.run({"result": result, "action": action})
            response_text = response.strip()
            return response_text
        except Exception as e:
            logger.error(f"Error generating user-friendly message: {e}")
            raise

    def improve_prompt_quality(
        self,
        prompt_template: PromptTemplate,
        input_data: dict,
        iterations: int = 3,
        evaluation_func=None,
        refinement_func=None,
    ) -> str:
        """
        Iteratively improve prompt quality based on evaluations.
        """
        best_prompt = prompt_template.template
        best_response = ""
        best_score = -float('inf')

        for i in range(iterations):
            logger.info(f"Iteration {i+1}: Current best prompt -> {best_prompt}")

            # Update prompt template
            current_prompt = PromptTemplate(
                input_variables=prompt_template.input_variables,
                template=best_prompt
            )

            chain = LLMChain(llm=self.llm, prompt=current_prompt)

            # Generate response using the current best prompt
            response = chain.run(input_data)
            logger.info(f"Generated Response: {response}")

            # Evaluate response quality
            if evaluation_func:
                score = evaluation_func(response)
            else:
                score = self.default_evaluation(response)

            logger.info(f"Response Quality Score: {score}")

            # If the new score is better, update the best prompt and best score
            if score > best_score:
                best_score = score
                best_response = response
            else:
                # Modify the prompt to improve quality using refinement function
                if refinement_func:
                    best_prompt = refinement_func(best_prompt, response)
                else:
                    best_prompt += " Ensure the response is detailed and addresses all aspects."

        logger.info(f"Final Best Prompt: {best_prompt}")
        return best_response

    @staticmethod
    def default_evaluation(response: str) -> float:
        """
        Default evaluation function for response quality.
        """
        score = 0.0

        # Example criteria
        if "keyword1" in response:
            score += 1.0
        if "keyword2" in response:
            score += 1.0

        # Check response length
        word_count = len(response.split())
        if 50 <= word_count <= 150:
            score += 1.0

        return score

    @staticmethod
    def refine_prompt(current_prompt: str, last_response: str) -> str:
        """
        Refine the prompt based on the last response.
        """
        if "unexpected result" in last_response.lower():
            current_prompt += " Ensure the response is detailed and addresses all aspects."

        if "missing_keyword" not in last_response.lower():
            current_prompt += " Be sure to include 'missing_keyword' in the response."

        return current_prompt
