"""
Garrison plugin for Terraria (TShock REST API).

TShock uses HTTP REST (default port 7878) with token auth, not Source RCON.
Token is obtained via POST /v2/token/create and included in subsequent requests.
"""

import aiohttp
from typing import Optional

try:
    from app.plugins.base import GamePlugin, PlayerInfo
except ImportError:
    # Standalone / testing fallback
    from dataclasses import dataclass, field
    from typing import List

    @dataclass
    class PlayerInfo:
        name: str
        steam_id: str = ""
        ping: int = 0
        score: int = 0

    class GamePlugin:
        custom_connection = False

        async def connect_custom(self, host, port, password):
            raise NotImplementedError

        async def disconnect(self):
            pass

        async def get_players(self, send_command):
            raise NotImplementedError

        async def kick_player(self, send_command, name, reason=""):
            raise NotImplementedError

        async def ban_player(self, send_command, name, reason=""):
            raise NotImplementedError

        async def get_status(self, send_command):
            raise NotImplementedError


class TerrariaPlugin(GamePlugin):
    """Terraria plugin using TShock REST API."""

    custom_connection = True

    def __init__(self):
        self._token: Optional[str] = None
        self._base_url: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

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

    async def disconnect(self):
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

    async def get_players(self, send_command) -> list:
        """Return list of online players."""
        data = await self._get("/v2/players/list")

        players = []
        for p in data.get("players", []):
            name = p if isinstance(p, str) else p.get("nickname", p.get("name", ""))
            players.append(PlayerInfo(name=name))

        return players

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

    async def get_status(self, send_command) -> dict:
        """Return server status info."""
        data = await self._get("/v2/server/status")

        return {
            "name": data.get("name", ""),
            "port": data.get("port"),
            "player_count": data.get("playercount", 0),
            "max_players": data.get("maxplayers", 0),
            "world": data.get("world", ""),
            "uptime": data.get("uptime", ""),
            "tshock_version": data.get("serverversion", ""),
            "raw": data,
        }

    async def run_command(self, send_command, command: str) -> str:
        """Execute a raw TShock server command."""
        data = await self._get("/v3/server/rawcmd", cmd=command)
        output = data.get("response", "")
        if isinstance(output, list):
            output = "\n".join(output)
        return output
