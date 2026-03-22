"""Multi-Sport Tools — NBA, NFL, Tennis und weitere Sportarten via TheSportsDB."""

import httpx
from typing import Any


THESPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"

# Bekannte Sport-Liga-IDs
SPORT_LIGEN = {
    "nba": {"id": "4387", "land": "USA", "sport": "Basketball"},
    "nfl": {"id": "4391", "land": "USA", "sport": "American Football"},
    "nhl": {"id": "4380", "land": "USA/Canada", "sport": "Ice Hockey"},
    "mlb": {"id": "4424", "land": "USA", "sport": "Baseball"},
    "atp_tennis": {"id": "4658", "land": "International", "sport": "Tennis"},
    "formula1": {"id": "4370", "land": "International", "sport": "Motorsport"},
    "rugby_6_nations": {"id": "4582", "land": "Europe", "sport": "Rugby"},
    "nba_g_league": {"id": "4389", "land": "USA", "sport": "Basketball"},
}


async def _sportsdb_get(endpoint: str, params: dict = None) -> dict[str, Any]:
    """TheSportsDB API Anfrage."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{THESPORTSDB_BASE}/{endpoint}",
                params=params or {},
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}


def register_multisport_tools(mcp) -> None:
    """Registriert alle Multi-Sport Tools."""

    @mcp.tool()
    async def list_sports_leagues() -> dict:
        """Gibt eine Übersicht aller unterstützten Sport-Ligen zurück."""
        return {
            "ligen": [
                {
                    "schluessel": key,
                    "liga_id": info["id"],
                    "sport": info["sport"],
                    "land": info["land"],
                }
                for key, info in SPORT_LIGEN.items()
            ],
            "gesamt": len(SPORT_LIGEN),
            "hinweis": "Verwende get_league_events mit dem 'schluessel' als league_key",
        }

    @mcp.tool()
    async def get_league_events(league_key: str, season: str = "2024-2025") -> dict:
        """Ruft Spiele einer Sport-Liga für eine Saison ab.

        Args:
            league_key: Liga-Schlüssel aus list_sports_leagues (z.B. nba, nfl, nhl)
            season: Saison (Standard: 2024-2025, bei NFL/NBA oft 2024)
        """
        if league_key not in SPORT_LIGEN:
            return {
                "fehler": f"Unbekannte Liga '{league_key}'",
                "verfuegbare": list(SPORT_LIGEN.keys()),
            }

        liga_info = SPORT_LIGEN[league_key]
        daten = await _sportsdb_get(
            "eventsseason.php",
            {"id": liga_info["id"], "s": season},
        )

        if "error" in daten:
            return {"fehler": daten["error"]}

        events = daten.get("events") or []
        letzte_spiele = []
        for event in events[-20:]:  # Letzte 20 Spiele der Saison
            score_heim = event.get("intHomeScore")
            score_auswaerts = event.get("intAwayScore")
            ergebnis = f"{score_heim} : {score_auswaerts}" if score_heim is not None else "Geplant"
            letzte_spiele.append({
                "datum": event.get("dateEvent"),
                "heim": event.get("strHomeTeam"),
                "auswaerts": event.get("strAwayTeam"),
                "ergebnis": ergebnis,
                "runde": event.get("intRound"),
                "venue": event.get("strVenue"),
            })

        return {
            "liga": league_key,
            "sport": liga_info["sport"],
            "saison": season,
            "letzte_20_spiele": letzte_spiele,
            "gesamt_events_in_saison": len(events),
        }

    @mcp.tool()
    async def search_sport_event(event_name: str) -> dict:
        """Sucht ein Sportereignis nach Name.

        Args:
            event_name: Ereignisname (z.B. "Super Bowl", "NBA Finals", "Wimbledon")
        """
        daten = await _sportsdb_get("searchevents.php", {"e": event_name})
        if "error" in daten:
            return {"fehler": daten["error"]}

        events = daten.get("event") or []
        if not events:
            return {"fehler": f"Kein Ereignis '{event_name}' gefunden"}

        ergebnisse = []
        for event in events[:10]:
            ergebnisse.append({
                "id": event.get("idEvent"),
                "name": event.get("strEvent"),
                "datum": event.get("dateEvent"),
                "sport": event.get("strSport"),
                "liga": event.get("strLeague"),
                "heim": event.get("strHomeTeam"),
                "auswaerts": event.get("strAwayTeam"),
                "ergebnis": f"{event.get('intHomeScore', '?')} : {event.get('intAwayScore', '?')}",
                "venue": event.get("strVenue"),
                "land": event.get("strCountry"),
            })

        return {
            "suchbegriff": event_name,
            "gefunden": len(ergebnisse),
            "events": ergebnisse,
        }

    @mcp.tool()
    async def get_sport_statistics(sport: str) -> dict:
        """Gibt eine Übersicht der verfügbaren Ligen für einen Sport zurück.

        Args:
            sport: Sportart (z.B. Soccer, Basketball, American Football, Ice Hockey, Tennis)
        """
        daten = await _sportsdb_get("all_leagues.php", {"s": sport})
        if "error" in daten:
            return {"fehler": daten["error"]}

        leagues = daten.get("leagues") or daten.get("countrys") or []
        ergebnisse = []
        for liga in leagues[:20]:
            ergebnisse.append({
                "id": liga.get("idLeague"),
                "name": liga.get("strLeague"),
                "kurz": liga.get("strLeagueAlternate"),
                "sport": liga.get("strSport"),
                "land": liga.get("strCountry"),
                "gender": liga.get("strGender"),
                "logo": liga.get("strBadge"),
            })

        return {
            "sport": sport,
            "ligen_gefunden": len(ergebnisse),
            "ligen": ergebnisse,
        }
