import discord
from discord.ext import tasks
import asyncio
import datetime

import config

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

# user_id → category info
active_categories = {}  


async def create_user_category(username: str):
    guild = client.get_guild(config.DISCORD_GUILD_ID)

    # Создаем категорию
    category = await guild.create_category(name=f"TG - {username}")
    # Создаем текстовый канал
    channel = await guild.create_text_channel(name=username, category=category)

    # Запланировать удаление через 24 часа
    async def delete_after_delay():
        await asyncio.sleep(24 * 60 * 60)
        await category.delete()

    asyncio.create_task(delete_after_delay())

    return category, channel


async def send_to_discord(username: str, message: str):
    # Если категории нет — создаём
    if username not in active_categories:
        category, channel = await create_user_category(username)
        active_categories[username] = channel
    else:
        channel = active_categories[username]

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await channel.send(f"**{username}** ({now}):\n{message}")


async def start_discord():
    await client.start(config.DISCORD_TOKEN)
