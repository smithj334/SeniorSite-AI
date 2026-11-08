"""
SeniorSite AI - Database Module
Handles DuckDB setup, schema creation, and data management
"""

import duckdb
from pathlib import Path
from config import DB_PATH

def get_connection():
    """Get a connection to the DuckDB database."""
    return duckdb.connect(str(DB_PATH))

def initialize_database():
    """Create all required tables if they don't exist."""
    conn = get_connection()
    
    # Demographics table - Census ACS data by ZIP code
    conn.execute("""
        CREATE TABLE IF NOT EXISTS demographics (
            zip_code VARCHAR PRIMARY KEY,
            county_fips VARCHAR,
            county_name VARCHAR,
            metro_area VARCHAR,
            total_population INTEGER,
            pop_65_plus INTEGER,
            pop_75_plus INTEGER,
            pop_85_plus INTEGER,
            median_household_income DOUBLE,
            median_income_65_plus DOUBLE,
            households_total INTEGER,
            households_65_plus INTEGER,
            owner_occupied_65_plus INTEGER,
            renter_occupied_65_plus INTEGER,
            pct_65_plus DOUBLE,
            pct_75_plus DOUBLE,
            income_qualified_il INTEGER,
            income_qualified_al INTEGER,
            latitude DOUBLE,
            longitude DOUBLE,
            data_year INTEGER
        )
    """)
    
    # Healthcare facilities table - CMS Provider Data
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthcare_facilities (
            facility_id VARCHAR PRIMARY KEY,
            facility_name VARCHAR,
            facility_type VARCHAR,
            address VARCHAR,
            city VARCHAR,
            state VARCHAR,
            zip_code VARCHAR,
            county_fips VARCHAR,
            phone VARCHAR,
            beds INTEGER,
            overall_rating INTEGER,
            latitude DOUBLE,
            longitude DOUBLE
        )
    """)
    
    # Senior housing inventory - Existing competitors
    conn.execute("""
        CREATE TABLE IF NOT EXISTS senior_housing (
            facility_id VARCHAR PRIMARY KEY,
            facility_name VARCHAR,
            facility_type VARCHAR,
            address VARCHAR,
            city VARCHAR,
            zip_code VARCHAR,
            county_fips VARCHAR,
            unit_count INTEGER,
            year_built INTEGER,
            latitude DOUBLE,
            longitude DOUBLE
        )
    """)
    
    # Population projections - Texas Demographic Center
    conn.execute("""
        CREATE TABLE IF NOT EXISTS population_projections (
            county_fips VARCHAR,
            year INTEGER,
            age_group VARCHAR,
            projected_population INTEGER,
            PRIMARY KEY (county_fips, year, age_group)
        )
    """)
    
    # Calculated metrics by ZIP code
    conn.execute("""
        CREATE TABLE IF NOT EXISTS zip_metrics (
            zip_code VARCHAR PRIMARY KEY,
            penetration_rate DOUBLE,
            demand_score DOUBLE,
            supply_score DOUBLE,
            healthcare_proximity_score DOUBLE,
            competitor_density DOUBLE,
            growth_rate_5yr DOUBLE,
            composite_score DOUBLE,
            last_calculated TIMESTAMP
        )
    """)
    
    conn.close()
    print("Database initialized successfully.")

def clear_table(table_name: str):
    """Clear all data from a specific table."""
    conn = get_connection()
    conn.execute(f"DELETE FROM {table_name}")
    conn.close()

def get_table_counts():
    """Get row counts for all tables."""
    conn = get_connection()
    tables = ['demographics', 'healthcare_facilities', 'senior_housing', 
              'population_projections', 'zip_metrics']
    counts = {}
    for table in tables:
        result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        counts[table] = result[0]
    conn.close()
    return counts

def execute_query(query: str):
    """Execute a SQL query and return results as a list of dictionaries."""
    conn = get_connection()
    try:
        result = conn.execute(query).fetchdf()
        return result
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_schema_description():
    """Return a description of the database schema for LLM context."""
    return """
DATABASE SCHEMA:

TABLE: demographics
- zip_code (VARCHAR, PRIMARY KEY): 5-digit ZIP code
- county_fips (VARCHAR): County FIPS code (e.g., '48201' for Harris County)
- county_name (VARCHAR): Full county name
- metro_area (VARCHAR): Metro area name (Houston, DFW, San Antonio)
- total_population (INTEGER): Total population in ZIP code
- pop_65_plus (INTEGER): Population aged 65 and older
- pop_75_plus (INTEGER): Population aged 75 and older
- pop_85_plus (INTEGER): Population aged 85 and older
- median_household_income (DOUBLE): Median household income in dollars
- median_income_65_plus (DOUBLE): Median income for 65+ householders
- households_total (INTEGER): Total number of households
- households_65_plus (INTEGER): Households with householder 65+
- income_qualified_il (INTEGER): Households qualifying for Independent Living (income > $48,000)
- income_qualified_al (INTEGER): Households qualifying for Assisted Living (income > $60,000)
- pct_65_plus (DOUBLE): Percentage of population 65+
- pct_75_plus (DOUBLE): Percentage of population 75+
- latitude (DOUBLE): ZIP code centroid latitude
- longitude (DOUBLE): ZIP code centroid longitude

TABLE: healthcare_facilities
- facility_id (VARCHAR, PRIMARY KEY): Unique facility identifier
- facility_name (VARCHAR): Name of the facility
- facility_type (VARCHAR): Type (Hospital, Nursing Home, etc.)
- address, city, state, zip_code: Location details
- county_fips (VARCHAR): County FIPS code
- beds (INTEGER): Number of beds
- overall_rating (INTEGER): CMS quality rating 1-5
- latitude, longitude (DOUBLE): Coordinates

TABLE: senior_housing
- facility_id (VARCHAR, PRIMARY KEY): Unique facility identifier
- facility_name (VARCHAR): Name of the senior housing community
- facility_type (VARCHAR): Type (Independent Living, Assisted Living, Memory Care, CCRC)
- address, city, zip_code: Location details
- county_fips (VARCHAR): County FIPS code
- unit_count (INTEGER): Number of units
- year_built (INTEGER): Year facility was built
- latitude, longitude (DOUBLE): Coordinates

TABLE: zip_metrics
- zip_code (VARCHAR, PRIMARY KEY): ZIP code
- penetration_rate (DOUBLE): Senior housing units / 75+ households
- demand_score (DOUBLE): 0-100 demand indicator
- supply_score (DOUBLE): 0-100 supply indicator
- healthcare_proximity_score (DOUBLE): 0-100 based on nearby healthcare
- competitor_density (DOUBLE): Competitors per square mile
- growth_rate_5yr (DOUBLE): Projected 5-year population growth rate
- composite_score (DOUBLE): Overall site score 0-100

COUNTY FIPS CODES:
- 48201: Harris County (Houston)
- 48157: Fort Bend County (Houston)
- 48339: Montgomery County (Houston)
- 48113: Dallas County (DFW)
- 48439: Tarrant County (DFW)
- 48085: Collin County (DFW)
- 48121: Denton County (DFW)

COMMON QUERY PATTERNS:
- Filter by metro: WHERE metro_area = 'Houston' or WHERE metro_area = 'DFW'
- Filter by county: WHERE county_name = 'Collin County' or WHERE county_fips = '48085'
- Senior population: Use pop_75_plus for most senior housing analysis
- Income filtering: Use income_qualified_il or income_qualified_al columns
"""

if __name__ == "__main__":
    initialize_database()
    print("Database setup complete!")
