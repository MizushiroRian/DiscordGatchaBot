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

@bot.tree.command(name="reset", description="すべてのトークテーマをリセットします（管理者専用）")
@app_commands.checks.has_permissions(manage_guild=True)  # 管理者権限を要求
async def reset(interaction: discord.Interaction):
    # 確認メッセージを送信
    await interaction.response.send_message(
        "⚠️ すべてのトークテーマを削除します。この操作は元に戻せません。続行しますか？\n"
        "続行する場合、10秒以内に「はい」と返信してください。",
        ephemeral=True  # 他のユーザーには見えない
    )
    def check(m):
        return m.author == interaction.user and m.content.lower() == "はい" and m.channel == interaction.channel
    try:
        # 10秒以内に「はい」の返信を待つ
        msg = await bot.wait_for('message', check=check, timeout=10.0)
        # データベースをリセット
        c.execute("DELETE FROM themes")
        conn.commit()
        await interaction.followup.send("✅ すべてのトークテーマをリセットしました！", ephemeral=True)
    except:
        await interaction.followup.send("⏰ タイムアウトしました。リセットはキャンセルされました。", ephemeral=True)

# キープアライブサーバーを起動
keep_alive()

# Botトークンを環境変数から取得
bot.run(os.getenv('BOT_TOKEN'))
