# Assignment 2 — Demonstration Script

## Demo 1 — RAG only
Ask: `What are the must-visit attractions in Singapore and which neighbourhoods are suitable for cultural experiences?`

Show that the answer cites knowledge-base sources and does not call weather/currency for this question.

## Demo 2 — Weather MCP
Ask: `What is the forecast for the next three days in Singapore?`

Show that current information is identified as coming from the weather MCP/Open-Meteo.

## Demo 3 — Currency MCP
Ask: `Convert INR 50,000 to SGD.`

Show the current/latest rate date and MCP source.

## Demo 4 — Required combined scenario
Ask: `Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.`

Show that the agent uses RAG for attractions/itinerary ideas and weather MCP for the forecast, then produces day-by-day recommendations with indoor alternatives when rain is expected.

## Demo 5 — Multi-turn context
First: `I am travelling with two children. Keep the trip relaxed and family-friendly.`
Second: `Now make a three-day itinerary and adjust it for the forecast.`

The second answer should preserve the family/relaxed preference.

## Demo 6 — Failure handling
Temporarily rename `data/vectorstore/index.faiss` or stop network access and ask a question that needs that component. Show that the application reports the missing/failed component rather than inventing a result. Restore the component afterward.
