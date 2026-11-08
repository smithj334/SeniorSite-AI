"""
SeniorSite AI - LLM Interface Module
Handles natural language query processing using LangChain and Ollama
"""

import re
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from database import get_connection, get_schema_description, execute_query
from config import OLLAMA_BASE_URL, OLLAMA_MODEL
import pandas as pd


def get_llm():
    """Initialize and return the Ollama LLM instance."""
    return OllamaLLM(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=0.1  # Low temperature for consistent SQL generation
    )


def check_ollama_connection():
    """Check if Ollama is running and the model is available."""
    try:
        llm = get_llm()
        response = llm.invoke("Say 'connected' if you can read this.")
        return "connected" in response.lower()
    except Exception as e:
        return False


# SQL Generation Prompt
SQL_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template="""You are a SQL expert assistant for a senior housing site selection database.

{schema}

Given the user's question, generate a DuckDB-compatible SQL query to answer it.

IMPORTANT RULES:
1. Only generate SELECT queries - never INSERT, UPDATE, DELETE, or DROP
2. Use the exact column and table names from the schema
3. For county filtering, use county_name (e.g., 'Collin County', 'Harris County') or county_fips
4. For metro filtering, use metro_area = 'Houston' or metro_area = 'DFW'
5. When asked about "senior population" or "seniors", use pop_75_plus (standard for senior housing analysis)
6. When asked about "elderly" or "older adults", use pop_65_plus
7. For income filtering, use median_income_65_plus for senior income or income_qualified_il/income_qualified_al
8. Always include relevant columns for context (county_name, metro_area when helpful)
9. Order results meaningfully (usually by the key metric descending)
10. Limit results to 20 unless specifically asked for more

USER QUESTION: {question}

Respond with ONLY the SQL query, nothing else. No explanations, no markdown formatting, just the raw SQL.
"""
)


# Response Synthesis Prompt  
RESPONSE_SYNTHESIS_PROMPT = PromptTemplate(
    input_variables=["question", "sql_query", "results"],
    template="""You are a senior housing market analyst assistant. A user asked a question, you queried the database, and now you need to synthesize the results into a helpful response.

USER QUESTION: {question}

SQL QUERY EXECUTED: {sql_query}

QUERY RESULTS:
{results}

Provide a clear, professional response that:
1. Directly answers the user's question
2. Highlights key findings from the data
3. Provides relevant context (e.g., what the numbers mean for senior housing development)
4. If results are empty, explain what that means and suggest alternative queries
5. Keep the response concise but informative

For senior housing context:
- Penetration rate below 8% = undersupplied market (opportunity)
- Penetration rate 8-12% = balanced market
- Penetration rate above 15% = saturated market
- 75+ population is the primary target demographic
- Income qualification of $48,000+ suggests Independent Living affordability
- Income qualification of $60,000+ suggests Assisted Living affordability

Respond in a conversational but professional tone. Use bullet points for lists of data.
"""
)


def clean_sql_query(query: str) -> str:
    """Clean and validate a generated SQL query."""
    # Remove markdown code blocks if present
    query = re.sub(r'```sql\s*', '', query)
    query = re.sub(r'```\s*', '', query)
    query = query.strip()
    
    # Remove any leading/trailing quotes
    query = query.strip('"\'')
    
    # Basic safety check - only allow SELECT
    if not query.upper().startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    
    # Check for dangerous keywords
    dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']
    query_upper = query.upper()
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            raise ValueError(f"Dangerous keyword '{keyword}' not allowed")
    
    return query


def generate_sql_query(question: str) -> str:
    """Generate a SQL query from a natural language question."""
    llm = get_llm()
    schema = get_schema_description()
    
    # Create chain using modern LCEL syntax
    chain = SQL_GENERATION_PROMPT | llm | StrOutputParser()
    
    response = chain.invoke({
        "schema": schema,
        "question": question
    })
    
    # Clean and validate
    sql_query = clean_sql_query(response)
    
    return sql_query


def execute_natural_language_query(question: str) -> dict:
    """
    Process a natural language question end-to-end.
    Returns the SQL query, results, and synthesized response.
    """
    result = {
        "question": question,
        "sql_query": None,
        "raw_results": None,
        "response": None,
        "error": None
    }
    
    try:
        # Generate SQL
        sql_query = generate_sql_query(question)
        result["sql_query"] = sql_query
        
        # Execute query
        df = execute_query(sql_query)
        result["raw_results"] = df
        
        # Format results for synthesis
        if len(df) == 0:
            results_text = "No results found."
        else:
            results_text = df.to_string(index=False)
        
        # Synthesize response using modern LCEL syntax
        llm = get_llm()
        synthesis_chain = RESPONSE_SYNTHESIS_PROMPT | llm | StrOutputParser()
        
        synthesis_response = synthesis_chain.invoke({
            "question": question,
            "sql_query": sql_query,
            "results": results_text
        })
        
        result["response"] = synthesis_response
        
    except Exception as e:
        result["error"] = str(e)
        result["response"] = f"I encountered an error processing your question: {str(e)}. Could you try rephrasing it?"
    
    return result


