import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import aiohttp
import json
import re
import os

# ---------- CONFIGURAÇÃO ----------
TOKEN = os.getenv("TOKEN")
SERVER_IP = "novafenixrp.com"
SERVER_PORT = 30120
CHANNEL_ID = 1448536032353190032
LOGO_URL = "https://cdn.discordapp.com/attachments/1417642877282160742/1417971423162404994/raw.png"

# ---------- INTENTS ----------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- LIMPAR CORES DO FIVEM ----------
def clean_fivem_name(name):
    return re.sub(r"\^\d", "", name)

# ---------- OBTER INFO DO SERVIDOR ----------
async def get_fivem_info():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://servers-frontend.fivem.net/api/servers/single/vrz95q"
            ) as resp:

                data = await resp.json()
                server = data["Data"]

                return {
                    "online": server["clients"] is not None,
                    "players": server["clients"],
                    "max_players": server["svMaxclients"],
                    "servername": server["hostname"]
                }

    except Exception as e:
        print("Erro API FiveM:", e)
        return {"online": False}

# ---------- BOTÕES ----------
class ServerButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(
            label="Conectar",
            emoji="<:fivemlogo:1287509960003162163>",
            url="https://servers.fivem.net/servers/detail/vrz95q"
        ))

        self.add_item(Button(
            label="Loja",
            emoji="💎",
            url="https://loja.novafenixrp.com/"
        ))

# ---------- CRIAR EMBED ----------
def create_embed(data):
    if not data["online"]:
        embed = discord.Embed(
            title="Nova Fénix RP",
            description="🔴 **Servidor Offline**",
            color=0xff0000
        )
        return embed

    embed = discord.Embed(
        title="Nova Fénix RP",
        description="🟢 **Servidor Online**",
        color=0xff0000  # Barra lateral vermelha
    )

    embed.add_field(
        name="👥 Players Online",
        value=f"{data['players']}/{data['max_players']}",
        inline=False
    )

    embed.add_field(
        name="🌐 IP",
        value="novafenixrp.com",
        inline=False
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=LOGO_URL)

    embed.set_footer(
        text="Atualiza automaticamente a cada 60 segundos"
    )

    return embed

# ---------- VARIÁVEL GLOBAL ----------
status_message = None

# ---------- LOOP DE ATUALIZAÇÃO ----------
@tasks.loop(seconds=60)
async def update_status():
    global status_message

    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
        data = await get_fivem_info()
        embed = create_embed(data)

        if status_message is None:
            status_message = await channel.send(
                embed=embed,
                view=ServerButtons()
            )
        else:
            await status_message.edit(
                embed=embed,
                view=ServerButtons()
            )

        print("Mensagem atualizada com sucesso")

    except Exception as e:
        print("ERRO:", e)

@update_status.before_loop
async def before_update():
    await bot.wait_until_ready()

# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"Bot ligado como {bot.user}")
    update_status.start()

bot.run(TOKEN)
