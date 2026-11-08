"""
SeniorSite AI - Data Loader Module
Loads sample data for demo and provides real API integration for production
"""

import pandas as pd
from database import get_connection, initialize_database
from config import TEXAS_TRIANGLE_COUNTIES

def load_sample_demographics():
    """
    Load realistic sample demographic data for Texas Triangle ZIP codes.
    This data mirrors Census ACS patterns for demonstration purposes.
    """
    
    # Sample data representing real Texas Triangle ZIP codes
    # Values are realistic approximations based on actual Census patterns
    sample_data = [
        # HARRIS COUNTY (Houston) - 48201
        {"zip_code": "77001", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 15234, "pop_65_plus": 1829, "pop_75_plus": 762, "pop_85_plus": 198,
         "median_household_income": 52340, "median_income_65_plus": 48200, "households_total": 5890,
         "households_65_plus": 1245, "latitude": 29.7604, "longitude": -95.3698},
        {"zip_code": "77002", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 18456, "pop_65_plus": 2214, "pop_75_plus": 885, "pop_85_plus": 221,
         "median_household_income": 67800, "median_income_65_plus": 58900, "households_total": 7234,
         "households_65_plus": 1567, "latitude": 29.7545, "longitude": -95.3622},
        {"zip_code": "77024", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 42567, "pop_65_plus": 7650, "pop_75_plus": 3442, "pop_85_plus": 860,
         "median_household_income": 142500, "median_income_65_plus": 125000, "households_total": 15234,
         "households_65_plus": 4123, "latitude": 29.7732, "longitude": -95.5249},
        {"zip_code": "77056", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 28934, "pop_65_plus": 4340, "pop_75_plus": 1953, "pop_85_plus": 488,
         "median_household_income": 89500, "median_income_65_plus": 76200, "households_total": 11567,
         "households_65_plus": 2890, "latitude": 29.7420, "longitude": -95.4670},
        {"zip_code": "77079", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 35678, "pop_65_plus": 5708, "pop_75_plus": 2568, "pop_85_plus": 642,
         "median_household_income": 115000, "median_income_65_plus": 98000, "households_total": 13456,
         "households_65_plus": 3234, "latitude": 29.7772, "longitude": -95.5910},
        {"zip_code": "77005", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 21345, "pop_65_plus": 3842, "pop_75_plus": 1729, "pop_85_plus": 432,
         "median_household_income": 156000, "median_income_65_plus": 132000, "households_total": 8234,
         "households_65_plus": 2145, "latitude": 29.7174, "longitude": -95.4219},
        {"zip_code": "77007", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 31245, "pop_65_plus": 3437, "pop_75_plus": 1375, "pop_85_plus": 344,
         "median_household_income": 95600, "median_income_65_plus": 82000, "households_total": 14567,
         "households_65_plus": 2678, "latitude": 29.7727, "longitude": -95.4080},
        {"zip_code": "77019", "county_fips": "48201", "county_name": "Harris County", "metro_area": "Houston",
         "total_population": 25678, "pop_65_plus": 4366, "pop_75_plus": 1965, "pop_85_plus": 491,
         "median_household_income": 128000, "median_income_65_plus": 108000, "households_total": 10234,
         "households_65_plus": 2567, "latitude": 29.7605, "longitude": -95.4039},
        
        # FORT BEND COUNTY (Houston suburbs) - 48157
        {"zip_code": "77459", "county_fips": "48157", "county_name": "Fort Bend County", "metro_area": "Houston",
         "total_population": 67234, "pop_65_plus": 8740, "pop_75_plus": 3496, "pop_85_plus": 699,
         "median_household_income": 125000, "median_income_65_plus": 95000, "households_total": 22456,
         "households_65_plus": 4567, "latitude": 29.5535, "longitude": -95.5774},
        {"zip_code": "77479", "county_fips": "48157", "county_name": "Fort Bend County", "metro_area": "Houston",
         "total_population": 89567, "pop_65_plus": 12538, "pop_75_plus": 5015, "pop_85_plus": 1003,
         "median_household_income": 142000, "median_income_65_plus": 112000, "households_total": 28934,
         "households_65_plus": 5890, "latitude": 29.5622, "longitude": -95.6343},
        {"zip_code": "77406", "county_fips": "48157", "county_name": "Fort Bend County", "metro_area": "Houston",
         "total_population": 54321, "pop_65_plus": 6519, "pop_75_plus": 2608, "pop_85_plus": 522,
         "median_household_income": 98000, "median_income_65_plus": 78000, "households_total": 18234,
         "households_65_plus": 3456, "latitude": 29.6010, "longitude": -95.7595},
        
        # MONTGOMERY COUNTY (The Woodlands) - 48339
        {"zip_code": "77380", "county_fips": "48339", "county_name": "Montgomery County", "metro_area": "Houston",
         "total_population": 45678, "pop_65_plus": 7765, "pop_75_plus": 3494, "pop_85_plus": 874,
         "median_household_income": 135000, "median_income_65_plus": 105000, "households_total": 16789,
         "households_65_plus": 4123, "latitude": 30.1658, "longitude": -95.4613},
        {"zip_code": "77381", "county_fips": "48339", "county_name": "Montgomery County", "metro_area": "Houston",
         "total_population": 38945, "pop_65_plus": 6231, "pop_75_plus": 2804, "pop_85_plus": 701,
         "median_household_income": 148000, "median_income_65_plus": 118000, "households_total": 14234,
         "households_65_plus": 3567, "latitude": 30.1838, "longitude": -95.4902},
        {"zip_code": "77382", "county_fips": "48339", "county_name": "Montgomery County", "metro_area": "Houston",
         "total_population": 52134, "pop_65_plus": 8341, "pop_75_plus": 3754, "pop_85_plus": 939,
         "median_household_income": 162000, "median_income_65_plus": 128000, "households_total": 18567,
         "households_65_plus": 4234, "latitude": 30.2010, "longitude": -95.5150},
        
        # DALLAS COUNTY - 48113
        {"zip_code": "75201", "county_fips": "48113", "county_name": "Dallas County", "metro_area": "DFW",
         "total_population": 19876, "pop_65_plus": 2186, "pop_75_plus": 875, "pop_85_plus": 219,
         "median_household_income": 78500, "median_income_65_plus": 65000, "households_total": 9234,
         "households_65_plus": 1456, "latitude": 32.7872, "longitude": -96.7985},
        {"zip_code": "75205", "county_fips": "48113", "county_name": "Dallas County", "metro_area": "DFW",
         "total_population": 28456, "pop_65_plus": 4552, "pop_75_plus": 2048, "pop_85_plus": 512,
         "median_household_income": 185000, "median_income_65_plus": 156000, "households_total": 11234,
         "households_65_plus": 2890, "latitude": 32.8318, "longitude": -96.7940},
        {"zip_code": "75209", "county_fips": "48113", "county_name": "Dallas County", "metro_area": "DFW",
         "total_population": 15678, "pop_65_plus": 2351, "pop_75_plus": 1058, "pop_85_plus": 265,
         "median_household_income": 92000, "median_income_65_plus": 78000, "households_total": 6789,
         "households_65_plus": 1567, "latitude": 32.8415, "longitude": -96.8210},
        {"zip_code": "75225", "county_fips": "48113", "county_name": "Dallas County", "metro_area": "DFW",
         "total_population": 32456, "pop_65_plus": 5517, "pop_75_plus": 2483, "pop_85_plus": 621,
         "median_household_income": 168000, "median_income_65_plus": 142000, "households_total": 12567,
         "households_65_plus": 3234, "latitude": 32.8668, "longitude": -96.7898},
        {"zip_code": "75230", "county_fips": "48113", "county_name": "Dallas County", "metro_area": "DFW",
         "total_population": 27890, "pop_65_plus": 4741, "pop_75_plus": 2134, "pop_85_plus": 534,
         "median_household_income": 145000, "median_income_65_plus": 125000, "households_total": 10567,
         "households_65_plus": 2678, "latitude": 32.8890, "longitude": -96.7695},
        
        # COLLIN COUNTY (Plano, Frisco, McKinney) - 48085
        {"zip_code": "75024", "county_fips": "48085", "county_name": "Collin County", "metro_area": "DFW",
         "total_population": 78234, "pop_65_plus": 10949, "pop_75_plus": 4380, "pop_85_plus": 876,
         "median_household_income": 138000, "median_income_65_plus": 108000, "households_total": 28456,
         "households_65_plus": 5678, "latitude": 33.0742, "longitude": -96.8050},
        {"zip_code": "75025", "county_fips": "48085", "county_name": "Collin County", "metro_area": "DFW",
         "total_population": 65432, "pop_65_plus": 8506, "pop_75_plus": 3402, "pop_85_plus": 680,
         "median_household_income": 125000, "median_income_65_plus": 98000, "households_total": 24567,
         "households_65_plus": 4567, "latitude": 33.0523, "longitude": -96.7507},
        {"zip_code": "75034", "county_fips": "48085", "county_name": "Collin County", "metro_area": "DFW",
         "total_population": 54678, "pop_65_plus": 6014, "pop_75_plus": 2406, "pop_85_plus": 481,
         "median_household_income": 152000, "median_income_65_plus": 118000, "households_total": 19234,
         "households_65_plus": 3456, "latitude": 33.1507, "longitude": -96.8236},
        {"zip_code": "75035", "county_fips": "48085", "county_name": "Collin County", "metro_area": "DFW",
         "total_population": 48765, "pop_65_plus": 5364, "pop_75_plus": 2146, "pop_85_plus": 429,
         "median_household_income": 142000, "median_income_65_plus": 112000, "households_total": 17234,
         "households_65_plus": 3012, "latitude": 33.1684, "longitude": -96.8022},
        {"zip_code": "75070", "county_fips": "48085", "county_name": "Collin County", "metro_area": "DFW",
         "total_population": 72345, "pop_65_plus": 9405, "pop_75_plus": 3762, "pop_85_plus": 752,
         "median_household_income": 128000, "median_income_65_plus": 102000, "households_total": 26234,
         "households_65_plus": 4890, "latitude": 33.1972, "longitude": -96.6397},
        {"zip_code": "75071", "county_fips": "48085", "county_name": "Collin County", "metro_area": "DFW",
         "total_population": 58976, "pop_65_plus": 7076, "pop_75_plus": 2830, "pop_85_plus": 566,
         "median_household_income": 118000, "median_income_65_plus": 95000, "households_total": 21567,
         "households_65_plus": 3890, "latitude": 33.2148, "longitude": -96.6150},
        {"zip_code": "75093", "county_fips": "48085", "county_name": "Collin County", "metro_area": "DFW",
         "total_population": 45678, "pop_65_plus": 7765, "pop_75_plus": 3494, "pop_85_plus": 874,
         "median_household_income": 175000, "median_income_65_plus": 145000, "households_total": 16234,
         "households_65_plus": 4123, "latitude": 33.0362, "longitude": -96.8028},
        
        # TARRANT COUNTY (Fort Worth) - 48439
        {"zip_code": "76107", "county_fips": "48439", "county_name": "Tarrant County", "metro_area": "DFW",
         "total_population": 24567, "pop_65_plus": 3440, "pop_75_plus": 1376, "pop_85_plus": 344,
         "median_household_income": 85000, "median_income_65_plus": 72000, "households_total": 10234,
         "households_65_plus": 2234, "latitude": 32.7381, "longitude": -97.3620},
        {"zip_code": "76109", "county_fips": "48439", "county_name": "Tarrant County", "metro_area": "DFW",
         "total_population": 31234, "pop_65_plus": 4997, "pop_75_plus": 2249, "pop_85_plus": 562,
         "median_household_income": 112000, "median_income_65_plus": 95000, "households_total": 12456,
         "households_65_plus": 2890, "latitude": 32.7068, "longitude": -97.3827},
        {"zip_code": "76116", "county_fips": "48439", "county_name": "Tarrant County", "metro_area": "DFW",
         "total_population": 42567, "pop_65_plus": 5962, "pop_75_plus": 2683, "pop_85_plus": 671,
         "median_household_income": 78000, "median_income_65_plus": 65000, "households_total": 15678,
         "households_65_plus": 3456, "latitude": 32.7251, "longitude": -97.4311},
        {"zip_code": "76132", "county_fips": "48439", "county_name": "Tarrant County", "metro_area": "DFW",
         "total_population": 38976, "pop_65_plus": 6236, "pop_75_plus": 2806, "pop_85_plus": 702,
         "median_household_income": 95000, "median_income_65_plus": 82000, "households_total": 14234,
         "households_65_plus": 3123, "latitude": 32.6799, "longitude": -97.3917},
        {"zip_code": "76034", "county_fips": "48439", "county_name": "Tarrant County", "metro_area": "DFW",
         "total_population": 28456, "pop_65_plus": 4268, "pop_75_plus": 1921, "pop_85_plus": 480,
         "median_household_income": 135000, "median_income_65_plus": 115000, "households_total": 10567,
         "households_65_plus": 2567, "latitude": 32.8612, "longitude": -97.1475},
        
        # DENTON COUNTY - 48121
        {"zip_code": "75077", "county_fips": "48121", "county_name": "Denton County", "metro_area": "DFW",
         "total_population": 45678, "pop_65_plus": 5481, "pop_75_plus": 2193, "pop_85_plus": 439,
         "median_household_income": 128000, "median_income_65_plus": 102000, "households_total": 16789,
         "households_65_plus": 3234, "latitude": 33.0462, "longitude": -97.0789},
        {"zip_code": "75056", "county_fips": "48121", "county_name": "Denton County", "metro_area": "DFW",
         "total_population": 52345, "pop_65_plus": 6805, "pop_75_plus": 2722, "pop_85_plus": 544,
         "median_household_income": 145000, "median_income_65_plus": 118000, "households_total": 18567,
         "households_65_plus": 3890, "latitude": 33.0773, "longitude": -97.0012},
        {"zip_code": "75028", "county_fips": "48121", "county_name": "Denton County", "metro_area": "DFW",
         "total_population": 68234, "pop_65_plus": 8188, "pop_75_plus": 3275, "pop_85_plus": 655,
         "median_household_income": 115000, "median_income_65_plus": 92000, "households_total": 25456,
         "households_65_plus": 4567, "latitude": 33.0137, "longitude": -97.1289},
        {"zip_code": "76210", "county_fips": "48121", "county_name": "Denton County", "metro_area": "DFW",
         "total_population": 35678, "pop_65_plus": 4281, "pop_75_plus": 1712, "pop_85_plus": 342,
         "median_household_income": 98000, "median_income_65_plus": 78000, "households_total": 13456,
         "households_65_plus": 2567, "latitude": 33.2148, "longitude": -97.1330},
    ]
    
    # Calculate derived fields
    for row in sample_data:
        row['pct_65_plus'] = round(row['pop_65_plus'] / row['total_population'] * 100, 2)
        row['pct_75_plus'] = round(row['pop_75_plus'] / row['total_population'] * 100, 2)
        row['owner_occupied_65_plus'] = int(row['households_65_plus'] * 0.75)  # Approximate
        row['renter_occupied_65_plus'] = row['households_65_plus'] - row['owner_occupied_65_plus']
        # Income qualified calculations
        if row['median_income_65_plus'] >= 48000:
            row['income_qualified_il'] = int(row['households_65_plus'] * 0.65)
        else:
            row['income_qualified_il'] = int(row['households_65_plus'] * 0.35)
        if row['median_income_65_plus'] >= 60000:
            row['income_qualified_al'] = int(row['households_65_plus'] * 0.55)
        else:
            row['income_qualified_al'] = int(row['households_65_plus'] * 0.25)
        row['data_year'] = 2023
    
    return pd.DataFrame(sample_data)


