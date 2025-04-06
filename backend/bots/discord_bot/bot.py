import discord
from discord.ext import commands
import requests
import os
import wikipediaapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Enable necessary intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"📩 Message received: {message.content}")

    await bot.process_commands(message)  # Allow command processing


@bot.command()
async def ask(ctx, *, question: str):
    """Handles !ask command to fetch AI-generated responses"""
    if not question:
        await ctx.send("❌ Please provide a question after `!ask`.")
        return

    ai_response = get_groq_response(question)

    # If the response is longer than 2000 characters, split it
    if len(ai_response) > 2000:
        for chunk in [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]:
            await ctx.send(chunk)
    else:
        await ctx.send(ai_response)


def retrieve_context(query):
    """Fetches context from Wikipedia based on the query"""
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="EventBusBot/1.0 (Contact: your_email@example.com)"  # Replace with a valid contact
    )
    page = wiki.page(query)

    if page.exists():
        return page.summary[:500]  # Limit context length
    else:
        return None


def get_groq_response(prompt):
    """Retrieves context and sends improved query to Groq API"""
    context = retrieve_context(prompt)  # Fetch relevant knowledge

    final_prompt = f"Context: {context}\n\nUser: {prompt}" if context else prompt

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": final_prompt}]
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ API Error: {response.text}"


bot.run(DISCORD_BOT_TOKEN)
