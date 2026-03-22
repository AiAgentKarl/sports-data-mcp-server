"""Sports Data MCP Server — Sportdaten für AI-Agents.

Bietet:
- Fußball: Teams, Tabellen, Ergebnisse, Spieler-Profile (Bundesliga, Premier League, La Liga, etc.)
- Multi-Sport: NBA, NFL, NHL, MLB, Tennis, Formel 1
- Live-Ergebnisse und kommende Fixtures
- Spieler-Statistiken und Team-Profile
- Alle Daten kostenlos via TheSportsDB (kein API-Key erforderlich)
"""

from mcp.server.fastmcp import FastMCP

from src.tools.football import register_football_tools
from src.tools.multisport import register_multisport_tools

# FastMCP Server erstellen
mcp = FastMCP(
    "Sports Data MCP Server",
    instructions=(
        "Gibt AI-Agents Zugriff auf weltweite Sportdaten: "
        "Fußball-Ligen (Bundesliga, Premier League, La Liga, Serie A, Champions League), "
        "US-Sport (NBA, NFL, NHL, MLB), Tennis ATP, Formel 1 und mehr. "
        "Tools: Team-Suche, Liga-Tabellen, Ergebnisse, Fixtures, Spieler-Profile, Event-Details. "
        "Alle Daten kostenlos ohne API-Key via TheSportsDB."
    ),
)

# Tool-Gruppen registrieren
register_football_tools(mcp)
register_multisport_tools(mcp)


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
