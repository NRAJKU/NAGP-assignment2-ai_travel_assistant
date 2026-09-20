# Assignment 2 — AI Travel Planning Assistant

Github Repo Link: https://github.com/NRAJKU/NAGP-assignment2-ai_travel_assistant

## 1. Overview

This project implements a context-aware AI travel assistant for Singapore.

The application combines:

- a document-based RAG knowledge base for stable destination information;
- MCP tools for current weather and currency information;
- an LLM for reasoning, tool selection, and response generation; and
- conversational context for multi-turn travel planning.

The application provides a simple Streamlit chat interface.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| LLM | Google Gemini (`gemini-3.5-flash-lite`) | Reasoning, tool selection, synthesis, and response generation |
| Agent orchestration | LangChain / LangGraph | Tool orchestration and conversation state |
| Embeddings | `BAAI/bge-m3` | Semantic embeddings for the knowledge base |
| Vector store | FAISS | Similarity search over knowledge-base chunks |
| RAG | LangChain + FAISS | Retrieval of stable Singapore travel knowledge |
| Weather MCP | Python MCP server + Open-Meteo | Current weather and forecast |
| Currency MCP | Python MCP server + Frankfurter | Current currency conversion |
| UI | Streamlit | User-facing chat application |

## 3. Architecture

```text
User
  |
  v
Streamlit
  |
  v
LangChain / LangGraph Agent
  |
  v
Gemini LLM
  |
  +-------------------+-------------------+
  |                   |                   |
  v                   v                   v
RAG Tool         Weather MCP        Currency MCP
  |                   |                   |
  v                   v                   v
BGE-M3             Open-Meteo         Frankfurter
  |
  v
FAISS
  |
  v
Singapore Knowledge Base
  |
  +-------------------+-------------------+
                      |
                      v
                Gemini LLM
                      |
                      v
                Final Response
```

The application keeps the information sources separate:

- **RAG** provides relatively stable Singapore destination knowledge.
- **Weather MCP** provides current weather and forecast information.
- **Currency MCP** provides current exchange-rate information.
- **Gemini** combines retrieved information, tool results, and conversation context into the final response.

## 4. Knowledge Base

The Singapore knowledge base contains content from four public travel resources:

1. Visit Singapore — Official Tourism Guide
2. Visit Singapore — 24 Hours in Singapore
3. Visit Singapore — Singapore Itineraries
4. Wikivoyage — Singapore Travel Guide

The source title, URL, and source type are retained as document metadata.

The knowledge base covers:

- major attractions and neighbourhoods;
- transportation;
- cultural and practical travel information;
- food and local experiences;
- sample itineraries; and
- indoor and outdoor activities.

Source information is also maintained in:

```text
data/source_registry.json
```

## 5. RAG Workflow

The RAG pipeline works as follows:

```text
Knowledge-base documents
        |
        v
Meaningful document chunks
        |
        v
BGE-M3 embeddings
        |
        v
FAISS vector store
        |
        v
Semantic retrieval
        |
        v
Retrieved context + source metadata
        |
        v
Gemini
        |
        v
Grounded response
```

The ingestion process:

1. Loads the Markdown knowledge-base documents.
2. Preserves source metadata.
3. Splits documents into meaningful overlapping chunks.
4. Generates `BAAI/bge-m3` embeddings.
5. Stores the embeddings in FAISS.

To rebuild the vector store:

```powershell
python scripts/ingest.py
```

The application retrieves relevant chunks for destination-related questions and provides their source information to the LLM.

If the knowledge base does not contain sufficient information, the assistant is instructed to state the limitation rather than invent destination facts.

## 6. MCP Tools

### Weather MCP

Implementation:

```text
mcp_servers/weather_server.py
```

The weather tool uses Open-Meteo to retrieve current weather and forecast information.

The returned information includes:

- current temperature;
- current weather condition;
- precipitation;
- daily minimum and maximum temperatures;
- precipitation probability; and
- precipitation amount.

Weather information is used when the user requests current weather, a forecast, or weather-based planning.

### Currency MCP

Implementation:

```text
mcp_servers/currency_server.py
```

The currency tool uses Frankfurter for currency conversion.

The returned information includes:

- rate date;
- source currency;
- target currency;
- exchange rate; and
- converted amount.

Currency information is retrieved through MCP rather than from the static travel knowledge base.

## 7. Tool Selection

The agent selects tools according to the user's intent.

| User request | Expected components |
|---|---|
| Singapore attractions | RAG + LLM |
| Singapore neighbourhoods and culture | RAG + LLM |
| Singapore transportation | RAG + LLM |
| Current Singapore weather | Weather MCP + LLM |
| Currency conversion | Currency MCP + LLM |
| Weather-aware itinerary | RAG + Weather MCP + LLM |
| Budget-aware itinerary | RAG + Currency MCP + LLM |
| Weather and budget-aware itinerary | RAG + Weather MCP + Currency MCP + LLM |