def get_quick_stats() -> dict:
    """Get quick statistics about the database for display."""
    conn = get_connection()
    
    stats = {}
    
    # Total ZIP codes
    stats['total_zip_codes'] = conn.execute(
        "SELECT COUNT(*) FROM demographics"
    ).fetchone()[0]
    
    # Total 75+ population
    stats['total_pop_75_plus'] = conn.execute(
        "SELECT SUM(pop_75_plus) FROM demographics"
    ).fetchone()[0]
    
    # Healthcare facilities
    stats['healthcare_facilities'] = conn.execute(
        "SELECT COUNT(*) FROM healthcare_facilities"
    ).fetchone()[0]
    
    # Senior housing communities
    stats['senior_housing_communities'] = conn.execute(
        "SELECT COUNT(*) FROM senior_housing"
    ).fetchone()[0]
    
    # Total senior housing units
    stats['total_senior_units'] = conn.execute(
        "SELECT SUM(unit_count) FROM senior_housing"
    ).fetchone()[0]
    
    # By metro area
    metro_stats = conn.execute("""
        SELECT metro_area, 
               COUNT(*) as zip_count,
               SUM(pop_75_plus) as pop_75_plus,
               ROUND(AVG(median_income_65_plus), 0) as avg_income_65
        FROM demographics
        GROUP BY metro_area
    """).fetchall()
    
    stats['by_metro'] = {
        row[0]: {
            'zip_count': row[1],
            'pop_75_plus': row[2],
            'avg_income_65': row[3]
        } for row in metro_stats
    }
    
    conn.close()
    return stats


# Predefined query templates for common questions
QUERY_TEMPLATES = {
    "top_markets": """
        SELECT zip_code, county_name, metro_area, pop_75_plus, 
               median_income_65_plus, income_qualified_il
        FROM demographics
        WHERE pop_75_plus > 2000
        ORDER BY pop_75_plus DESC
        LIMIT 10
    """,
    
    "houston_demographics": """
        SELECT zip_code, county_name, pop_75_plus, pct_75_plus,
               median_income_65_plus, income_qualified_il
        FROM demographics
        WHERE metro_area = 'Houston'
        ORDER BY pop_75_plus DESC
    """,
    
    "dfw_demographics": """
        SELECT zip_code, county_name, pop_75_plus, pct_75_plus,
               median_income_65_plus, income_qualified_il
        FROM demographics
        WHERE metro_area = 'DFW'
        ORDER BY pop_75_plus DESC
    """,
    
    "high_income_seniors": """
        SELECT zip_code, county_name, metro_area, pop_75_plus,
               median_income_65_plus, income_qualified_al
        FROM demographics
        WHERE median_income_65_plus > 100000
        ORDER BY median_income_65_plus DESC
    """,
    
    "healthcare_facilities": """
        SELECT facility_name, facility_type, city, beds, overall_rating
        FROM healthcare_facilities
        ORDER BY beds DESC
    """,
    
    "senior_housing_inventory": """
        SELECT facility_name, facility_type, city, unit_count, year_built
        FROM senior_housing
        ORDER BY unit_count DESC
    """
}


def run_template_query(template_name: str) -> pd.DataFrame:
    """Run a predefined query template."""
    if template_name not in QUERY_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
    
    return execute_query(QUERY_TEMPLATES[template_name])


# Example questions for the UI
EXAMPLE_QUESTIONS = [
    "Show me ZIP codes in Collin County where the 75+ population exceeds 3,000",
    "What are the top 10 ZIP codes by senior population in the Houston metro?",
    "Find areas with median senior income above $100,000",
    "List all hospitals in the DFW area with more than 300 beds",
    "Which ZIP codes have the highest percentage of seniors?",
    "Show me senior housing communities with more than 200 units",
    "Compare demographics between Harris County and Dallas County",
    "Find high-income senior populations in Fort Bend County",
    "What healthcare facilities are in Montgomery County?",
    "Show me the largest senior housing competitors in Plano"
]


if __name__ == "__main__":
    # Test the LLM interface
    print("Testing LLM Interface...\n")
    
    # Check connection
    print("Checking Ollama connection...")
    if check_ollama_connection():
        print("✓ Ollama is connected!\n")
    else:
        print("✗ Ollama is not running. Please start Ollama first.\n")
        exit(1)
    
    # Test a query
    test_question = "Show me ZIP codes in Collin County where the 75+ population exceeds 2000"
    print(f"Test Question: {test_question}\n")
    
    result = execute_natural_language_query(test_question)
    
    print(f"Generated SQL:\n{result['sql_query']}\n")
    print(f"Response:\n{result['response']}")
