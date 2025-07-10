import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3
import os
from keep_alive import keep_alive

# 特権Intentを有効化
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Botを初期化
bot = commands.Bot(command_prefix='/', intents=intents)

# データベース設定
conn = sqlite3.connect('themes.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS themes (theme TEXT, user_id INTEGER)''')

@bot.event
async def on_ready():
    await bot.tree.sync()  # スラッシュコマンドを同期
    print(f'{bot.user} がオンラインになりました！')

@bot.tree.command(name="submit", description="トークテーマを投稿します")
@app_commands.describe(theme="投稿するトークテーマ")
async def submit(interaction: discord.Interaction, theme: str):
    c.execute("INSERT INTO themes VALUES (?, ?)", (theme, interaction.user.id))
    conn.commit()
    await interaction.response.send_message(f"テーマ「{theme}」を投稿しました！")

@bot.tree.command(name="gacha", description="投稿されたテーマからランダムに選びます")
async def gacha(interaction: discord.Interaction):
    c.execute("SELECT theme FROM themes")
    themes = c.fetchall()
    if themes:
        random_theme = random.choice(themes)[0]
        await interaction.response.send_message(f"今日のトークテーマは：**{random_theme}**")
    else:
        await interaction.response.send_message("まだテーマが投稿されていません。")

# キープアライブサーバーを起動
keep_alive()

# Botトークンを環境変数から取得
bot.run(os.getenv('BOT_TOKEN'))
