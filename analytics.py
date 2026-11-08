"""
SeniorSite AI - Analytics Module
Calculates industry-standard metrics for senior housing site selection
"""

import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from database import get_connection, execute_query
from config import METRICS_CONFIG, DEFAULT_SCORING_WEIGHTS


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth.
    Returns distance in miles.
    """
    R = 3959  # Earth's radius in miles
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def calculate_penetration_rate(zip_code: str) -> dict:
    """
    Calculate senior housing penetration rate for a ZIP code.
    Penetration Rate = Total Senior Housing Units / 75+ Households
    """
    conn = get_connection()
    
    # Get demographic data
    demo = conn.execute("""
        SELECT households_65_plus, pop_75_plus, latitude, longitude
        FROM demographics WHERE zip_code = ?
    """, [zip_code]).fetchone()
    
    if not demo:
        conn.close()
        return {"error": "ZIP code not found"}
    
    households_65_plus, pop_75_plus, lat, lon = demo
    
    # Estimate 75+ households (roughly 40% of 65+ households)
    households_75_plus = int(households_65_plus * 0.4)
    
    # Count senior housing units within 5-mile radius
    inventory = conn.execute("""
        SELECT SUM(unit_count) as total_units
        FROM senior_housing
        WHERE latitude IS NOT NULL
    """).fetchone()[0] or 0
    
    # For more accurate calculation, filter by distance
    senior_housing = conn.execute("""
        SELECT unit_count, latitude, longitude
        FROM senior_housing
        WHERE latitude IS NOT NULL
    """).fetchall()
    
    conn.close()
    
    nearby_units = 0
    for units, slat, slon in senior_housing:
        if haversine_distance(lat, lon, slat, slon) <= 5:
            nearby_units += units
    
    # Calculate penetration rate
    if households_75_plus > 0:
        penetration_rate = nearby_units / households_75_plus
    else:
        penetration_rate = 0
    
    # Interpret the rate
    if penetration_rate < METRICS_CONFIG['penetration_benchmarks']['undersupplied']:
        market_status = "Undersupplied"
    elif penetration_rate < METRICS_CONFIG['penetration_benchmarks']['saturated']:
        market_status = "Balanced"
    else:
        market_status = "Saturated"
    
    return {
        "zip_code": zip_code,
        "households_75_plus": households_75_plus,
        "nearby_senior_housing_units": nearby_units,
        "penetration_rate": round(penetration_rate * 100, 2),
        "market_status": market_status
    }


def calculate_healthcare_proximity(lat: float, lon: float, max_miles: float = 10) -> dict:
    """
    Calculate healthcare proximity metrics for a location.
    Returns count and details of healthcare facilities within specified radius.
    """
    conn = get_connection()
    
    facilities = conn.execute("""
        SELECT facility_id, facility_name, facility_type, beds, overall_rating,
               latitude, longitude
        FROM healthcare_facilities
        WHERE latitude IS NOT NULL
    """).fetchall()
    
    conn.close()
    
    nearby = []
    hospitals_within_10mi = 0
    total_beds_nearby = 0
    
    for fac in facilities:
        fac_id, name, ftype, beds, rating, flat, flon = fac
        distance = haversine_distance(lat, lon, flat, flon)
        
        if distance <= max_miles:
            nearby.append({
                "facility_name": name,
                "facility_type": ftype,
                "beds": beds,
                "rating": rating,
                "distance_miles": round(distance, 2)
            })
            
            if ftype == "Hospital":
                hospitals_within_10mi += 1
            
            total_beds_nearby += (beds or 0)
    
    # Calculate proximity score (0-100)
    # Higher score = better healthcare access
    score = min(100, (hospitals_within_10mi * 20) + (total_beds_nearby / 50))
    
    return {
        "facilities_within_radius": len(nearby),
        "hospitals_within_10mi": hospitals_within_10mi,
        "total_beds_nearby": total_beds_nearby,
        "healthcare_proximity_score": round(score, 1),
        "nearby_facilities": sorted(nearby, key=lambda x: x['distance_miles'])[:10]
    }


def calculate_competitor_density(lat: float, lon: float, radius_miles: float = 5) -> dict:
    """
    Calculate competitor density for a location.
    Returns count and details of senior housing within specified radius.
    """
    conn = get_connection()
    
    competitors = conn.execute("""
        SELECT facility_id, facility_name, facility_type, unit_count, year_built,
               latitude, longitude
        FROM senior_housing
        WHERE latitude IS NOT NULL
    """).fetchall()
    
    conn.close()
    
    nearby = []
    total_units = 0
    
    for comp in competitors:
        comp_id, name, ctype, units, year_built, clat, clon = comp
        distance = haversine_distance(lat, lon, clat, clon)
        
        if distance <= radius_miles:
            nearby.append({
                "facility_name": name,
                "facility_type": ctype,
                "unit_count": units,
                "year_built": year_built,
                "distance_miles": round(distance, 2)
            })
            total_units += (units or 0)
    
    # Calculate density score (inverse - lower density = higher opportunity score)
    density_per_sqmi = len(nearby) / (3.14159 * radius_miles**2)
    opportunity_score = max(0, 100 - (density_per_sqmi * 50))
    
    return {
        "competitors_within_radius": len(nearby),
        "total_competitor_units": total_units,
        "density_per_sq_mile": round(density_per_sqmi, 3),
        "opportunity_score": round(opportunity_score, 1),
        "nearby_competitors": sorted(nearby, key=lambda x: x['distance_miles'])
    }


def calculate_demand_projection(county_fips: str, years_ahead: int = 5) -> dict:
    """
    Project senior housing demand based on population growth.
    Uses Texas Demographic Center projections where available.
    """
    conn = get_connection()
    
    # Get current demographics for the county
    current = conn.execute("""
        SELECT 
            SUM(pop_65_plus) as total_65_plus,
            SUM(pop_75_plus) as total_75_plus,
            SUM(pop_85_plus) as total_85_plus,
            SUM(households_65_plus) as total_hh_65_plus,
            SUM(income_qualified_il) as total_qualified_il,
            SUM(income_qualified_al) as total_qualified_al,
            county_name
        FROM demographics
        WHERE county_fips = ?
        GROUP BY county_fips
    """, [county_fips]).fetchone()
    
    conn.close()
    
    if not current:
        return {"error": "County not found"}
    
    total_65, total_75, total_85, total_hh, qual_il, qual_al, county_name = current
    
    # Apply growth rates (Texas Triangle averages 2-3% annual senior growth)
    growth_rate = 0.025  # 2.5% annual
    
    projected_65 = int(total_65 * (1 + growth_rate) ** years_ahead)
    projected_75 = int(total_75 * (1 + growth_rate) ** years_ahead)
    projected_85 = int(total_85 * (1 + growth_rate) ** years_ahead)
    
    # Estimate unit demand based on penetration assumptions
    # IL: ~3% of 75+ population
    # AL: ~5% of 80+ population (approximated from 75+ and 85+)
    # MC: ~2% of 85+ population
    
    current_il_demand = int(total_75 * 0.03)
    projected_il_demand = int(projected_75 * 0.03)
    
    pop_80_plus_current = int((total_75 + total_85) / 2)
    pop_80_plus_projected = int((projected_75 + projected_85) / 2)
    
    current_al_demand = int(pop_80_plus_current * 0.05)
    projected_al_demand = int(pop_80_plus_projected * 0.05)
    
    current_mc_demand = int(total_85 * 0.02)
    projected_mc_demand = int(projected_85 * 0.02)
    
    return {
        "county_name": county_name,
        "county_fips": county_fips,
        "projection_year": 2023 + years_ahead,
        "current_population": {
            "age_65_plus": total_65,
            "age_75_plus": total_75,
            "age_85_plus": total_85
        },
        "projected_population": {
            "age_65_plus": projected_65,
            "age_75_plus": projected_75,
            "age_85_plus": projected_85
        },
        "growth_rate_annual": f"{growth_rate * 100}%",
        "demand_estimates": {
            "independent_living": {
                "current_units": current_il_demand,
                "projected_units": projected_il_demand,
                "growth": projected_il_demand - current_il_demand
            },
            "assisted_living": {
                "current_units": current_al_demand,
                "projected_units": projected_al_demand,
                "growth": projected_al_demand - current_al_demand
            },
            "memory_care": {
                "current_units": current_mc_demand,
                "projected_units": projected_mc_demand,
                "growth": projected_mc_demand - current_mc_demand
            }
        },
        "income_qualified_households": {
            "independent_living": qual_il,
            "assisted_living": qual_al
        }
    }


def calculate_composite_score(zip_code: str, weights: dict = None) -> dict:
    """
    Calculate a composite site score for a ZIP code.
    Combines demographic, market, and accessibility factors.
    """
    if weights is None:
        weights = DEFAULT_SCORING_WEIGHTS
    
    conn = get_connection()
    
    # Get ZIP code data
    demo = conn.execute("""
        SELECT zip_code, county_fips, county_name, metro_area,
               total_population, pop_65_plus, pop_75_plus, pop_85_plus,
               median_household_income, median_income_65_plus,
               households_65_plus, income_qualified_il, income_qualified_al,
               pct_65_plus, pct_75_plus, latitude, longitude
        FROM demographics WHERE zip_code = ?
    """, [zip_code]).fetchone()
    
    conn.close()
    
    if not demo:
        return {"error": "ZIP code not found"}
    
    (zip_code, county_fips, county_name, metro_area, total_pop, 
     pop_65, pop_75, pop_85, median_income, income_65, hh_65, 
     qual_il, qual_al, pct_65, pct_75, lat, lon) = demo
    
    # Demographic Score (0-100)
    # Based on 75+ population, income qualification, and senior concentration
    pop_score = min(100, (pop_75 / 100) * 5)  # Higher population = higher score
    income_score = min(100, (qual_il / 100) * 10)  # More qualified households = higher
    concentration_score = min(100, pct_75 * 8)  # Higher % seniors = higher
    
    demographic_score = (pop_score * 0.4 + income_score * 0.4 + concentration_score * 0.2)
    
    # Market Score (0-100)
    # Based on penetration rate (lower = better opportunity)
    penetration = calculate_penetration_rate(zip_code)
    if "error" not in penetration:
        pen_rate = penetration['penetration_rate']
        if pen_rate < 8:
            market_score = 90  # Undersupplied - great opportunity
        elif pen_rate < 12:
            market_score = 70  # Balanced
        elif pen_rate < 15:
            market_score = 50  # Moderately saturated
        else:
            market_score = 30  # Saturated
    else:
        market_score = 50  # Default if can't calculate
    
    # Competitor analysis
    competitor_data = calculate_competitor_density(lat, lon)
    competitor_score = competitor_data['opportunity_score']
    
    market_score = (market_score * 0.6 + competitor_score * 0.4)
    
    # Accessibility Score (0-100)
    # Based on healthcare proximity
    healthcare_data = calculate_healthcare_proximity(lat, lon)
    accessibility_score = healthcare_data['healthcare_proximity_score']
    
    # Composite Score
    composite = (
        demographic_score * weights['demographic'] +
        market_score * weights['market'] +
        accessibility_score * weights['accessibility']
    )
    
    # Determine rating
    if composite >= 80:
        rating = "Excellent"
    elif composite >= 65:
        rating = "Good"
    elif composite >= 50:
        rating = "Moderate"
    else:
        rating = "Below Average"
    
    return {
        "zip_code": zip_code,
        "county_name": county_name,
        "metro_area": metro_area,
        "composite_score": round(composite, 1),
        "rating": rating,
        "component_scores": {
            "demographic_score": round(demographic_score, 1),
            "market_score": round(market_score, 1),
            "accessibility_score": round(accessibility_score, 1)
        },
        "weights_used": weights,
        "key_metrics": {
            "population_75_plus": pop_75,
            "median_income_65_plus": income_65,
            "income_qualified_households": qual_il,
            "penetration_rate": penetration.get('penetration_rate', 'N/A'),
            "hospitals_within_10mi": healthcare_data['hospitals_within_10mi'],
            "competitors_within_5mi": competitor_data['competitors_within_radius']
        }
    }


def get_top_zip_codes(metro_area: str = None, county_name: str = None, 
                      limit: int = 10, min_pop_75: int = 1000) -> list:
    """
    Get top-scoring ZIP codes for senior housing development.
    Can filter by metro area or county.
    """
    conn = get_connection()
    
    query = """
        SELECT zip_code, county_name, metro_area, pop_75_plus, 
               median_income_65_plus, income_qualified_il, latitude, longitude
        FROM demographics
        WHERE pop_75_plus >= ?
    """
    params = [min_pop_75]
    
    if metro_area:
        query += " AND metro_area = ?"
        params.append(metro_area)
    
    if county_name:
        query += " AND county_name = ?"
        params.append(county_name)
    
    results = conn.execute(query, params).fetchall()
    conn.close()
    
    # Calculate scores for each ZIP
    scored_zips = []
    for row in results:
        zip_code, county, metro, pop_75, income_65, qual_il, lat, lon = row
        score_data = calculate_composite_score(zip_code)
        if "error" not in score_data:
            scored_zips.append({
                "zip_code": zip_code,
                "county_name": county,
                "metro_area": metro,
                "composite_score": score_data['composite_score'],
                "rating": score_data['rating'],
                "population_75_plus": pop_75,
                "median_income_65_plus": income_65,
                "income_qualified_households": qual_il
            })
    
    # Sort by score descending
    scored_zips.sort(key=lambda x: x['composite_score'], reverse=True)
    
    return scored_zips[:limit]


def compare_sites(zip_codes: list) -> pd.DataFrame:
    """
    Compare multiple ZIP codes side by side.
    """
    comparison_data = []
    
    for zip_code in zip_codes:
        score_data = calculate_composite_score(zip_code)
        if "error" not in score_data:
            comparison_data.append({
                "ZIP Code": zip_code,
                "County": score_data['county_name'],
                "Composite Score": score_data['composite_score'],
                "Rating": score_data['rating'],
                "Demographic Score": score_data['component_scores']['demographic_score'],
                "Market Score": score_data['component_scores']['market_score'],
                "Accessibility Score": score_data['component_scores']['accessibility_score'],
                "75+ Population": score_data['key_metrics']['population_75_plus'],
                "Qualified Households": score_data['key_metrics']['income_qualified_households'],
                "Penetration Rate": score_data['key_metrics']['penetration_rate']
            })
    
    return pd.DataFrame(comparison_data)


if __name__ == "__main__":
    # Test analytics functions
    print("Testing analytics module...\n")
    
    # Test penetration rate
    print("Penetration Rate for 77024:")
    print(calculate_penetration_rate("77024"))
    print()
    
    # Test healthcare proximity
    print("Healthcare Proximity for central Houston (29.76, -95.37):")
    print(calculate_healthcare_proximity(29.76, -95.37))
    print()
    
    # Test demand projection
    print("Demand Projection for Harris County:")
    print(calculate_demand_projection("48201"))
    print()
    
    # Test composite score
    print("Composite Score for 75024 (Plano):")
    print(calculate_composite_score("75024"))
