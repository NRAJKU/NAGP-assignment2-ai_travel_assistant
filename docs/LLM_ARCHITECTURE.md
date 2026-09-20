# LLM, RAG and MCP Interaction

The LLM is the inference and orchestration layer. It is not the embedding model.

```text
User
  |
  v
Streamlit
  |
  v
LangChain Agent
  |
  v
Gemini LLM
  |
  +------------------+------------------+
  |                  |                  |
  v                  v                  v
RAG Tool         Weather MCP       Currency MCP
  |                  |                  |
  v                  v                  v
BGE-M3            Open-Meteo        Frankfurter
  |
  v
FAISS
  |
  v
Singapore KB
  |
  +------------------+------------------+
                     |
                     v
                  Gemini LLM
                     |
                     v
              Final grounded answer
```

## Responsibilities

### LLM
- Understand the request.
- Select relevant tools.
- Combine tool outputs.
- Apply conversation context.
- Produce the final answer.

### BGE-M3
- Embed knowledge-base documents.
- Embed retrieval queries.
- Enable semantic similarity search.
- Does not generate answers.

### FAISS
- Store document vectors.
- Retrieve semantically similar chunks.

### RAG tool
- Expose Singapore KB retrieval to the agent.
- Return source title, URL and content.

### MCP tools
- Weather: current/forecast data.
- Currency: latest exchange conversion.

This separation ensures stable knowledge, current information and generative reasoning have distinct responsibilities.
