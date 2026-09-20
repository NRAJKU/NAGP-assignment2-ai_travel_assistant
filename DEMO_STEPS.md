# Assignment 2 — Demo

## 1. Prepare the project

Open a PowerShell terminal in the project root and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the virtual environment is already created, only activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 2. Configure the LLM

Create the environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add the Gemini API key:

```text
GEMINI_API_KEY=your_api_key
GEMEINI_MODEL=gemini-3.5-flash-lite
```

## 3. Build the RAG knowledge base

Run:

```powershell
python scripts/ingest.py
```

#### Reasoning

> The ingestion script loads the Singapore travel documents, splits them into meaningful chunks, generates BGE-M3 embeddings, and stores the vectors in FAISS. The resulting vector store is then used by the RAG retrieval tool.

Wait for ingestion to complete successfully before continuing.

## 4. Start the application

Run:

```powershell
streamlit run app.py
```

Streamlit will open the Travel Assistant in the browser. Do not close the terminal because the application is running from it.

## 5. Demo 1 — RAG-only question

Enter:

```text
What are the must-visit attractions in Singapore and which neighbourhoods are suitable for cultural experiences?
```

Demonstratation:

- The LLM answers using the Singapore knowledge base.
- The response contains source information for knowledge-base facts.
- No live weather or currency information is needed for this question.

#### Reasoning

> This demonstrates the RAG path. BGE-M3 converts the query into an embedding, FAISS retrieves relevant Singapore knowledge-base chunks, and the LLM uses that retrieved context to generate the answer.

## 6. Demo 2 — Weather MCP

Enter:

```text
What is the forecast for the next three days in Singapore?
```

Demonstratation:

- The answer contains current/forecast information.
- The response identifies the weather information as coming from the MCP weather service/Open-Meteo.

#### Reasoning

> Weather is time-sensitive, so the assistant does not rely on the static RAG knowledge base. The LLM uses the Weather MCP tool to obtain current forecast information.

## 7. Demo 3 — Currency MCP

Enter:

```text
Convert INR 50,000 to SGD.
```

Demonstratation:

- The assistant uses the Currency MCP tool.
- The answer includes the current/latest rate information and source/date where returned by the tool.

#### Reasoning

> Currency information can change, so it is obtained through the Currency MCP rather than stored in the static vector database.

## 8. Demo 4 — Required RAG + MCP scenario

Enter:

```text
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

### Assistant combines:

```text
Singapore destination knowledge
        ↓
       RAG
   BGE-M3 + FAISS

Current weather
        ↓
   Weather MCP

        ↓
       LLM
        ↓
Weather-aware itinerary
```

The response should distinguish, where appropriate:

- Knowledge-base facts
- Current MCP information
- AI recommendations

#### Reasoning

> This is the combined scenario required by the assignment. The LLM uses RAG for stable Singapore destination information and Weather MCP for the current forecast. It then combines those inputs to produce a weather-aware three-day itinerary.

## 9. Demo 5 — Multi-turn conversation context

Enter:

```text
I am travelling with two children. Keep the trip relaxed and family-friendly.
```

Enter:

```text
Now make a three-day itinerary and adjust it for the forecast.
```

Demonstratation:

- The second response respects the children/family-friendly preference.
- The user does not need to repeat the preference.
- Weather information is still obtained from Weather MCP.

#### Reasoning

> This demonstrates conversational context. The application keeps the conversation state, so the later itinerary request can use the preference provided in the previous turn.

## 10. Demo 6 — Failure handling

Demonstration, stop or delete one required dependency (ex - `data/vectorstore/`) and issue this question as it requires it.

Enter:

```text
What are the main attractions in Singapore?
```

#### Expectation:
The application will report that the knowledge base/vector store is unavailable rather than inventing retrieved facts.

#### Reasoning
After the demonstration, restore the vector store.
