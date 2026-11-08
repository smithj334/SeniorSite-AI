# SeniorSite AI

## AI-Powered Senior Housing Site Selection System for the Texas Triangle

SeniorSite AI is a prototype system that enables institutional senior housing developers to analyze demographic, healthcare, and market data through natural language queries. The system covers the Houston and Dallas-Fort Worth metropolitan areas.

---

## Quick Start (Windows)

### Step 1: Install Python Dependencies

Open Command Prompt or PowerShell in this folder and run:

```
pip install -r requirements.txt
```

### Step 2: Start Ollama (for AI features)

Make sure Ollama is running with Llama 3.1:

```
ollama run llama3.1
```

Leave this terminal open. The AI features require Ollama to be running.

### Step 3: Launch the Application

Open a NEW Command Prompt/PowerShell window (keep Ollama running in the first one):

```
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

---

## Features

### 💬 Chat Analysis
Ask natural language questions about senior housing markets:
- "Show me ZIP codes in Collin County where the 75+ population exceeds 3,000"
- "What are the top markets by senior income in the Houston metro?"
- "Find areas with high concentrations of seniors near hospitals"

### 📊 Market Explorer
- Browse demographic data by ZIP code
- Filter by metro area and population thresholds
- Visualize population and income distributions
- Calculate site scores for any ZIP code

### 🗺️ Map View
- Interactive map of the Texas Triangle
- View demographic markers sized by population
- See healthcare facilities and competitor locations
- Color-coded by income levels

### 📈 Site Comparison
- Compare up to 5 ZIP codes side by side
- View composite scores and component breakdowns
- Identify top-scoring markets by metro area

---

## Data Coverage

The prototype includes sample data for:

**Houston Metro:**
- Harris County
- Fort Bend County  
- Montgomery County

**Dallas-Fort Worth Metro:**
- Dallas County
- Collin County
- Tarrant County
- Denton County

---

## Project Structure

```
seniorsite_ai/
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── database.py         # DuckDB database management
├── data_loader.py      # Sample data and data loading
├── analytics.py        # Industry metrics calculations
├── llm_interface.py    # LangChain + Ollama integration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11 | Primary development |
| Database | DuckDB | Analytical queries |
| LLM Server | Ollama | Local model hosting |
| AI Model | Llama 3.1 8B | Natural language understanding |
| AI Framework | LangChain | Query orchestration |
| Web Interface | Streamlit | Dashboard & chat UI |
| Visualization | Plotly, Folium | Charts & maps |

---

## Troubleshooting

### "Ollama connection failed"
- Make sure Ollama is running (`ollama run llama3.1`)
- Check that it's accessible at http://localhost:11434
- The Chat Analysis page requires Ollama; other pages work without it

### "No data found"
- The application auto-loads sample data on first run
- If tables are empty, restart the application

### "Module not found" errors
- Run `pip install -r requirements.txt` again
- Make sure you're using Python 3.9 or higher

### Streamlit won't start
- Try: `python -m streamlit run app.py`
- Check that port 8501 isn't in use

---

## Extending the System

### Adding Real Census Data
1. Get a free API key at https://api.census.gov/data/key_signup.html
2. Add it to `config.py` as `CENSUS_API_KEY`
3. Modify `data_loader.py` to fetch live data

### Adding More Counties
1. Add county FIPS codes to `TEXAS_TRIANGLE_COUNTIES` in `config.py`
2. Update sample data in `data_loader.py`
3. Re-run the data loader

### Customizing Scoring Weights
Modify `DEFAULT_SCORING_WEIGHTS` in `config.py`:
```python
DEFAULT_SCORING_WEIGHTS = {
    "demographic": 0.40,    # Population, income factors
    "market": 0.35,         # Penetration, competition
    "accessibility": 0.25   # Healthcare proximity
}
```

---

## For Demo/Presentation

1. **Start Ollama first** - Run `ollama run llama3.1` and leave it running
2. **Launch the app** - Run `streamlit run app.py` in a separate terminal
3. **Show Chat Analysis** - Ask a few natural language questions
4. **Show Market Explorer** - Demonstrate filtering and site scoring
5. **Show Map View** - Display geographic distribution
6. **Show Site Comparison** - Compare top markets

**Sample demo questions:**
- "Show me ZIP codes in Collin County with senior population above 3000"
- "What are the highest income senior markets in Houston?"
- "List hospitals in the DFW area"
- "Which ZIP codes have the best penetration rates?"

---

## License

This is a prototype system for educational/demonstration purposes.

---

## Contact

For questions about this system, refer to the technical proposal document.
