import discord
from discord.ext import commands
from discord import app_commands
import requests

TOKEN = '9f1c4a5dd259b3d19f8b3597c591e9feb3833cc844b5b6d53abb6448d52fe59a'
NAVER_CLIENT_ID = 'zgcf515ajs'
NAVER_CLIENT_SECRET = 'XLMzx6WyeG5m7GaUuCkJBHU3pdWi8aVs6AFZq7IW'

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
user_lang_prefs = {}  # 유저별 번역 언어 설정 저장 (ex: {'123456': 'en'})

def detect_language(text):
    url = "https://openapi.naver.com/v1/papago/detectLangs"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    data = {"query": text}
    response = requests.post(url, headers=headers, data=data)
    return response.json()['lang']

def translate(text, source, target):
    url = "https://openapi.naver.com/v1/papago/n2mt"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    data = {
        "source": source,
        "target": target,
        "text": text
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()['message']['result']['translatedText']

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"[봇 작동 중] {bot.user}")

# ✅ (1) 슬래시 명령어 번역
@bot.tree.command(name="translate", description="입력한 문장을 번역합니다.")
@app_commands.describe(text="번역할 문장")
async def translate_slash(interaction: discord.Interaction, text: str):
    user_id = str(interaction.user.id)
    src_lang = detect_language(text)
    target_lang = user_lang_prefs.get(user_id, 'ko' if src_lang != 'ko' else 'en')
    translated = translate(text, src_lang, target_lang)
    await interaction.response.send_message(f"🌐 [{src_lang} → {target_lang}] 번역: {translated}")

# ✅ (2) 언어 설정 명령어
@bot.tree.command(name="setlang", description="내 번역 대상 언어를 설정합니다.")
@app_commands.describe(language="예: ko, en, ja, zh-CN")
async def setlang(interaction: discord.Interaction, language: str):
    user_lang_prefs[str(interaction.user.id)] = language
    await interaction.response.send_message(f"✅ 번역 언어가 `{language}`(으)로 설정되었습니다.")

# ✅ (3) 반응 이모지로 번역
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot or str(reaction.emoji) != "🌐":
        return

    msg = reaction.message
    src_lang = detect_language(msg.content)
    target_lang = user_lang_prefs.get(str(user.id), 'ko' if src_lang != 'ko' else 'en')

    try:
        translated = translate(msg.content, src_lang, target_lang)
        await msg.channel.send(f"🌐 <@{user.id}> 요청: [{src_lang} → {target_lang}] {translated}")
    except Exception as e:
        await msg.channel.send("❌ 번역 실패")

bot.run(TOKEN)
