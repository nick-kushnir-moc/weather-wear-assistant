from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import employee, department, reservation, open_ai_helper, appointments, schedules, nl_query, weather_assistant

app = FastAPI()

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5000",  # Common Svelte dev server port
    "http://localhost:5173",  # Vite dev server port (used by newer Svelte projects)
    "http://localhost:3000",  # Another common dev server port
    "*",      
]

@app.get("/")
async def root():
    return {"message": "Welcome to the Personal AI Assistant API"}

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

# Mounting routers
app.include_router(employee.router)
app.include_router(department.router)
app.include_router(reservation.router)
app.include_router(open_ai_helper.router)
app.include_router(appointments.router)
app.include_router(schedules.router)
app.include_router(nl_query.router)
app.include_router(weather_assistant.router)

# Database connection setup and dependencies
from db import get_db

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)