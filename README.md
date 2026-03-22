# garrison-plugin-terraria

Terraria (TShock) plugin for [Garrison](https://github.com/ProfessorZ/garrison) — a multi-game RCON web dashboard.

## Requirements

- [TShock](https://github.com/Pryaxis/TShock) server with REST API enabled (default port **7878**)
- TShock REST API password configured in `tshock/config.json` (`"RestApiEnabled": true, "RestApiPort": 7878`)

## Connection

Unlike Source RCON games, Terraria uses TShock's HTTP REST API:

| Field    | Value                  |
|----------|------------------------|
| Host     | Server IP / hostname   |
| Port     | `7878` (TShock REST)   |
| Password | TShock REST password   |

## TShock Config

Ensure your `tshock/config.json` has:

```json
{
  "RestApiEnabled": true,
  "RestApiPort": 7878,
  "ApplicationRestTokenPermission": "..."
}
```

## Features

- ✅ Player list
- ✅ Kick player
- ✅ Ban player
- ✅ Server status (name, world, player count, version)
- ✅ Raw command execution (`/v3/server/rawcmd`)

## Auth Flow

```
POST /v2/token/create  { "password": "..." }  →  { "token": "abc123" }
GET  /v2/players/list?token=abc123
GET  /v2/server/status?token=abc123
```
