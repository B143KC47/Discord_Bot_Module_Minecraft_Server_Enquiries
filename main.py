# main.py
import discord
from discord.ext import commands
from discord import app_commands, Interaction # Ensure Interaction is imported
import os
import asyncio # Required for loading extensions
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Bot Setup ---
intents = discord.Intents.default()
# intents.message_content = True # Add if you need message content intent later
# intents.members = True      # Add if you need member intent later

bot = commands.Bot(command_prefix='!', intents=intents) # Prefix is less relevant for slash commands

# --- Bot Events ---
@bot.event
async def on_ready():
    print(f'{bot.user.name} (ID: {bot.user.id}) has connected to Discord!')
    print(f'Using Intents: {bot.intents}')
    
    # 在bot准备就绪后同步命令
    print("Syncing commands...")
    try:
        await sync_commands()
    except Exception as e:
        print(f"Error syncing commands: {e}")
    
    print('------')


# --- Generic Error Handler (Mostly unchanged) ---
# This handles errors from *any* app command across all cogs
@bot.tree.error
async def on_app_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    """Handles errors specifically from slash commands."""
    error_message = "An unknown error occurred while executing the command."
    log_error = True
    ephemeral_msg = True # Send error messages privately by default

    # Nicer error messages based on error type
    if isinstance(error, app_commands.errors.MissingPermissions):
        missing_perms = ", ".join(error.missing_permissions)
        error_message = f"❌ You lack the required permissions: `{missing_perms}`."
        log_error = False
    elif isinstance(error, app_commands.errors.CommandNotFound):
        error_message = "🤔 Command not found. It might be syncing or removed."
        log_error = False
    elif isinstance(error, app_commands.errors.CommandInvokeError):
        original = error.original
        print(f"Error invoking command '{interaction.command.name if interaction.command else 'unknown'}':")
        traceback.print_exception(type(original), original, original.__traceback__)
        if isinstance(original, discord.Forbidden):
            error_message = f"❌ Bot lacks permissions for this action ({type(original).__name__}). Check its roles."
        elif isinstance(original, discord.HTTPException):
            error_message = f"Network error communicating with Discord ({original.status} - {original.code}). Try again later."
        # Catch specific RCON/Socket errors if they bubble up this far (should be caught in cog)
        elif isinstance(original, (socket.timeout, ConnectionRefusedError, MCRconException, socket.gaierror)):
             error_message = f"⚙️ Failed to communicate with the Minecraft server ({type(original).__name__}). Check server status and RCON config."
        else:
            error_message = f"⚙️ An internal error occurred: {type(original).__name__}. Check console logs."
    elif isinstance(error, app_commands.errors.CheckFailure):
        error_message = "🚫 You don't meet the conditions to use this command."
        log_error = False
    elif isinstance(error, app_commands.errors.TransformerError):
        error_message = f"Parameter error: Invalid value '{error.value}' for '{error.param.name}' ({type(error.original).__name__})."
    elif isinstance(error, app_commands.errors.CommandOnCooldown):
        error_message = f"⏳ Command on cooldown. Try again in {error.retry_after:.2f} seconds."
        log_error = False
        ephemeral_msg = False # Cooldown messages often shown publicly
    else:
        error_message = f"An unhandled error occurred: {type(error).__name__}"

    if log_error:
        print(f"Unhandled App Command Error ({type(error).__name__}): {error}")
        # Optionally print full traceback for unhandled ones
        # traceback.print_exception(type(error), error, error.__traceback__)

    # Try to send the error message
    try:
        # Use followup if the interaction was deferred, otherwise response.send_message
        if interaction.response.is_done():
            await interaction.followup.send(error_message, ephemeral=ephemeral_msg)
        else:
            await interaction.response.send_message(error_message, ephemeral=ephemeral_msg)
    except discord.InteractionResponded:
         print(f"Error: Could not send error message to {interaction.user} (Interaction already responded). Message: {error_message}")
    except discord.HTTPException as e:
        print(f"Error: Failed to send error message via Discord API: {e}")
    except Exception as e:
         print(f"Error: Unexpected exception while sending error message: {e}")


