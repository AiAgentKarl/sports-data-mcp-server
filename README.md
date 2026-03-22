# sports-data-mcp-server

MCP-Server für Sportdaten — Fußball, Basketball, American Football, Eishockey und mehr für AI-Agents.

## Features

- **11 Tools** für umfassende Sportdaten
- **Fußball**: Bundesliga, Premier League, La Liga, Serie A, Champions League, MLS und mehr
- **US-Sport**: NBA, NFL, NHL, MLB
- **Weitere Sportarten**: ATP Tennis, Formel 1, Rugby
- **Kostenlos**: Kein API-Key erforderlich (TheSportsDB Free Tier)

## Installation

```bash
pip install sports-data-mcp-server
```

Oder via `uvx`:
```bash
uvx sports-data-mcp-server
```

## Claude Desktop Konfiguration

```json
{
  "mcpServers": {
    "sports-data": {
      "command": "uvx",
      "args": ["sports-data-mcp-server"]
    }
  }
}
```

## Tools

### Fußball / Soccer
| Tool | Beschreibung |
|------|-------------|
| `search_team` | Team nach Name suchen |
| `get_team_last_results` | Letzte Ergebnisse eines Teams |
| `get_team_next_fixtures` | Nächste Spiele eines Teams |
| `get_league_table` | Liga-Tabelle abrufen |
| `search_player` | Spieler-Profil und Stats |
| `get_event_details` | Spiel-Details mit Highlight-Link |

### Multi-Sport
| Tool | Beschreibung |
|------|-------------|
| `list_sports_leagues` | Alle unterstützten Ligen |
| `get_league_events` | Spiele einer Saison (NBA, NFL, etc.) |
| `search_sport_event` | Sportereignis nach Name suchen |
| `get_sport_statistics` | Ligen-Übersicht nach Sportart |

## Beispiel-Nutzung

```python
# Bundesliga-Tabelle
tabelle = await get_league_table("bundesliga", "2024-2025")

# Bayern München letzte Spiele
team = await search_team("Bayern Munich")
ergebnisse = await get_team_last_results(team["teams"][0]["id"], count=5)

# NBA letzte Spiele
nba = await get_league_events("nba", "2024-2025")

# Spieler-Profil
spieler = await search_player("Robert Lewandowski")
```

## Unterstützte Ligen

### Fußball
- Bundesliga (1. und 2.)
- Premier League
- La Liga
- Serie A
- Ligue 1
- Champions League
- Eredivisie, MLS, Primeira Liga

### US-Sport
- NBA (Basketball)
- NFL (American Football)
- NHL (Ice Hockey)
- MLB (Baseball)

### Weitere
- ATP Tennis
- Formel 1
- Rugby 6 Nations

## Lizenz

MIT
