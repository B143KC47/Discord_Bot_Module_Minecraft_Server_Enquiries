# Discord Minecraft Server Enquiry Bot

A Discord bot module for querying Minecraft server status and player information.

[中文文档](README.CN.md) | English

![Discord Bot](https://img.shields.io/badge/Discord-Bot-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Minecraft](https://img.shields.io/badge/Minecraft-62B47A?style=for-the-badge&logo=minecraft&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Features
- ✅ Check Minecraft server status (online/offline)
- 👥 Get player count and list
- 📊 Query server version and MOTD
- 🔄 Support for multiple Minecraft servers
- 💬 Clean Discord embed messages

## Requirements
- Python 3.8+
- Discord bot token
- Minecraft server address(es)

## Installation
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your settings
4. Configure your Minecraft server(s) in `server_info.json`
5. Run the bot: `python main.py`

## Configuration

### Discord Bot Setup
Edit `.env` file with your:
- `DISCORD_TOKEN`: Your Discord bot token
- `TEST_GUILD_ID`: (Optional) Guild ID for testing/development

### Minecraft Server Setup
Edit `server_info.json` with your server information:
```json
[ 
  {"ip":"play.example.com", "Name": "My Minecraft Server"},
  {"ip":"mc.example.org", "Name": "Another MC Server"}
]
```

## Commands
- `/ip`: Display status of all configured Minecraft servers

## Project Structure
```
├── main.py              # Bot initialization
├── cogs/
│   └── status_cog.py    # Server status command implementation
├── utils/
│   └── config_loader.py # Configuration utilities
├── server_info.json     # Server configuration
└── .env                 # Environment variables
```

## Support
For issues or feature requests, please open an issue on GitHub.

## License
MIT