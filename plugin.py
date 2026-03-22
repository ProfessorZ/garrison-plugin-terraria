"""
Garrison plugin for Terraria (TShock REST API).

TShock uses HTTP REST (default port 7878) with token auth, not Source RCON.
Token is obtained via POST /v2/token/create and included in subsequent requests.
"""

import aiohttp
import json
from typing import Optional

from app.plugins.base import GamePlugin, PlayerInfo, ServerStatus, CommandDef


class TerrariaPlugin(GamePlugin):
    """Terraria plugin using TShock REST API."""

    custom_connection = True

    def __init__(self):
        self._token: Optional[str] = None
        self._base_url: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def game_type(self) -> str:
        return "terraria"

    @property
    def display_name(self) -> str:
        return "Terraria"

    async def parse_players(self, raw_response: str) -> list[PlayerInfo]:
        """Parse TShock /v2/players/list JSON response."""
        try:
            data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
            players = []
            for p in data.get("players", []):
                name = p if isinstance(p, str) else p.get("nickname", p.get("name", ""))
                players.append(PlayerInfo(name=name))
            return players
        except Exception:
            return []

    async def get_status(self, send_command) -> ServerStatus:
        """Return server status."""
        try:
            data = await self._get("/v2/server/status")
            return ServerStatus(
                online=True,
                player_count=data.get("playercount", 0),
                version=data.get("serverversion"),
                extra={
                    "name": data.get("name", ""),
                    "world": data.get("world", ""),
                    "maxplayers": data.get("maxplayers", 0),
                },
            )
        except Exception:
            return ServerStatus(online=False)

    def get_commands(self) -> list[CommandDef]:
        try:
            from schema import get_commands
            return get_commands()
        except ImportError:
            return []

    async def connect_custom(self, host: str, port: int, password: str) -> bool:
        """Authenticate with TShock REST API and obtain a session token."""
        self._base_url = f"http://{host}:{port}"

        try:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )

            async with self._session.post(
                f"{self._base_url}/v2/token/create",
                data={"password": password},
            ) as resp:
                data = await resp.json(content_type=None)

                if data.get("status") == "200" or resp.status == 200:
                    self._token = data.get("token")
                    if self._token:
                        return True

                error = data.get("error", "Unknown error")
                raise ConnectionError(f"TShock auth failed: {error}")

        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(f"Cannot connect to TShock at {self._base_url}: {e}")
        except Exception:
            if self._session and not self._session.closed:
                await self._session.close()
            raise

    async def disconnect(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._token = None
        self._base_url = None
        self._session = None

    def _params(self, **extra) -> dict:
        """Build query params with token."""
        return {"token": self._token, **extra}

    async def _get(self, path: str, **params):
        """Make an authenticated GET request."""
        if not self._session or self._session.closed:
            raise ConnectionError("Not connected to TShock")

        async with self._session.get(
            f"{self._base_url}{path}",
            params=self._params(**params),
        ) as resp:
            return await resp.json(content_type=None)

    async def get_players(self, send_command) -> list[PlayerInfo]:
        """Return list of online players."""
        data = await self._get("/v2/players/list")
        raw = json.dumps(data)
        return await self.parse_players(raw)

    async def kick_player(self, send_command, name: str, reason: str = "") -> bool:
        """Kick a player by name."""
        params = {"player": name}
        if reason:
            params["reason"] = reason
        data = await self._get("/v2/players/kick", **params)
        return data.get("status") == "200"

    async def ban_player(self, send_command, name: str, reason: str = "") -> bool:
        """Ban a player by name."""
        params = {"player": name}
        if reason:
            params["reason"] = reason
        data = await self._get("/v2/bans/create", **params)
        return data.get("status") == "200"

    async def run_command(self, send_command, command: str) -> str:
        """Execute a raw TShock server command."""
        data = await self._get("/v3/server/rawcmd", cmd=command)
        output = data.get("response", "")
        if isinstance(output, list):
            output = "\n".join(output)
        return output
