"""
SeniorSite AI - Main Application
Streamlit-based dashboard for senior housing site selection
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from database import get_connection, initialize_database, get_table_counts
from data_loader import load_all_sample_data
from analytics import (
    calculate_composite_score, 
    calculate_penetration_rate,
    calculate_healthcare_proximity,
    calculate_competitor_density,
    calculate_demand_projection,
    get_top_zip_codes,
    compare_sites
)
from llm_interface import (
    execute_natural_language_query,
    check_ollama_connection,
    get_quick_stats,
    EXAMPLE_QUESTIONS
)

# Page configuration
st.set_page_config(
    page_title="SeniorSite AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .score-excellent { color: #22c55e; font-weight: bold; }
    .score-good { color: #3b82f6; font-weight: bold; }
    .score-moderate { color: #f59e0b; font-weight: bold; }
    .score-below { color: #ef4444; font-weight: bold; }
    .stChatMessage {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'ollama_status' not in st.session_state:
        st.session_state.ollama_status = None


def check_and_load_data():
    """Check if data is loaded, load if not."""
    counts = get_table_counts()
    if counts.get('demographics', 0) == 0:
        with st.spinner("Loading sample data for the first time..."):
            load_all_sample_data()
        st.session_state.data_loaded = True
        return True
    st.session_state.data_loaded = True
    return False


def render_sidebar():
    """Render the sidebar with navigation and status."""
    with st.sidebar:
        st.markdown("## 🏠 SeniorSite AI")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigate",
            ["💬 Chat Analysis", "📊 Market Explorer", "🗺️ Map View", "📈 Site Comparison"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # System Status
        st.markdown("### System Status")
        
        # Data status
        counts = get_table_counts()
        st.markdown(f"📍 **ZIP Codes:** {counts.get('demographics', 0)}")
        st.markdown(f"🏥 **Healthcare:** {counts.get('healthcare_facilities', 0)}")
        st.markdown(f"🏢 **Senior Housing:** {counts.get('senior_housing', 0)}")
        
        # Ollama status
        if st.session_state.ollama_status is None:
            st.session_state.ollama_status = check_ollama_connection()
        
        if st.session_state.ollama_status:
            st.success("🦙 AI Connected")
        else:
            st.warning("🦙 AI Offline - Start Ollama")
            st.markdown("Run: `ollama run llama3.1`")
        
        st.markdown("---")
        
        # Quick filters
        st.markdown("### Quick Filters")
        metro_filter = st.selectbox(
            "Metro Area",
            ["All", "Houston", "DFW"],
            key="metro_filter"
        )
        
        min_pop = st.slider(
            "Min 75+ Population",
            min_value=0,
            max_value=10000,
            value=1000,
            step=500,
            key="min_pop_filter"
        )
        
        return page, metro_filter, min_pop


def render_chat_page():
    """Render the main chat analysis page."""
    st.markdown('<p class="main-header">💬 Chat Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about senior housing markets in natural language</p>', unsafe_allow_html=True)
    
    # Check Ollama status
    if not st.session_state.ollama_status:
        st.warning("""
        ⚠️ **Ollama is not running.** To enable AI-powered queries:
        1. Open a terminal/command prompt
        2. Run: `ollama run llama3.1`
        3. Refresh this page
        
        You can still explore the Market Explorer and Map View pages.
        """)
        return
    
    # Example questions
    with st.expander("📝 Example Questions", expanded=False):
        cols = st.columns(2)
        for i, q in enumerate(EXAMPLE_QUESTIONS[:6]):
            with cols[i % 2]:
                if st.button(q, key=f"example_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.rerun()
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sql" in message:
                    with st.expander("View SQL Query"):
                        st.code(message["sql"], language="sql")
                if "data" in message:
                    with st.expander("View Data"):
                        st.dataframe(message["data"])
    
    # Chat input
    if prompt := st.chat_input("Ask about senior housing markets..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = execute_natural_language_query(prompt)
                
                response = result.get("response", "I couldn't process that question.")
                st.markdown(response)
                
                # Show SQL if generated
                if result.get("sql_query"):
                    with st.expander("View SQL Query"):
                        st.code(result["sql_query"], language="sql")
                
                # Show data if available
                if result.get("raw_results") is not None and len(result["raw_results"]) > 0:
                    with st.expander("View Data Table"):
                        st.dataframe(result["raw_results"])
                
                # Store in history
                message_data = {"role": "assistant", "content": response}
                if result.get("sql_query"):
                    message_data["sql"] = result["sql_query"]
                if result.get("raw_results") is not None:
                    message_data["data"] = result["raw_results"]
                
                st.session_state.messages.append(message_data)


def render_market_explorer():
    """Render the market explorer page with interactive data views."""
    st.markdown('<p class="main-header">📊 Market Explorer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Explore demographic and market data across the Texas Triangle</p>', unsafe_allow_html=True)
    
    # Get data
    conn = get_connection()
    
    # Filters from sidebar
    metro_filter = st.session_state.get('metro_filter', 'All')
    min_pop = st.session_state.get('min_pop_filter', 1000)
    
    # Build query
    query = f"""
        SELECT zip_code, county_name, metro_area, total_population,
               pop_65_plus, pop_75_plus, pop_85_plus,
               median_household_income, median_income_65_plus,
               households_65_plus, income_qualified_il, income_qualified_al,
               pct_65_plus, pct_75_plus, latitude, longitude
        FROM demographics
        WHERE pop_75_plus >= {min_pop}
    """
    if metro_filter != "All":
        query += f" AND metro_area = '{metro_filter}'"
    query += " ORDER BY pop_75_plus DESC"
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ZIP Codes", len(df))
    with col2:
        st.metric("Total 75+ Population", f"{df['pop_75_plus'].sum():,}")
    with col3:
        st.metric("Avg Senior Income", f"${df['median_income_65_plus'].mean():,.0f}")
    with col4:
        st.metric("Qualified Households (IL)", f"{df['income_qualified_il'].sum():,}")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Data Table", "📊 Charts", "🎯 Site Scoring"])
    
    with tab1:
        st.markdown("### Demographic Data by ZIP Code")
        
        # Column selection
        display_cols = st.multiselect(
            "Select columns to display",
            df.columns.tolist(),
            default=['zip_code', 'county_name', 'metro_area', 'pop_75_plus', 
                    'median_income_65_plus', 'income_qualified_il', 'pct_75_plus']
        )
        
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "seniorsite_demographics.csv",
            "text/csv"
        )
    
    with tab2:
        st.markdown("### Visualizations")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Population by county
            county_data = df.groupby('county_name')['pop_75_plus'].sum().reset_index()
            fig1 = px.bar(
                county_data, 
                x='county_name', 
                y='pop_75_plus',
                title="75+ Population by County",
                color='pop_75_plus',
                color_continuous_scale='Blues'
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        
        with chart_col2:
            # Income distribution
            fig2 = px.histogram(
                df, 
                x='median_income_65_plus',
                nbins=20,
                title="Senior Income Distribution",
                color_discrete_sequence=['#3b82f6']
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Scatter plot
        st.markdown("### Population vs Income Analysis")
        fig3 = px.scatter(
            df,
            x='pop_75_plus',
            y='median_income_65_plus',
            color='metro_area',
            size='income_qualified_il',
            hover_data=['zip_code', 'county_name'],
            title="75+ Population vs Senior Income (size = qualified households)"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab3:
        st.markdown("### Site Scoring Analysis")
        st.markdown("Select a ZIP code to calculate its composite site score.")
        
        selected_zip = st.selectbox(
            "Select ZIP Code",
            df['zip_code'].tolist(),
            format_func=lambda x: f"{x} - {df[df['zip_code']==x]['county_name'].values[0]}"
        )
        
        if st.button("Calculate Score", type="primary"):
            with st.spinner("Calculating..."):
                score_data = calculate_composite_score(selected_zip)
                
                if "error" not in score_data:
                    # Display score
                    score = score_data['composite_score']
                    rating = score_data['rating']
                    
                    # Color based on rating
                    if rating == "Excellent":
                        color = "score-excellent"
                    elif rating == "Good":
                        color = "score-good"
                    elif rating == "Moderate":
                        color = "score-moderate"
                    else:
                        color = "score-below"
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown(f"### Composite Score")
                        st.markdown(f'<h1 class="{color}">{score}/100</h1>', unsafe_allow_html=True)
                        st.markdown(f"**Rating:** {rating}")
                    
                    with col2:
                        # Component scores radar chart
                        components = score_data['component_scores']
                        fig = go.Figure(data=go.Scatterpolar(
                            r=[components['demographic_score'], 
                               components['market_score'], 
                               components['accessibility_score'],
                               components['demographic_score']],
                            theta=['Demographic', 'Market', 'Accessibility', 'Demographic'],
                            fill='toself',
                            fillcolor='rgba(59, 130, 246, 0.3)',
                            line_color='#3b82f6'
                        ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            showlegend=False,
                            title="Component Scores"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Key metrics
                    st.markdown("### Key Metrics")
                    metrics = score_data['key_metrics']
                    mcol1, mcol2, mcol3 = st.columns(3)
                    with mcol1:
                        st.metric("75+ Population", f"{metrics['population_75_plus']:,}")
                        st.metric("Qualified Households", f"{metrics['income_qualified_households']:,}")
                    with mcol2:
                        st.metric("Senior Income", f"${metrics['median_income_65_plus']:,}")
                        st.metric("Penetration Rate", f"{metrics['penetration_rate']}%")
                    with mcol3:
                        st.metric("Hospitals (10mi)", metrics['hospitals_within_10mi'])
                        st.metric("Competitors (5mi)", metrics['competitors_within_5mi'])
                else:
                    st.error(score_data.get("error", "Error calculating score"))


def render_map_view():
    """Render the interactive map page."""
    st.markdown('<p class="main-header">🗺️ Map View</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Geographic visualization of senior housing markets</p>', unsafe_allow_html=True)
    
    # Get data
    conn = get_connection()
    
    metro_filter = st.session_state.get('metro_filter', 'All')
    
    # Get demographics with coordinates
    query = """
        SELECT zip_code, county_name, metro_area, pop_75_plus,
               median_income_65_plus, income_qualified_il, latitude, longitude
        FROM demographics
        WHERE latitude IS NOT NULL
    """
    if metro_filter != "All":
        query += f" AND metro_area = '{metro_filter}'"
    
    demographics = pd.read_sql(query, conn)
    
    # Get healthcare facilities
    healthcare = pd.read_sql("""
        SELECT facility_name, facility_type, city, beds, latitude, longitude
        FROM healthcare_facilities
        WHERE latitude IS NOT NULL
    """, conn)
    
    # Get senior housing
    senior_housing = pd.read_sql("""
        SELECT facility_name, facility_type, city, unit_count, latitude, longitude
        FROM senior_housing
        WHERE latitude IS NOT NULL
    """, conn)
    
    conn.close()
    
    # Map layer selection
    st.markdown("### Map Layers")
    col1, col2, col3 = st.columns(3)
    with col1:
        show_demographics = st.checkbox("📍 ZIP Demographics", value=True)
    with col2:
        show_healthcare = st.checkbox("🏥 Healthcare Facilities", value=True)
    with col3:
        show_competitors = st.checkbox("🏢 Senior Housing", value=True)
    
    # Create map centered on Texas Triangle
    if metro_filter == "Houston":
        center = [29.76, -95.37]
        zoom = 9
    elif metro_filter == "DFW":
        center = [32.85, -96.85]
        zoom = 9
    else:
        center = [31.0, -96.5]  # Center of Texas Triangle
        zoom = 7
    
    m = folium.Map(location=center, zoom_start=zoom, tiles="cartodbpositron")
    
    # Add demographics layer
    if show_demographics and len(demographics) > 0:
        for _, row in demographics.iterrows():
            # Size based on population
            radius = min(max(row['pop_75_plus'] / 500, 5), 20)
            
            # Color based on income
            if row['median_income_65_plus'] >= 100000:
                color = '#22c55e'  # Green - high income
            elif row['median_income_65_plus'] >= 60000:
                color = '#3b82f6'  # Blue - medium-high
            else:
                color = '#f59e0b'  # Orange - moderate
            
            popup_html = f"""
            <b>ZIP: {row['zip_code']}</b><br>
            County: {row['county_name']}<br>
            75+ Pop: {row['pop_75_plus']:,}<br>
            Senior Income: ${row['median_income_65_plus']:,.0f}<br>
            Qualified HH: {row['income_qualified_il']:,}
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=radius,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                popup=folium.Popup(popup_html, max_width=200)
            ).add_to(m)
    
    # Add healthcare facilities
    if show_healthcare and len(healthcare) > 0:
        for _, row in healthcare.iterrows():
            popup_html = f"""
            <b>{row['facility_name']}</b><br>
            Type: {row['facility_type']}<br>
            City: {row['city']}<br>
            Beds: {row['beds']}
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.Icon(color='red', icon='plus', prefix='fa')
            ).add_to(m)
    
    # Add senior housing
    if show_competitors and len(senior_housing) > 0:
        for _, row in senior_housing.iterrows():
            popup_html = f"""
            <b>{row['facility_name']}</b><br>
            Type: {row['facility_type']}<br>
            City: {row['city']}<br>
            Units: {row['unit_count']}
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.Icon(color='purple', icon='home', prefix='fa')
            ).add_to(m)
    
    # Display map
    st_folium(m, width=None, height=600, use_container_width=True)
    
    # Legend
    st.markdown("### Legend")
    lcol1, lcol2, lcol3 = st.columns(3)
    with lcol1:
        st.markdown("**Demographics (circles)**")
        st.markdown("🟢 High Income (>$100K)")
        st.markdown("🔵 Medium Income ($60-100K)")
        st.markdown("🟠 Moderate Income (<$60K)")
        st.markdown("*Size = 75+ Population*")
    with lcol2:
        st.markdown("**Healthcare**")
        st.markdown("🔴 Hospitals & Medical Facilities")
    with lcol3:
        st.markdown("**Senior Housing**")
        st.markdown("🟣 Existing Communities")