The agent is instructed not to use RAG as a substitute for current weather or currency information.

## 8. Combined RAG + MCP Scenario

The primary combined scenario is:

```text
Create a three-day Singapore itinerary for next week
and adjust it according to the weather forecast.
```

For this request, the application combines destination knowledge from RAG with current forecast information from Weather MCP.

The response distinguishes between:

- **Knowledge Base Facts** — information retrieved from the Singapore knowledge base.
- **MCP Current Information** — current information returned by an MCP tool.
- **AI Recommendations** — planning recommendations generated by the LLM.

If the requested travel dates are outside the available forecast range, the assistant explicitly states that the forecast does not cover those dates and does not substitute unrelated forecast data.

## 9. Prompt and Context Strategy

The system prompt establishes the following rules:

1. Use RAG for stable destination information.
2. Use Weather MCP for current weather and forecasts.
3. Use Currency MCP for current exchange rates.
4. Select only the tools relevant to the user's request.
5. Use all relevant sources for combined requests.
6. Do not present unsupported information as fact.
7. State clearly when required information is unavailable.
8. Distinguish knowledge-base facts, MCP information, and AI recommendations.
9. Include source information for knowledge-base content.
10. Preserve relevant user preferences across conversation turns.

For example:

```text
User:
I am travelling with two children. Keep the trip relaxed and family-friendly.

User:
Now make a three-day itinerary and adjust it for the forecast.
```

The second request can use the preference established in the first request without requiring the user to repeat it.

## 10. Error and Missing-Information Handling

The application is designed to avoid fabricating information when a dependency is unavailable.

Examples include:

- missing FAISS vector store → the RAG tool reports a knowledge-base error;
- weather service failure → the weather tool reports the failure;
- currency service failure → the currency tool reports the failure;
- insufficient retrieved knowledge → the assistant states that the available knowledge is insufficient;
- unavailable forecast dates → the assistant does not use an unrelated forecast as if it covered the requested dates.

## 11. Setup

### Prerequisites

- Python
- Gemini API key
- Windows PowerShell or equivalent terminal

### Create the environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Configure the application

Create `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Configure:

```text
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Do not commit `.env` or expose the API key.

### Build the knowledge base

```powershell
python scripts/ingest.py
```

### Start the application

```powershell
streamlit run app.py
```

## 12. Sample Questions

### RAG

```text
What are the must-visit attractions in Singapore and which neighbourhoods are suitable for cultural experiences?
```

Expected behavior:

- RAG retrieval is used.
- Stable destination information is returned.
- Source information is provided.

### Weather MCP

```text
What is the forecast for the next 3 days in Singapore?
```

Expected behavior:

- Weather MCP is used.
- Current forecast information is returned.
- Open-Meteo is identified as the source.

### Currency MCP

```text
Convert INR 50,000 to SGD.
```

Expected behavior:

- Currency MCP is used.
- The returned exchange rate and converted amount are presented.

### Combined RAG + MCP

```text
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

Expected behavior:

- RAG provides destination knowledge.
- Weather MCP provides current forecast information.
- Gemini combines both sources into a weather-aware itinerary.
- Facts, MCP information, and recommendations are distinguished.

### Multi-turn Context

```text
I am travelling with two children. Keep the trip relaxed and family-friendly.
```

Followed by:

```text
Now make a three-day itinerary and adjust it for the forecast.
```

Expected behavior:

- The second response retains the family and pacing preference.

## 13. Project Structure

```text
assignment2_ai_travel/
├── .streamlit/
│   └── config.toml
├── data/
│   ├── raw/
│   │   ├── 01_visit_singapore_overview.md
│   │   ├── 02_visit_singapore_itinerary.md
│   │   ├── 03_visit_singapore_itineraries.md
│   │   └── 04_wikivoyage_singapore.md
│   ├── source_registry.json
│   └── vectorstore/
├── docs/
│   ├── DEMO_SCRIPT.md
│   ├── LLM_ARCHITECTURE.md
│   └── SOURCE_NOTES.md
├── mcp_servers/
│   ├── weather_server.py
│   └── currency_server.py
├── scripts/
│   ├── fetch_sources.py
│   └── ingest.py
├── src/
│   └── rag_tools.py
├── .env.example
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

## 14. Demonstration

The demonstration covers the core assignment requirements:

1. RAG-based destination question.
2. Weather MCP query.
3. Currency MCP query.
4. Combined RAG + Weather MCP itinerary.
5. Multi-turn conversation context.
6. Failure and missing-information handling.

The detailed recording sequence is provided in:

```text
docs/DEMO_SCRIPT.md
```

## 15. Scope

The application focuses on travel planning and does not provide:

- flight booking;
- hotel booking;
- payment processing;
- travel reservations; or
- route-navigation services.

Current weather and currency information depend on the availability of their respective external services.
