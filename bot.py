import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import aiohttp
import re
import os

# ---------- CONFIGURAÇÃO ----------
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1448536032353190032
LOGO_URL = "https://cdn.discordapp.com/attachments/1417642877282160742/1417971423162404994/raw.png"

# Código do servidor FiveM
FIVEM_CODE = "vrz95q"

# ---------- INTENTS ----------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- LIMPAR CORES DO FIVEM ----------
def clean_fivem_name(name):
    return re.sub(r"\^\d", "", name)

# ---------- OBTER INFO DO SERVIDOR (API OFICIAL) ----------
async def get_fivem_info():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://servers-frontend.fivem.net/api/servers/single/{FIVEM_CODE}"
            ) as resp:

                data = await resp.json()
                server = data["Data"]

                players = max(
                    server.get("clients", 0),
                    server.get("selfReportedClients", 0)
                )

                return {
                    "online": True,
                    "players": players,
                    "max_players": server["svMaxclients"],
                    "servername": clean_fivem_name(server["hostname"])
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
            url=f"https://cfx.re/join/{FIVEM_CODE}"
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
        title=data["servername"],
        description="🟢 **Servidor Online**",
        color=0xff0000  # Barra vermelha lateral
    )

    embed.add_field(
        name="👥 Players Online",
        value=f"{data['players']}/{data['max_players']}",
        inline=False
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=LOGO_URL)

    embed.set_footer(
        text="Atualiza automaticamente a cada 60 segundos"
    )

    return embed

# ---------- LOOP DE ATUALIZAÇÃO ----------
@tasks.loop(seconds=60)
async def update_status():
    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
        data = await get_fivem_info()
        embed = create_embed(data)

        # Procurar mensagem já enviada pelo bot
        async for message in channel.history(limit=10):
            if message.author == bot.user:
                await message.edit(embed=embed, view=ServerButtons())
                print("Mensagem atualizada com sucesso")
                return

        # Se não existir, cria nova
        await channel.send(embed=embed, view=ServerButtons())
        print("Nova mensagem criada")

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
