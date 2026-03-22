"""Football/Soccer Tools — Ergebnisse, Tabellen und Statistiken via TheSportsDB."""

import httpx
from typing import Any


THESPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"

# Bekannte Liga-IDs
LIGA_IDS = {
    "bundesliga": "4331",
    "premier_league": "4328",
    "la_liga": "4335",
    "serie_a": "4332",
    "ligue_1": "4334",
    "champions_league": "4480",
    "mls": "4346",
    "bundesliga_2": "4737",
    "eredivisie": "4337",
    "primeira_liga": "4344",
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


def register_football_tools(mcp) -> None:
    """Registriert alle Football/Soccer Tools."""

    @mcp.tool()
    async def search_team(team_name: str) -> dict:
        """Sucht ein Sportteam nach Name und gibt Details zurück.

        Args:
            team_name: Teamname (z.B. "Bayern Munich", "Liverpool", "Real Madrid")
        """
        daten = await _sportsdb_get("searchteams.php", {"t": team_name})
        if "error" in daten:
            return {"fehler": daten["error"]}

        teams = daten.get("teams") or []
        if not teams:
            return {"fehler": f"Kein Team '{team_name}' gefunden"}

        ergebnisse = []
        for team in teams[:5]:
            ergebnisse.append({
                "id": team.get("idTeam"),
                "name": team.get("strTeam"),
                "kurzname": team.get("strTeamShort"),
                "land": team.get("strCountry"),
                "liga": team.get("strLeague"),
                "liga_id": team.get("idLeague"),
                "stadion": team.get("strStadium"),
                "begruendet": team.get("intFormedYear"),
                "logo": team.get("strTeamBadge"),
                "website": team.get("strWebsite"),
                "facebook": team.get("strFacebook"),
                "beschreibung_en": (team.get("strDescriptionEN") or "")[:300],
            })
        return {
            "suchbegriff": team_name,
            "gefunden": len(ergebnisse),
            "teams": ergebnisse,
        }

    @mcp.tool()
    async def get_team_last_results(team_id: str, count: int = 5) -> dict:
        """Ruft die letzten Ergebnisse eines Teams ab.

        Args:
            team_id: Team-ID (aus search_team erhalten)
            count: Anzahl der letzten Spiele (Standard: 5, max: 15)
        """
        count = min(count, 15)
        daten = await _sportsdb_get("eventslast.php", {"id": team_id})
        if "error" in daten:
            return {"fehler": daten["error"]}

        events = daten.get("results") or []
        ergebnisse = []
        for event in events[:count]:
            ergebnisse.append({
                "datum": event.get("dateEvent"),
                "heim": event.get("strHomeTeam"),
                "auswaerts": event.get("strAwayTeam"),
                "ergebnis": f"{event.get('intHomeScore', '?')} : {event.get('intAwayScore', '?')}",
                "wettbewerb": event.get("strLeague"),
                "runde": event.get("intRound"),
                "venue": event.get("strVenue"),
                "event_id": event.get("idEvent"),
            })
        return {
            "team_id": team_id,
            "letzte_spiele": len(ergebnisse),
            "ergebnisse": ergebnisse,
        }

    @mcp.tool()
    async def get_team_next_fixtures(team_id: str, count: int = 5) -> dict:
        """Ruft die nächsten geplanten Spiele eines Teams ab.

        Args:
            team_id: Team-ID (aus search_team erhalten)
            count: Anzahl der nächsten Spiele (Standard: 5, max: 15)
        """
        count = min(count, 15)
        daten = await _sportsdb_get("eventsnext.php", {"id": team_id})
        if "error" in daten:
            return {"fehler": daten["error"]}

        events = daten.get("events") or []
        spiele = []
        for event in events[:count]:
            spiele.append({
                "datum": event.get("dateEvent"),
                "uhrzeit": event.get("strTime"),
                "heim": event.get("strHomeTeam"),
                "auswaerts": event.get("strAwayTeam"),
                "wettbewerb": event.get("strLeague"),
                "runde": event.get("intRound"),
                "venue": event.get("strVenue"),
                "event_id": event.get("idEvent"),
            })
        return {
            "team_id": team_id,
            "naechste_spiele": len(spiele),
            "fixtures": spiele,
        }

    @mcp.tool()
    async def get_league_table(league_name: str, season: str = "2024-2025") -> dict:
        """Ruft die aktuelle Tabelle einer Liga ab.

        Args:
            league_name: Liga-Name — bundesliga, premier_league, la_liga, serie_a, ligue_1, champions_league, mls, eredivisie
            season: Saison (Standard: 2024-2025)
        """
        league_id = LIGA_IDS.get(league_name.lower().replace(" ", "_"))
        if not league_id:
            return {
                "fehler": f"Liga '{league_name}' nicht gefunden",
                "verfuegbare_ligen": list(LIGA_IDS.keys()),
            }

        daten = await _sportsdb_get("lookuptable.php", {"l": league_id, "s": season})
        if "error" in daten:
            return {"fehler": daten["error"]}

        tabelle_roh = daten.get("table") or []
        tabelle = []
        for eintrag in tabelle_roh:
            tabelle.append({
                "platz": eintrag.get("intRank"),
                "team": eintrag.get("strTeam"),
                "spiele": eintrag.get("intPlayed"),
                "siege": eintrag.get("intWin"),
                "unentschieden": eintrag.get("intDraw"),
                "niederlagen": eintrag.get("intLoss"),
                "tore": eintrag.get("intGoalsFor"),
                "gegentore": eintrag.get("intGoalsAgainst"),
                "tordifferenz": eintrag.get("intGoalDifference"),
                "punkte": eintrag.get("intPoints"),
                "form": eintrag.get("strForm"),
            })

        return {
            "liga": league_name,
            "saison": season,
            "tabellen_groesse": len(tabelle),
            "tabelle": tabelle,
        }

    @mcp.tool()
    async def search_player(player_name: str) -> dict:
        """Sucht einen Spieler nach Name und gibt Statistiken zurück.

        Args:
            player_name: Spielername (z.B. "Lionel Messi", "Robert Lewandowski")
        """
        daten = await _sportsdb_get("searchplayers.php", {"p": player_name})
        if "error" in daten:
            return {"fehler": daten["error"]}

        players = daten.get("player") or []
        if not players:
            return {"fehler": f"Kein Spieler '{player_name}' gefunden"}

        ergebnisse = []
        for player in players[:5]:
            ergebnisse.append({
                "id": player.get("idPlayer"),
                "name": player.get("strPlayer"),
                "geburtsdatum": player.get("dateBorn"),
                "nationalitaet": player.get("strNationality"),
                "position": player.get("strPosition"),
                "team": player.get("strTeam"),
                "liga": player.get("strLeague"),
                "geburtsstaedte": player.get("strBirthLocation"),
                "groesse": player.get("strHeight"),
                "gewicht": player.get("strWeight"),
                "foto": player.get("strThumb"),
                "beschreibung_en": (player.get("strDescriptionEN") or "")[:300],
            })

        return {
            "suchbegriff": player_name,
            "gefunden": len(ergebnisse),
            "spieler": ergebnisse,
        }

    @mcp.tool()
    async def get_event_details(event_id: str) -> dict:
        """Ruft Details zu einem einzelnen Sportereignis ab.

        Args:
            event_id: Event-ID (aus anderen Tools erhalten)
        """
        daten = await _sportsdb_get("lookupevent.php", {"id": event_id})
        if "error" in daten:
            return {"fehler": daten["error"]}

        events = daten.get("events") or []
        if not events:
            return {"fehler": f"Event {event_id} nicht gefunden"}

        event = events[0]
        return {
            "id": event.get("idEvent"),
            "name": event.get("strEvent"),
            "datum": event.get("dateEvent"),
            "uhrzeit": event.get("strTime"),
            "heim_team": event.get("strHomeTeam"),
            "auswaerts_team": event.get("strAwayTeam"),
            "heim_score": event.get("intHomeScore"),
            "auswaerts_score": event.get("intAwayScore"),
            "halbzeit": f"{event.get('intHomeScoreExtraTime', '?')} : {event.get('intAwayScoreExtraTime', '?')}",
            "liga": event.get("strLeague"),
            "saison": event.get("strSeason"),
            "venue": event.get("strVenue"),
            "zuschauer": event.get("intAttendance"),
            "beschreibung": (event.get("strDescriptionEN") or "")[:300],
            "highlight_url": event.get("strVideo"),
        }
