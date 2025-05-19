from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class NLQueryRequest(BaseModel):
    """Request model for natural language query processing"""
    query: str = Field(..., description="Natural language query to process")
    
class QueryResponse(BaseModel):
    """Response model with query results"""
    original_query: str = Field(..., description="The original natural language query")
    sql_query: str = Field("", description="The generated SQL query")
    results: List[Dict[str, Any]] = Field([], description="Query results as a list of records")
    error: Optional[str] = Field(None, description="Error message, if any")
    user_message: Optional[str] = Field(None, description="User-friendly message describing the results")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata about the query")