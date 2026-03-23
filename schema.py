"""
TShock command schema for Garrison.
Covers TShock 4.x / 5.x built-in commands.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TerrariaConnectionConfig(BaseModel):
    host: str = Field(..., description="TShock server hostname or IP")
    port: int = Field(7878, description="TShock REST API port (default: 7878)")
    password: str = Field(..., description="TShock REST API password")


class TerrariaPlayerInfo(BaseModel):
    name: str
    ip: Optional[str] = None
    team: Optional[int] = None
    difficulty: Optional[str] = None
    account: Optional[str] = None
    ping: Optional[int] = None


# ── Command definitions ────────────────────────────────────────────────────────
# Each entry: { "name": str, "description": str, "usage": str, "group": str }

COMMANDS = [
    # Server management
    {"name": "exit", "description": "Gracefully shuts down the server", "usage": "/exit", "group": "server"},
    {"name": "exit-nosave", "description": "Shuts down the server without saving", "usage": "/exit-nosave", "group": "server"},
    {"name": "save", "description": "Saves the world", "usage": "/save", "group": "server"},
    {"name": "restart", "description": "Restarts the server", "usage": "/restart", "group": "server"},
    {"name": "reload", "description": "Reloads config, groups, and regions", "usage": "/reload", "group": "server"},
    {"name": "version", "description": "Shows server version", "usage": "/version", "group": "server"},
    {"name": "uptime", "description": "Shows server uptime", "usage": "/uptime", "group": "server"},
    {"name": "serverpassword", "description": "Changes or shows the server password", "usage": "/serverpassword [password]", "group": "server"},
    {"name": "motd", "description": "Shows or sets the message of the day", "usage": "/motd [message]", "group": "server"},
    {"name": "rules", "description": "Shows or sets the server rules", "usage": "/rules [rules]", "group": "server"},
    {"name": "stats", "description": "Shows server stats", "usage": "/stats", "group": "server"},
    {"name": "maxspawns", "description": "Sets max mob spawns", "usage": "/maxspawns <count>", "group": "server"},
    {"name": "spawnrate", "description": "Sets mob spawn rate", "usage": "/spawnrate <rate>", "group": "server"},
    {"name": "settempgroup", "description": "Temporarily sets a player's group", "usage": "/settempgroup <player> <group>", "group": "server"},
    # Broadcast / chat
    {"name": "say", "description": "Broadcasts a message to all players", "usage": "/say <message>", "group": "chat"},
    {"name": "whisper", "description": "Sends a private message to a player", "usage": "/whisper <player> <message>", "group": "chat"},
    {"name": "reply", "description": "Replies to the last whisper", "usage": "/reply <message>", "group": "chat"},
    {"name": "broadcast", "description": "Broadcasts a message (alias: /bc)", "usage": "/broadcast <message>", "group": "chat"},
    # Player management
    {"name": "kick", "description": "Kicks a player from the server", "usage": "/kick <player> [reason]", "group": "players"},
    {"name": "ban", "description": "Bans a player by name", "usage": "/ban <player> [reason]", "group": "players"},
    {"name": "unban", "description": "Unbans a player", "usage": "/unban <player>", "group": "players"},
    {"name": "mute", "description": "Mutes a player", "usage": "/mute <player>", "group": "players"},
    {"name": "unmute", "description": "Unmutes a player", "usage": "/unmute <player>", "group": "players"},
    {"name": "tp", "description": "Teleports to a player or location", "usage": "/tp <player|x y>", "group": "players"},
    {"name": "tphere", "description": "Teleports a player to you", "usage": "/tphere <player>", "group": "players"},
    {"name": "tpnpc", "description": "Teleports to an NPC", "usage": "/tpnpc <npc>", "group": "players"},
    {"name": "tppos", "description": "Teleports to tile coordinates", "usage": "/tppos <x> <y>", "group": "players"},
    {"name": "who", "description": "Lists online players", "usage": "/who [player]", "group": "players"},
    {"name": "playing", "description": "Lists online players (alias)", "usage": "/playing", "group": "players"},
    {"name": "forcehalloween", "description": "Toggles forced Halloween mode", "usage": "/forcehalloween", "group": "players"},
    {"name": "forcexmas", "description": "Toggles forced Christmas mode", "usage": "/forcexmas", "group": "players"},
    {"name": "heal", "description": "Heals a player", "usage": "/heal [player]", "group": "players"},
    {"name": "buff", "description": "Gives a buff to a player", "usage": "/buff <player> <buff id> [time]", "group": "players"},
    {"name": "give", "description": "Gives items to a player", "usage": "/give <item> <player> [stack] [prefix]", "group": "players"},
    {"name": "item", "description": "Gives items to yourself", "usage": "/item <item> [stack] [prefix]", "group": "players"},
    {"name": "slap", "description": "Slaps a player for damage", "usage": "/slap <player> [damage]", "group": "players"},
    {"name": "kill", "description": "Kills a player", "usage": "/kill <player>", "group": "players"},
    {"name": "sudo", "description": "Makes a player run a command", "usage": "/sudo <player> <command>", "group": "players"},
    # Groups / permissions
    {"name": "group", "description": "Manages groups", "usage": "/group <add|del|addperm|delperm|list|perm> ...", "group": "groups"},
    {"name": "addgroup", "description": "Adds a group", "usage": "/addgroup <group> [permissions]", "group": "groups"},
    {"name": "delgroup", "description": "Deletes a group", "usage": "/delgroup <group>", "group": "groups"},
    {"name": "addgroupperms", "description": "Adds permissions to a group", "usage": "/addgroupperms <group> <perm> [...]", "group": "groups"},
    {"name": "delgroupperms", "description": "Removes permissions from a group", "usage": "/delgroupperms <group> <perm> [...]", "group": "groups"},
    {"name": "listgroups", "description": "Lists all groups", "usage": "/listgroups", "group": "groups"},
    {"name": "usergroup", "description": "Changes a user's group", "usage": "/usergroup <player> <group>", "group": "groups"},
    # World management
    {"name": "time", "description": "Sets or shows the world time", "usage": "/time [day|night|dusk|noon|hh:mm]", "group": "world"},
    {"name": "dawn", "description": "Sets time to dawn", "usage": "/dawn", "group": "world"},
    {"name": "noon", "description": "Sets time to noon", "usage": "/noon", "group": "world"},
    {"name": "dusk", "description": "Sets time to dusk", "usage": "/dusk", "group": "world"},
    {"name": "midnight", "description": "Sets time to midnight", "usage": "/midnight", "group": "world"},
    {"name": "rain", "description": "Toggles or controls rain", "usage": "/rain [slime|blood|stop|<seconds>]", "group": "world"},
    {"name": "wind", "description": "Sets wind speed", "usage": "/wind <speed>", "group": "world"},
    {"name": "hardmode", "description": "Toggles hardmode", "usage": "/hardmode", "group": "world"},
    {"name": "dropmeteor", "description": "Drops a meteor", "usage": "/dropmeteor", "group": "world"},
    {"name": "star", "description": "Spawns a star", "usage": "/star", "group": "world"},
    {"name": "fullmoon", "description": "Starts a full moon event", "usage": "/fullmoon", "group": "world"},
    {"name": "bloodmoon", "description": "Starts a blood moon event", "usage": "/bloodmoon", "group": "world"},
    {"name": "eclipse", "description": "Starts a solar eclipse event", "usage": "/eclipse", "group": "world"},
    {"name": "invade", "description": "Starts an invasion event", "usage": "/invade [goblin|frost|pirate|martian|pumpkin|frost]", "group": "world"},
    {"name": "stopevent", "description": "Stops the current invasion/event", "usage": "/stopevent", "group": "world"},
    {"name": "spawnboss", "description": "Spawns a boss", "usage": "/spawnboss <boss name>", "group": "world"},
    {"name": "spawnmob", "description": "Spawns a mob", "usage": "/spawnmob <mob> [count]", "group": "world"},
    {"name": "grow", "description": "Grows trees or plants", "usage": "/grow [tree|cactus|herb|pumpkin]", "group": "world"},
    {"name": "settle", "description": "Settles liquids", "usage": "/settle", "group": "world"},
    {"name": "tile", "description": "Places a tile at coordinates", "usage": "/tile <x> <y> <tile id>", "group": "world"},
    {"name": "wall", "description": "Places a wall at coordinates", "usage": "/wall <x> <y> <wall id>", "group": "world"},
    {"name": "protectregion", "description": "Protects a region", "usage": "/protectregion <name>", "group": "world"},
    # Regions
    {"name": "region", "description": "Manages regions", "usage": "/region <define|protect|delete|list|info|...> ...", "group": "regions"},
    # Warps
    {"name": "warp", "description": "Teleports to a warp point", "usage": "/warp <name>", "group": "warps"},
    {"name": "setwarp", "description": "Creates a warp point", "usage": "/setwarp <name>", "group": "warps"},
    {"name": "delwarp", "description": "Deletes a warp point", "usage": "/delwarp <name>", "group": "warps"},
    {"name": "listwarps", "description": "Lists all warp points", "usage": "/listwarps", "group": "warps"},
    # User accounts
    {"name": "user", "description": "Manages user accounts", "usage": "/user <add|del|password|group|list> ...", "group": "accounts"},
    {"name": "register", "description": "Registers an account", "usage": "/register <password>", "group": "accounts"},
    {"name": "login", "description": "Logs into an account", "usage": "/login <password>", "group": "accounts"},
    {"name": "logout", "description": "Logs out of an account", "usage": "/logout", "group": "accounts"},
    {"name": "password", "description": "Changes account password", "usage": "/password <old> <new>", "group": "accounts"},
    {"name": "accountinfo", "description": "Shows account info", "usage": "/accountinfo [player]", "group": "accounts"},
    # Plugins / config
    {"name": "aliases", "description": "Lists command aliases", "usage": "/aliases [command]", "group": "misc"},
    {"name": "help", "description": "Lists commands or shows help for a command", "usage": "/help [command]", "group": "misc"},
    {"name": "search", "description": "Searches for items, NPCs, or tiles", "usage": "/search <type> <query>", "group": "misc"},
    {"name": "clear", "description": "Clears items or projectiles", "usage": "/clear <item|npc|projectile> [radius]", "group": "misc"},
    {"name": "butcher", "description": "Kills all hostile NPCs", "usage": "/butcher [radius]", "group": "misc"},
    {"name": "npccount", "description": "Shows NPC counts", "usage": "/npccount", "group": "misc"},
    {"name": "pvp", "description": "Toggles PvP for a player", "usage": "/pvp [player]", "group": "misc"},
    {"name": "team", "description": "Sets a player's team", "usage": "/team <none|red|green|blue|yellow|pink>", "group": "misc"},
    {"name": "annoy", "description": "Annoys a player (fires at them)", "usage": "/annoy <player>", "group": "misc"},
    {"name": "confuse", "description": "Confuses a player", "usage": "/confuse <player>", "group": "misc"},
    {"name": "rocket", "description": "Rockets a player upward", "usage": "/rocket <player>", "group": "misc"},
    {"name": "firework", "description": "Shoots fireworks at a player", "usage": "/firework <player>", "group": "misc"},
    {"name": "serverinfo", "description": "Shows detailed server info", "usage": "/serverinfo", "group": "misc"},
    {"name": "showpos", "description": "Shows a player's position", "usage": "/showpos [player]", "group": "misc"},
    {"name": "pos", "description": "Shows your position", "usage": "/pos", "group": "misc"},
    {"name": "logs", "description": "Shows recent server logs", "usage": "/logs [count]", "group": "misc"},
    {"name": "inspect", "description": "Toggles tile inspection mode", "usage": "/inspect", "group": "misc"},
    {"name": "kick", "description": "Kicks a player", "usage": "/kick <player> [reason]", "group": "players"},
]
