"""
Garrison plugin for Terraria (TShock REST API).

TShock uses HTTP REST (default port 7878) with token auth, not Source RCON.
Token is obtained via POST /v2/token/create and included in subsequent requests.
"""

import aiohttp
from typing import Optional, List

try:
    from app.plugins.base import GamePlugin, PlayerInfo
except ImportError:
    from dataclasses import dataclass, field

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

        async def disconnect_custom(self):
            pass

        async def send_command_custom(self, command, content):
            raise NotImplementedError

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

    # ── Connection lifecycle ──────────────────────────────────────────────────

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

    async def disconnect_custom(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._token = None
        self._base_url = None
        self._session = None

    # Keep backward-compat alias
    async def disconnect(self):
        await self.disconnect_custom()

    # ── Low-level helpers ─────────────────────────────────────────────────────

    def _params(self, **extra) -> dict:
        return {"token": self._token, **extra}

    async def _get(self, path: str, **params):
        if not self._session or self._session.closed:
            raise ConnectionError("Not connected to TShock")
        async with self._session.get(
            f"{self._base_url}{path}",
            params=self._params(**params),
        ) as resp:
            return await resp.json(content_type=None)

    async def send_command_custom(self, command: str, content: str = "") -> str:
        """
        Execute a raw TShock server command via /v3/server/rawcmd.
        `command` is the full command string (e.g. "say Hello world").
        `content` is appended if non-empty.
        """
        cmd = f"{command} {content}".strip() if content else command
        data = await self._get("/v3/server/rawcmd", cmd=cmd)
        output = data.get("response", "")
        if isinstance(output, list):
            output = "\n".join(output)
        return output

    # ── Status & players ──────────────────────────────────────────────────────

    async def get_status(self, send_command) -> dict:
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

    def parse_players(self, raw_response) -> List[PlayerInfo]:
        """
        Parse TShock /v2/players/list response into PlayerInfo list.
        Response may be the full JSON dict or the players array directly.
        """
        if isinstance(raw_response, dict):
            players_data = raw_response.get("players", [])
        elif isinstance(raw_response, list):
            players_data = raw_response
        else:
            return []

        result = []
        for p in players_data:
            if isinstance(p, str):
                result.append(PlayerInfo(name=p))
            elif isinstance(p, dict):
                name = p.get("nickname") or p.get("name", "")
                result.append(PlayerInfo(
                    name=name,
                    steam_id=str(p.get("account", "")),
                    ping=p.get("ping", 0),
                ))
        return result

    async def get_players(self, send_command) -> List[PlayerInfo]:
        data = await self._get("/v2/players/list")
        return self.parse_players(data)

    # ── Moderation ────────────────────────────────────────────────────────────

    async def kick_player(self, send_command, name: str, reason: str = "") -> bool:
        params = {"player": name}
        if reason:
            params["reason"] = reason
        data = await self._get("/v2/players/kick", **params)
        return data.get("status") == "200"

    async def ban_player(self, send_command, name: str, reason: str = "") -> bool:
        params = {"player": name}
        if reason:
            params["reason"] = reason
        data = await self._get("/v2/bans/create", **params)
        return data.get("status") == "200"

    async def mute_player(self, send_command, name: str) -> bool:
        data = await self._get("/v2/players/mute", player=name)
        return data.get("status") == "200"

    async def unmute_player(self, send_command, name: str) -> bool:
        data = await self._get("/v2/players/unmute", player=name)
        return data.get("status") == "200"

    async def message_player(self, send_command, name: str, message: str) -> bool:
        """Send a private message to a player using the whisper command."""
        cmd = f"whisper {name} {message}"
        data = await self._get("/v3/server/rawcmd", cmd=cmd)
        return data.get("status") == "200"

    # ── Roles / groups ────────────────────────────────────────────────────────

    def get_player_roles(self) -> List[str]:
        """TShock built-in group hierarchy."""
        return ["owner", "superadmin", "admin", "moderator", "trusted", "default"]

    async def promote_player(self, send_command, player: str, role: str) -> bool:
        """Change a player's TShock group."""
        data = await self._get("/v2/users/updategroup", user=player, group=role)
        return data.get("status") == "200"

    async def demote_player(self, send_command, player: str) -> bool:
        """Reset a player's group to default."""
        return await self.promote_player(send_command, player, "default")

    # ── World ─────────────────────────────────────────────────────────────────

    async def get_world(self, send_command) -> dict:
        data = await self._get("/v2/world/read")
        return {
            "name": data.get("name", ""),
            "size": data.get("size", ""),
            "difficulty": data.get("difficulty", ""),
            "is_hardmode": data.get("isHardmode", False),
            "evil_type": data.get("evilType", ""),
            "raw": data,
        }

    # ── Bans ──────────────────────────────────────────────────────────────────

    async def get_bans(self, send_command) -> list:
        data = await self._get("/v2/bans/list")
        return data.get("bans", [])

    async def unban_player(self, send_command, identifier: str) -> bool:
        data = await self._get("/v2/bans/destroy", ban=identifier)
        return data.get("status") == "200"

    # ── Events ────────────────────────────────────────────────────────────────

    async def poll_events(self, send_command, since=None) -> list:
        """
        TShock REST API has no event stream endpoint.
        Returns empty list; event polling is not supported.
        """
        return []

    # ── Commands schema ───────────────────────────────────────────────────────

    def get_commands(self) -> list:
        """Return available commands from schema."""
        try:
            from . import schema
        except ImportError:
            try:
                import schema  # type: ignore
            except ImportError:
                return []
        return getattr(schema, "COMMANDS", [])

    # ── Misc helpers ──────────────────────────────────────────────────────────

    async def run_command(self, send_command, command: str) -> str:
        """Execute a raw server command and return text output."""
        return await self.send_command_custom(command)
