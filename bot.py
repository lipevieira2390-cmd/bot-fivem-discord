import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import re
from discord.ui import View, Button

# ---------- CONFIGURAÇÃO ----------
import os
import os
TOKEN = os.getenv("TOKEN")
SERVER_IP = "novafenixrp.com"
SERVER_PORT = 30120
CHANNEL_ID = 1448536032353190032  # ID do canal do Discord
LOGO_URL = "https://cdn.discordapp.com/attachments/1417642877282160742/1417971423162404994/raw.png?ex=693bd30b&is=693a818b&hm=ea131e5d8908867448ff621f1032a608f702d0b05376c9cde8ef26af29284ed8&"  # Logotipo do servidor

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- FUNÇÃO PARA LIMPAR CÓDIGOS DE COR ----------
def clean_fivem_name(name):
    """Remove códigos de cores do FiveM como ^1, ^7, etc."""
    return re.sub(r"\^\d", "", name)

# ---------- FUNÇÃO PARA OBTER INFO ----------
async def get_fivem_info():
    url_players = f"http://{SERVER_IP}:{SERVER_PORT}/players.json"
    url_info = f"http://{SERVER_IP}:{SERVER_PORT}/info.json"

    async with aiohttp.ClientSession() as session:
        try:
            # players.json
            async with session.get(url_players, timeout=10) as resp_players:
                text = await resp_players.text()
                try:
                    players = json.loads(text)
                except:
                    players = []

            # info.json
            try:
                async with session.get(url_info, timeout=10) as resp_info:
                    text_info = await resp_info.text()
                    try:
                        server_info = json.loads(text_info)
                        max_players = server_info.get("vars", {}).get("sv_maxClients", "??")
                        server_name = server_info.get("vars", {}).get("sv_projectName", "Servidor FiveM")
                    except:
                        max_players = "??"
                        server_name = "Servidor FiveM"
            except:
                max_players = "??"
                server_name = "Servidor FiveM"

            return {
                "online": True,
                "players": len(players),
                "max_players": max_players,
                "servername": server_name
            }

        except Exception as e:
            print("Erro ao obter info do FiveM:", e)
            return {"online": False}

# ---------- FUNÇÃO PARA CRIAR EMBED ----------
def create_embed(data):
    if not data["online"]:
        embed = discord.Embed(
            title="Status do Servidor FiveM",
            description="🚫 O servidor está offline!",
            color=0xff0000
        )
    else:
        server_name_clean = clean_fivem_name(data['servername'])
        embed = discord.Embed(
            title=server_name_clean,
            description="🌟 Bem-vindo ao servidor Nova Fénix RP! 🌟",
            color=0x00ff00
        )
        # Apenas o IP/Host
        embed.add_field(name="IP", value=f"{SERVER_IP}", inline=True)
        embed.add_field(name="Players Online", value=f"{data['players']}/{data['max_players']}", inline=True)
        embed.add_field(name="Slots", value=data['max_players'], inline=True)
        
        embed.set_footer(text="Dados atualizados automaticamente")
        embed.set_thumbnail(url=LOGO_URL)  # Imagem pequena ao lado direito
        embed.set_image(url=LOGO_URL)      # Imagem grande embaixo

    return embed
from discord.ui import View, Button

class ServerButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

        # 🔶 Botão Conectar
        self.add_item(Button(
            label="Conectar",
            emoji="<:fivemlogo:1287509960003162163>",
            url="fivem://connect/novafenixrp.com:30120"
        ))

        # 💎 Botão Loja
        self.add_item(Button(
            label="Loja",
            emoji="💎",
            url=" https://loja.novafenixrp.com/"
        ))

# ---------- LOOP DE ATUALIZAÇÃO ----------
async def update_status():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("Canal não encontrado!")
        return

    data = await get_fivem_info()

    await channel.send(
        embed=create_embed(data),
        view=ServerButtons()
    )

# ---------- EVENTO READY ----------
@bot.event
async def on_ready():
    print(f"Bot ligado como {bot.user}")
    await update_status()

bot.run(TOKEN)
