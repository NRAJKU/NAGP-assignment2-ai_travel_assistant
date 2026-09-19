from __future__ import annotations

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Currency Exchange MCP",
    instructions="Provides current/latest currency conversion using Frankfurter."
)

URL = "https://api.frankfurter.dev/v1/latest"


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount using the latest rate available from Frankfurter."""

    if amount < 0:
        return "TOOL_ERROR: amount must be non-negative."

    base = from_currency.upper().strip()
    target = to_currency.upper().strip()

    if len(base) != 3 or len(target) != 3:
        return "TOOL_ERROR: currencies must be three-letter ISO currency codes."

    if base == target:
        return (
            f"MCP_SOURCE: Frankfurter\n"
            f"rate_date: same currency\n"
            f"rate: 1\n"
            f"converted_amount: {amount:.2f} {target}"
        )

    try:
        r = requests.get(
            URL,
            params={"base": base, "symbols": target},
            timeout=20
        )
        r.raise_for_status()

        data = r.json()
        rate = float(data["rates"][target])
        converted = amount * rate

        return (
            f"MCP_SOURCE: Frankfurter\n"
            f"rate_date: {data.get('date')}\n"
            f"from_currency: {base}\n"
            f"to_currency: {target}\n"
            f"rate: {rate}\n"
            f"input_amount: {amount}\n"
            f"converted_amount: {converted:.2f}"
        )

    except Exception as exc:
        return f"TOOL_ERROR: Currency service unavailable: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")