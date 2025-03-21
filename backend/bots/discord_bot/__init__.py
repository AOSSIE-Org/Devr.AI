import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
PERMISSIONS = 8

CONFIG_FILE = "server_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

def get_prefix(bot, message):
    """Get prefix for each server"""
    if message.guild:
        guild_id = str(message.guild.id)
        return config.get(guild_id, {}).get("prefix", "!")
    return "!" 

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="invite")
async def invite(ctx):
    """Send the OAuth2 invite link"""
    oauth_url = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions={PERMISSIONS}&scope=bot%20applications.commands"
    await ctx.send(f"Click here to invite me to your server: {oauth_url}")

@bot.command(name="setprefix")
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix: str):
    """Change bot command prefix for the server"""
    guild_id = str(ctx.guild.id)
    if guild_id not in config:
        config[guild_id] = {}
    config[guild_id]["prefix"] = new_prefix
    save_config(config)
    await ctx.send(f"Prefix changed to: `{new_prefix}`")

@bot.event
async def on_guild_join(guild):
    """Handle when the bot joins a new server"""
    owner = guild.owner
    if owner:
        await owner.send(f"Thanks for adding me to {guild.name}! Use `{config.get(str(guild.id), {}).get('prefix', '!')}help` to see my commands.")

CONFIG_FILE = "role_config.json"

def load_roles():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_roles(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

role_config = load_roles()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="setrole")
@commands.has_permissions(administrator=True)
async def setrole(ctx, role: discord.Role, command: str):
    """Assign a role that can execute a command"""
    guild_id = str(ctx.guild.id)

    if guild_id not in role_config:
        role_config[guild_id] = {}

    role_config[guild_id][command] = role.id
    save_roles(role_config)
    await ctx.send(f"Role `{role.name}` can now use `{command}` command!")

def has_required_role(command_name):
    async def predicate(ctx):
        guild_id = str(ctx.guild.id)
        if guild_id in role_config and command_name in role_config[guild_id]:
            role_id = role_config[guild_id][command_name]
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role in ctx.author.roles:
                return True
            await ctx.send("You don't have permission to use this command!")
            return False
        return True  
    return commands.check(predicate)

@bot.command(name="secret")
@has_required_role("secret")
async def secret(ctx):
    """Restricted command only for specific roles"""
    await ctx.send("This is a secret command!")

if __name__ == "__main__":
    bot.run(TOKEN)


if __name__ == "__main__":
    bot.run(TOKEN)