# --- Startup Logic ---
async def load_extensions():
    """Loads all cogs from the 'cogs' directory."""
    print("Loading extensions...")
    cogs_loaded = 0
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            extension = f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(extension)
                print(f'Successfully loaded extension: {extension}')
                cogs_loaded += 1
            except commands.ExtensionNotFound:
                print(f'Error: Extension {extension} not found.')
            except commands.ExtensionAlreadyLoaded:
                print(f'Warning: Extension {extension} already loaded.')
            except commands.NoEntryPointError:
                print(f'Error: Extension {extension} has no setup() function.')
            except commands.ExtensionFailed as e:
                print(f'Error: Extension {extension} failed to load.')
                traceback.print_exception(type(e.original), e.original, e.original.__traceback__)
            except Exception as e:
                 print(f'Error: An unexpected error occurred loading {extension}:')
                 traceback.print_exc()
    print(f"Finished loading extensions. {cogs_loaded} cogs loaded.")


async def sync_commands():
    """Syncs application commands."""
    print("Syncing application commands...")
    try:
        test_guild_id = os.getenv("TEST_GUILD_ID")
        if test_guild_id:
            try:
                test_guild_id = int(test_guild_id)
                guild = discord.Object(id=test_guild_id)
                bot.tree.copy_global_to(guild=guild) # Optional: copy global commands to guild
                synced = await bot.tree.sync(guild=guild)
                print(f'Synced {len(synced)} commands to test guild {test_guild_id}!')
            except (ValueError, discord.NotFound):
                print("Warning: TEST_GUILD_ID is invalid or guild not found. Falling back to global sync.")
                synced = await bot.tree.sync()
                print(f'Synced {len(synced)} commands globally (may take time to update)!')
            except discord.HTTPException as e:
                 print(f"Error syncing commands to guild {test_guild_id}: {e}")
                 print("Attempting global sync as fallback...")
                 synced = await bot.tree.sync()
                 print(f'Synced {len(synced)} commands globally (may take time to update)!')

        else:
            print("No TEST_GUILD_ID found. Syncing commands globally...")
            synced = await bot.tree.sync()
            print(f'Synced {len(synced)} commands globally (may take time to update)!')

    except discord.HTTPException as e:
        print(f"Error syncing commands globally: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during command sync: {e}")
        traceback.print_exc()


async def main():
    """Main asynchronous function to setup and run the bot."""
    discord.utils.setup_logging() # Setup basic logging for discord.py

    async with bot:
        # Load extensions first
        await load_extensions()

        # Get token AFTER loading extensions
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("CRITICAL ERROR: DISCORD_TOKEN not found in .env file or environment variables.")
            return

        print("Starting bot...")
        try:
            # 直接启动bot，让sync_commands在on_ready中执行
            await bot.start(token)
        except discord.LoginFailure:
            print("\n" + "="*60)
            print("CRITICAL ERROR: Login Failed - Invalid Token!")
            print("Please check your DISCORD_TOKEN in the .env file.")
            print("="*60 + "\n")
        except discord.PrivilegedIntentsRequired:
            print("\n" + "="*60)
            print("CRITICAL ERROR: Privileged Intents Required!")
            print("Your bot needs certain intents enabled in the Discord Developer Portal:")
            print("- Check SERVER MEMBERS INTENT and MESSAGE CONTENT INTENT if you plan to use features needing them.")
            print("Currently enabled intents:", bot.intents)
            print("="*60 + "\n")
        except Exception as e:
            print(f"\nCRITICAL ERROR: An unexpected error occurred during bot execution:")
            traceback.print_exc()


# --- Run the Bot ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shutdown requested.")
    except Exception as e:
         print(f"Fatal error in main execution block: {e}")
         traceback.print_exc()