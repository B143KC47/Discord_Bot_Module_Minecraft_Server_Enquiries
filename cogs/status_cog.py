# cogs/status_cog.py
import discord
from discord.ext import commands
from discord import app_commands, Embed, Color
import socket
import re
from datetime import datetime
import traceback

from mcstatus import JavaServer
# Use the utility for loading config
from utils.config_loader import load_server_configs, get_validation_warnings

QUERY_TIMEOUT = 5

class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Status Cog loaded.")

    @app_commands.command(name="ip", description="Query and display the status of configured Minecraft servers.")
    async def show_server_status(self, interaction: discord.Interaction):
        """Reads server_info.json, queries server status, and displays it."""
        await interaction.response.defer(thinking=True, ephemeral=False)

        server_embed = Embed(
            title="<:glass:1356630975949443273>  Minecraft Server Status",
            description="Loading configurations and querying servers...",
            color=Color.blue()
        )
        server_embed.set_footer(text=f"Query Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        server_configs = []
        config_load_error = None
        validation_warnings = []

        # 1. Load Configurations using the utility
        try:
            server_configs = load_server_configs()
            # Retrieve any validation warnings found during loading
            validation_warnings = get_validation_warnings(server_configs)
        except (FileNotFoundError, json.JSONDecodeError, TypeError, IOError) as e:
            config_load_error = f"Error loading or parsing configuration: {e}"
        except Exception as e:
            config_load_error = f"An unexpected error occurred while loading configuration: {e}"
            print(f"Unexpected config load error: {e}")
            traceback.print_exc()

        if config_load_error:
            server_embed.description = config_load_error
            server_embed.color = Color.red()
            await interaction.followup.send(embed=server_embed)
            return

        if not server_configs and not validation_warnings:
             server_embed.description = f"No valid server configurations found in the configuration file."
             server_embed.color = Color.orange()
             await interaction.followup.send(embed=server_embed)
             return

        # 2. Query Servers
        servers_processed = 0
        servers_online = 0
        status_description = "Live status of the configured servers:"
        if validation_warnings:
            status_description += "\n\n**Configuration Warnings:**\n" + "\n".join(f"- {w}" for w in validation_warnings)

        server_embed.description = status_description # Update description

        for server_config in server_configs:
            servers_processed += 1
            ip_address = server_config["ip"]
            server_name = server_config["Name"]
            print(f"Querying status for: {server_name} ({ip_address})")

            status_str = "🔴 Offline"
            players_str = "N/A"
            latency_str = "N/A"
            version_str = "Unknown"
            motd_str = ""

            try:
                # Use await for async lookup and status
                server = await JavaServer.async_lookup(ip_address, timeout=QUERY_TIMEOUT)
                status = await server.async_status()

                status_str = "🟢 Online"
                players_str = f"{status.players.online}/{status.players.max}"
                latency_str = f"{status.latency:.2f} ms"
                version_str = status.version.name
                # Clean and format MOTD
                cleaned_motd = discord.utils.escape_markdown(re.sub(r'§[0-9a-fk-or]', '', status.description))
                motd_str = f"\n`{cleaned_motd}`" if cleaned_motd else ""
                servers_online += 1

            except socket.timeout:
                print(f"Query timed out for {server_name} ({ip_address})")
                status_str = "🟡 Timeout"
            except ConnectionRefusedError:
                print(f"Connection refused for {server_name} ({ip_address})")
                status_str = "🔴 Refused"
            except socket.gaierror:
                print(f"Address resolution error for {server_name} ({ip_address})")
                status_str = "❓ Invalid Address"
            except Exception as e:
                # Handle common mcstatus protocol errors more gracefully
                if "invalid literal for int() with base 10" in str(e) or "unpack requires" in str(e) or "received 0 bytes" in str(e):
                    print(f"Server response format error for {server_name} ({ip_address}): {e}")
                    status_str = "❓ Bad Response"
                else:
                    print(f"Unknown error querying {server_name} ({ip_address}): {e}")
                    status_str = "❓ Query Error"
                    traceback.print_exc()

            # Build field value
            field_value = (
                f"**Status:** {status_str} | **Players:** {players_str}\n"
                f"**Latency:** {latency_str} | **Version:** {version_str}\n"
                f"**Address:** `{ip_address}`{motd_str}"
            )
            server_embed.add_field(name=f"{server_name}", value=field_value, inline=False)

        # Adjust Embed color based on results
        if servers_processed == 0 and validation_warnings: # Only warnings, no valid servers
             server_embed.color = Color.orange()
        elif servers_online == servers_processed and servers_processed > 0:
            server_embed.color = Color.green()
        elif servers_online > 0:
            server_embed.color = Color.gold()
        elif servers_processed > 0: # Processed some, but none online
            server_embed.color = Color.red()
        # else: Keep blue if no servers were processed and no warnings

        # Send the final result
        await interaction.followup.send(embed=server_embed)

# Setup function for loading the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))