def load_sample_healthcare_facilities():
    """Load sample healthcare facility data for Texas Triangle."""
    
    facilities = [
        # Houston Hospitals
        {"facility_id": "HOU001", "facility_name": "Houston Methodist Hospital", "facility_type": "Hospital",
         "address": "6565 Fannin St", "city": "Houston", "state": "TX", "zip_code": "77030",
         "county_fips": "48201", "phone": "713-790-3311", "beds": 1005, "overall_rating": 5,
         "latitude": 29.7077, "longitude": -95.3963},
        {"facility_id": "HOU002", "facility_name": "Memorial Hermann TMC", "facility_type": "Hospital",
         "address": "6411 Fannin St", "city": "Houston", "state": "TX", "zip_code": "77030",
         "county_fips": "48201", "phone": "713-704-4000", "beds": 891, "overall_rating": 5,
         "latitude": 29.7099, "longitude": -95.3975},
        {"facility_id": "HOU003", "facility_name": "St. Luke's Hospital", "facility_type": "Hospital",
         "address": "6720 Bertner Ave", "city": "Houston", "state": "TX", "zip_code": "77030",
         "county_fips": "48201", "phone": "832-355-1000", "beds": 650, "overall_rating": 4,
         "latitude": 29.7071, "longitude": -95.4001},
        {"facility_id": "HOU004", "facility_name": "Houston Methodist Willowbrook", "facility_type": "Hospital",
         "address": "18220 Tomball Pkwy", "city": "Houston", "state": "TX", "zip_code": "77070",
         "county_fips": "48201", "phone": "281-477-1000", "beds": 312, "overall_rating": 4,
         "latitude": 29.9543, "longitude": -95.5396},
        {"facility_id": "HOU005", "facility_name": "Memorial Hermann The Woodlands", "facility_type": "Hospital",
         "address": "9250 Pinecroft Dr", "city": "The Woodlands", "state": "TX", "zip_code": "77380",
         "county_fips": "48339", "phone": "713-897-2300", "beds": 397, "overall_rating": 5,
         "latitude": 30.1578, "longitude": -95.4601},
        {"facility_id": "HOU006", "facility_name": "Houston Methodist Sugar Land", "facility_type": "Hospital",
         "address": "16655 Southwest Fwy", "city": "Sugar Land", "state": "TX", "zip_code": "77479",
         "county_fips": "48157", "phone": "281-274-7000", "beds": 348, "overall_rating": 4,
         "latitude": 29.5807, "longitude": -95.6247},
        
        # Dallas Hospitals
        {"facility_id": "DAL001", "facility_name": "UT Southwestern Medical Center", "facility_type": "Hospital",
         "address": "5323 Harry Hines Blvd", "city": "Dallas", "state": "TX", "zip_code": "75390",
         "county_fips": "48113", "phone": "214-648-3111", "beds": 740, "overall_rating": 5,
         "latitude": 32.8121, "longitude": -96.8406},
        {"facility_id": "DAL002", "facility_name": "Baylor University Medical Center", "facility_type": "Hospital",
         "address": "3500 Gaston Ave", "city": "Dallas", "state": "TX", "zip_code": "75246",
         "county_fips": "48113", "phone": "214-820-0111", "beds": 914, "overall_rating": 5,
         "latitude": 32.7879, "longitude": -96.7710},
        {"facility_id": "DAL003", "facility_name": "Texas Health Presbyterian Dallas", "facility_type": "Hospital",
         "address": "8200 Walnut Hill Ln", "city": "Dallas", "state": "TX", "zip_code": "75231",
         "county_fips": "48113", "phone": "214-345-6789", "beds": 875, "overall_rating": 4,
         "latitude": 32.8687, "longitude": -96.7683},
        {"facility_id": "DAL004", "facility_name": "Medical City Plano", "facility_type": "Hospital",
         "address": "3901 W 15th St", "city": "Plano", "state": "TX", "zip_code": "75075",
         "county_fips": "48085", "phone": "972-596-6800", "beds": 493, "overall_rating": 4,
         "latitude": 33.0224, "longitude": -96.7495},
        {"facility_id": "DAL005", "facility_name": "Texas Health Presbyterian Plano", "facility_type": "Hospital",
         "address": "6200 W Parker Rd", "city": "Plano", "state": "TX", "zip_code": "75093",
         "county_fips": "48085", "phone": "972-981-8000", "beds": 366, "overall_rating": 5,
         "latitude": 33.0458, "longitude": -96.8161},
        {"facility_id": "DAL006", "facility_name": "Baylor Scott & White McKinney", "facility_type": "Hospital",
         "address": "5252 W University Dr", "city": "McKinney", "state": "TX", "zip_code": "75071",
         "county_fips": "48085", "phone": "469-764-1000", "beds": 143, "overall_rating": 4,
         "latitude": 33.1968, "longitude": -96.6651},
        
        # Fort Worth Hospitals
        {"facility_id": "FTW001", "facility_name": "Texas Health Harris Methodist", "facility_type": "Hospital",
         "address": "1301 Pennsylvania Ave", "city": "Fort Worth", "state": "TX", "zip_code": "76104",
         "county_fips": "48439", "phone": "817-250-2000", "beds": 725, "overall_rating": 4,
         "latitude": 32.7262, "longitude": -97.3298},
        {"facility_id": "FTW002", "facility_name": "JPS Health Network", "facility_type": "Hospital",
         "address": "1500 S Main St", "city": "Fort Worth", "state": "TX", "zip_code": "76104",
         "county_fips": "48439", "phone": "817-921-3431", "beds": 573, "overall_rating": 3,
         "latitude": 32.7196, "longitude": -97.3307},
        {"facility_id": "FTW003", "facility_name": "Medical City Fort Worth", "facility_type": "Hospital",
         "address": "900 Eighth Ave", "city": "Fort Worth", "state": "TX", "zip_code": "76104",
         "county_fips": "48439", "phone": "817-336-2100", "beds": 320, "overall_rating": 4,
         "latitude": 32.7298, "longitude": -97.3345},
        
        # Nursing Homes (sample)
        {"facility_id": "NH001", "facility_name": "Brookdale Galleria", "facility_type": "Nursing Home",
         "address": "2929 Post Oak Blvd", "city": "Houston", "state": "TX", "zip_code": "77056",
         "county_fips": "48201", "phone": "713-621-4500", "beds": 120, "overall_rating": 4,
         "latitude": 29.7386, "longitude": -95.4618},
        {"facility_id": "NH002", "facility_name": "The Tradition Prestonwood", "facility_type": "Nursing Home",
         "address": "5555 N Dallas Pkwy", "city": "Dallas", "state": "TX", "zip_code": "75240",
         "county_fips": "48113", "phone": "972-503-6700", "beds": 180, "overall_rating": 5,
         "latitude": 32.9231, "longitude": -96.8039},
        {"facility_id": "NH003", "facility_name": "Autumn Leaves of Plano", "facility_type": "Nursing Home",
         "address": "8221 Ohio Dr", "city": "Plano", "state": "TX", "zip_code": "75024",
         "county_fips": "48085", "phone": "972-378-2727", "beds": 65, "overall_rating": 5,
         "latitude": 33.0687, "longitude": -96.8077},
    ]
    
    return pd.DataFrame(facilities)