def render_comparison_page():
    """Render the site comparison page."""
    st.markdown('<p class="main-header">📈 Site Comparison</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Compare multiple sites side by side</p>', unsafe_allow_html=True)
    
    # Get available ZIP codes
    conn = get_connection()
    zips = pd.read_sql("""
        SELECT zip_code, county_name, metro_area, pop_75_plus
        FROM demographics
        ORDER BY county_name, zip_code
    """, conn)
    conn.close()
    
    # Multi-select for ZIP codes
    st.markdown("### Select ZIP Codes to Compare (up to 5)")
    
    selected_zips = st.multiselect(
        "Select ZIP codes",
        zips['zip_code'].tolist(),
        format_func=lambda x: f"{x} - {zips[zips['zip_code']==x]['county_name'].values[0]} ({zips[zips['zip_code']==x]['pop_75_plus'].values[0]:,} seniors)",
        max_selections=5
    )
    
    if len(selected_zips) >= 2:
        if st.button("Compare Sites", type="primary"):
            with st.spinner("Calculating scores..."):
                comparison_df = compare_sites(selected_zips)
                
                if len(comparison_df) > 0:
                    st.markdown("### Comparison Results")
                    
                    # Display table
                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                    
                    # Visualization
                    st.markdown("### Score Comparison")
                    
                    # Bar chart of composite scores
                    fig1 = px.bar(
                        comparison_df,
                        x='ZIP Code',
                        y='Composite Score',
                        color='Rating',
                        color_discrete_map={
                            'Excellent': '#22c55e',
                            'Good': '#3b82f6',
                            'Moderate': '#f59e0b',
                            'Below Average': '#ef4444'
                        },
                        title="Composite Scores by Site"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Component comparison
                    st.markdown("### Component Score Breakdown")
                    
                    fig2 = go.Figure()
                    for _, row in comparison_df.iterrows():
                        fig2.add_trace(go.Bar(
                            name=row['ZIP Code'],
                            x=['Demographic', 'Market', 'Accessibility'],
                            y=[row['Demographic Score'], row['Market Score'], row['Accessibility Score']]
                        ))
                    
                    fig2.update_layout(barmode='group', title="Component Scores by Site")
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # Download comparison
                    csv = comparison_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Comparison",
                        csv,
                        "site_comparison.csv",
                        "text/csv"
                    )
    else:
        st.info("Select at least 2 ZIP codes to compare.")
    
    # Top markets quick view
    st.markdown("---")
    st.markdown("### 🏆 Top Scoring Markets")
    
    top_col1, top_col2 = st.columns(2)
    
    with top_col1:
        st.markdown("**Houston Metro**")
        houston_top = get_top_zip_codes(metro_area="Houston", limit=5)
        if houston_top:
            for site in houston_top:
                st.markdown(f"- **{site['zip_code']}** ({site['county_name']}): {site['composite_score']}/100 - {site['rating']}")
    
    with top_col2:
        st.markdown("**DFW Metro**")
        dfw_top = get_top_zip_codes(metro_area="DFW", limit=5)
        if dfw_top:
            for site in dfw_top:
                st.markdown(f"- **{site['zip_code']}** ({site['county_name']}): {site['composite_score']}/100 - {site['rating']}")


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Initialize database if needed
    initialize_database()
    
    # Check and load data
    just_loaded = check_and_load_data()
    if just_loaded:
        st.success("✅ Sample data loaded successfully!")
    
    # Render sidebar and get navigation
    page, metro_filter, min_pop = render_sidebar()
    
    # Render selected page
    if page == "💬 Chat Analysis":
        render_chat_page()
    elif page == "📊 Market Explorer":
        render_market_explorer()
    elif page == "🗺️ Map View":
        render_map_view()
    elif page == "📈 Site Comparison":
        render_comparison_page()


if __name__ == "__main__":
    main()
