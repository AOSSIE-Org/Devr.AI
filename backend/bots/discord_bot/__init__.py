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
ROLE_CONFIG_FILE = "role_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

def load_roles():
    if not os.path.exists(ROLE_CONFIG_FILE):
        with open(ROLE_CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(ROLE_CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_roles(config):
    with open(ROLE_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

role_config = load_roles()

def get_prefix(bot, message):
    """Get prefix for each server"""
    if message.guild:
        guild_id = str(message.guild.id)
        return config.get(guild_id, {}).get("prefix", "!")
    return "!"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

def has_required_role(command_name):
    """Check if user has permission to use a command"""
    async def predicate(ctx):
        guild_id = str(ctx.guild.id)
        
        if guild_id not in role_config or command_name not in role_config[guild_id]:
            return False
        
        role_entry = role_config[guild_id][command_name]
        
        if isinstance(role_entry, dict):
            role_id = role_entry.get("role_id")
            is_restricted = role_entry.get("restricted", False)
        else:
            role_id = role_entry
            is_restricted = False
        
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        
        if role and role in ctx.author.roles:
            return True
        
        if is_restricted:
            await ctx.send(f"❌ Only members with the `{role.name if role else 'configured'}` role can use this command!")
            return False
        
        await ctx.send("❌ You don't have permission to use this command!")
        return False
    
    return commands.check(predicate)
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot is in {len(bot.guilds)} servers")

@bot.event
async def on_guild_join(guild):
    """Send welcome message when bot joins a server"""
    owner = guild.owner
    if owner:
        await owner.send(f"Thanks for adding me to {guild.name}! Use `{config.get(str(guild.id), {}).get('prefix', '!')}help` to see my commands.")

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
    await ctx.send(f"✅ Prefix changed to: `{new_prefix}`")

@bot.command(name="setrole")
@commands.has_permissions(administrator=True)
async def setrole(ctx, role: discord.Role, command: str):
    """Assign a role that can execute a command (in addition to admins)"""
    guild_id = str(ctx.guild.id)
    if guild_id not in role_config:
        role_config[guild_id] = {}
    
    role_config[guild_id][command] = role.id
    save_roles(role_config)
    await ctx.send(f"✅ Role `{role.name}` can now use the `{command}` command!")

@bot.command(name="restrictrole")
@commands.has_permissions(administrator=True)
async def restrictrole(ctx, role: discord.Role, command: str):
    """Make a command ONLY usable by members with a specific role (and admins)"""
    guild_id = str(ctx.guild.id)
    if guild_id not in role_config:
        role_config[guild_id] = {}
    
    role_config[guild_id][command] = {"role_id": role.id, "restricted": True}
    save_roles(role_config)
    await ctx.send(f"✅ Command `{command}` restricted! Only admins and members with `{role.name}` role can use it.")

@bot.command(name="viewroles")
@commands.has_permissions(administrator=True)
async def viewroles(ctx):
    """View all role configurations for this server"""
    guild_id = str(ctx.guild.id)
    if guild_id not in role_config or not role_config[guild_id]:
        await ctx.send("❌ No role configurations found for this server.")
        return
    
    embed = discord.Embed(title="Role Command Permissions", color=discord.Color.blue())
    
    for command, role_data in role_config[guild_id].items():
        if isinstance(role_data, dict):
            role_id = role_data.get("role_id")
            is_restricted = role_data.get("restricted", False)
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            status = "Restricted to" if is_restricted else "Allowed for"
        else:
            role = discord.utils.get(ctx.guild.roles, id=role_data)
            status = "Allowed for"
        
        role_name = role.name if role else "Unknown Role"
        embed.add_field(name=f"!{command}", value=f"{status} @{role_name}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="vip")
@commands.check_any(
    commands.has_permissions(administrator=True), 
    has_required_role("vip")                      
)
async def vip(ctx):
    """VIP command that admins can always use, plus assigned roles"""
    await ctx.send("🌟 VIP access granted! Welcome to the exclusive area.")

@bot.command(name="mod")
@commands.check_any(
    commands.has_permissions(administrator=True),
    has_required_role("mod")
)
async def mod(ctx):
    """Moderator command that admins and assigned roles can use"""
    await ctx.send("🛡️ Moderator command executed successfully!")

@bot.command(name="admin")
@commands.has_permissions(administrator=True)
async def admin(ctx):
    """Admin-only command that can't be assigned to roles"""
    await ctx.send("⚙️ Administrative command executed.")

if __name__ == "__main__":
    bot.run(TOKEN)