def load_sample_senior_housing():
    """Load sample senior housing inventory (competitors)."""
    
    inventory = [
        # Houston Senior Housing
        {"facility_id": "SH001", "facility_name": "Belmont Village West University", "facility_type": "Assisted Living",
         "address": "2929 W Holcombe Blvd", "city": "Houston", "zip_code": "77025",
         "county_fips": "48201", "unit_count": 175, "year_built": 2001, "latitude": 29.7089, "longitude": -95.4352},
        {"facility_id": "SH002", "facility_name": "The Buckingham Senior Living", "facility_type": "Independent Living",
         "address": "6301 W Alabama St", "city": "Houston", "zip_code": "77005",
         "county_fips": "48201", "unit_count": 250, "year_built": 1998, "latitude": 29.7308, "longitude": -95.4305},
        {"facility_id": "SH003", "facility_name": "Parkway Place", "facility_type": "CCRC",
         "address": "1321 Park Bayou Dr", "city": "Houston", "zip_code": "77077",
         "county_fips": "48201", "unit_count": 380, "year_built": 2005, "latitude": 29.7582, "longitude": -95.5649},
        {"facility_id": "SH004", "facility_name": "The Village of Meyerland", "facility_type": "Assisted Living",
         "address": "4141 N Braeswood Blvd", "city": "Houston", "zip_code": "77025",
         "county_fips": "48201", "unit_count": 145, "year_built": 2010, "latitude": 29.6909, "longitude": -95.4567},
        {"facility_id": "SH005", "facility_name": "Sunrise of The Woodlands", "facility_type": "Assisted Living",
         "address": "2323 Lake Robbins Dr", "city": "The Woodlands", "zip_code": "77380",
         "county_fips": "48339", "unit_count": 85, "year_built": 2008, "latitude": 30.1582, "longitude": -95.4587},
        {"facility_id": "SH006", "facility_name": "Brazos Towers at Bayou Manor", "facility_type": "Independent Living",
         "address": "4141 S Braeswood Blvd", "city": "Houston", "zip_code": "77025",
         "county_fips": "48201", "unit_count": 210, "year_built": 1985, "latitude": 29.6835, "longitude": -95.4567},
        
        # Dallas Senior Housing
        {"facility_id": "SH007", "facility_name": "CC Young Senior Living", "facility_type": "CCRC",
         "address": "4829 W Lawther Dr", "city": "Dallas", "zip_code": "75214",
         "county_fips": "48113", "unit_count": 450, "year_built": 1962, "latitude": 32.8245, "longitude": -96.7515},
        {"facility_id": "SH008", "facility_name": "The Tradition Prestonwood", "facility_type": "Independent Living",
         "address": "5555 N Dallas Pkwy", "city": "Dallas", "zip_code": "75240",
         "county_fips": "48113", "unit_count": 290, "year_built": 2015, "latitude": 32.9231, "longitude": -96.8039},
        {"facility_id": "SH009", "facility_name": "Atria Valley View", "facility_type": "Assisted Living",
         "address": "13500 N Dallas Pkwy", "city": "Dallas", "zip_code": "75240",
         "county_fips": "48113", "unit_count": 120, "year_built": 2003, "latitude": 32.9447, "longitude": -96.8203},
        {"facility_id": "SH010", "facility_name": "Sunrise of Plano", "facility_type": "Assisted Living",
         "address": "3105 N Central Expy", "city": "Plano", "zip_code": "75074",
         "county_fips": "48085", "unit_count": 95, "year_built": 2000, "latitude": 33.0185, "longitude": -96.7048},
        {"facility_id": "SH011", "facility_name": "Legacy Senior Communities", "facility_type": "Independent Living",
         "address": "5701 Virginia Pkwy", "city": "McKinney", "zip_code": "75071",
         "county_fips": "48085", "unit_count": 185, "year_built": 2018, "latitude": 33.1623, "longitude": -96.6532},
        {"facility_id": "SH012", "facility_name": "The Conservatory at Plano", "facility_type": "Assisted Living",
         "address": "8000 Coit Rd", "city": "Plano", "zip_code": "75025",
         "county_fips": "48085", "unit_count": 110, "year_built": 2012, "latitude": 33.0692, "longitude": -96.7698},
        
        # Fort Worth Senior Housing
        {"facility_id": "SH013", "facility_name": "Trinity Terrace", "facility_type": "CCRC",
         "address": "1600 Texas St", "city": "Fort Worth", "zip_code": "76102",
         "county_fips": "48439", "unit_count": 320, "year_built": 1975, "latitude": 32.7555, "longitude": -97.3308},
        {"facility_id": "SH014", "facility_name": "The Stayton at Museum Way", "facility_type": "Independent Living",
         "address": "3100 W Lancaster Ave", "city": "Fort Worth", "zip_code": "76107",
         "county_fips": "48439", "unit_count": 240, "year_built": 2008, "latitude": 32.7463, "longitude": -97.3658},
        {"facility_id": "SH015", "facility_name": "Autumn Leaves of Southlake", "facility_type": "Memory Care",
         "address": "251 State St", "city": "Southlake", "zip_code": "76092",
         "county_fips": "48439", "unit_count": 68, "year_built": 2017, "latitude": 32.9415, "longitude": -97.1498},
    ]
    
    return pd.DataFrame(inventory)


def load_all_sample_data():
    """Load all sample data into the database."""
    
    # Initialize database
    initialize_database()
    
    conn = get_connection()
    
    # Load demographics
    print("Loading demographic data...")
    demographics_df = load_sample_demographics()
    conn.execute("DELETE FROM demographics")
    conn.execute("INSERT INTO demographics SELECT * FROM demographics_df")
    print(f"  Loaded {len(demographics_df)} ZIP codes")
    
    # Load healthcare facilities
    print("Loading healthcare facilities...")
    healthcare_df = load_sample_healthcare_facilities()
    conn.execute("DELETE FROM healthcare_facilities")
    conn.execute("INSERT INTO healthcare_facilities SELECT * FROM healthcare_df")
    print(f"  Loaded {len(healthcare_df)} facilities")
    
    # Load senior housing inventory
    print("Loading senior housing inventory...")
    senior_housing_df = load_sample_senior_housing()
    conn.execute("DELETE FROM senior_housing")
    conn.execute("INSERT INTO senior_housing SELECT * FROM senior_housing_df")
    print(f"  Loaded {len(senior_housing_df)} senior housing communities")
    
    conn.close()
    print("\nAll sample data loaded successfully!")


if __name__ == "__main__":
    load_all_sample_data()
