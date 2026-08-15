import discord, random, os, yt_dlp, asyncio, re, json
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "¡Crustáceo Cascarudo abierto! 🍔"
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["!", ")"], intents=intents)

WELCOME_CHANNEL_ID = 1537139780662329364
CANGRE_CHANNEL_ID = 1537279256281747588
CANGRE_FILE = "cangreburgers.json"
CARNADA_FILE = "carnada.json"
SECRETOS_FILE = "secretos.json"
SECRETOS_USER_FILE = "secretos_user.json"
CONF_CANALES_FILE = "conf_canales.json"
conf_canales = cargar_json(CONF_CANALES_FILE)

def cargar_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return json.load(f)
        except: return {}
    return {}

def guardar_json(path, data):
    with open(path, "w") as f: json.dump(data, f)

carnada_data = cargar_json(CARNADA_FILE)
secretos_data = cargar_json(SECRETOS_FILE)
if "total" not in secretos_data: secretos_data = {"total": 0}
secretos_user = cargar_json(SECRETOS_USER_FILE)

TIENDA = {
    "color_azul": {"nombre": "Color burger azul 🔵", "precio": 100, "rol": "Color burger azul", "tipo": "rol", "color": 0x3498db},
    "color_rosa": {"nombre": "Color burger rosa 🩷", "precio": 100, "rol": "Color burger rosa", "tipo": "rol", "color": 0xff69b4},
    "color_morado": {"nombre": "Color burger morado 🟣", "precio": 100, "rol": "Color burger morado", "tipo": "rol", "color": 0x9b59b6},
    "color_naranja": {"nombre": "Color burger naranja 🟠", "precio": 100, "rol": "Color burger naranja", "tipo": "rol", "color": 0xe67e22},
    "color_verde": {"nombre": "Color burger verde 🟢", "precio": 100, "rol": "Color burger verde", "tipo": "rol", "color": 0x2ecc71},
    "color_roja": {"nombre": "Color burger roja 🔴", "precio": 100, "rol": "Color burger roja", "tipo": "rol", "color": 0xe74c3c},
    "color_amarilla": {"nombre": "Color burger amarilla 🟡", "precio": 100, "rol": "Color burger amarilla", "tipo": "rol", "color": 0xf1c40f},
    "color_negra": {"nombre": "Color burger negra ⚫", "precio": 100, "rol": "Color burger negra", "tipo": "rol", "color": 0x2c3e50},
    "vip_bikini": {"nombre": "VIP Fondo de Bikini 👑", "precio": 500, "rol": "VIP Bikini", "tipo": "rol", "color": 0xffd700},
    "gary": {"nombre": "Gary 🐌", "precio": 800, "rol": "Dueño de Gary 🐌", "tipo": "mascota", "color": 0xffc0cb},
    "gusano": {"nombre": "Gusano Rockero 🪱", "precio": 1200, "rol": "Gusano de Fondo Bikini 🪱", "tipo": "mascota", "color": 0x8b4513},
    "almeja": {"nombre": "Almeja Bebé 🦪", "precio": 600, "rol": "Almeja Bebé 🦪", "tipo": "mascota", "color": 0xadd8e6},
    "medusa": {"nombre": "Medusa Reina 🪼", "precio": 1500, "rol": "Reina de Medusas 🪼", "tipo": "mascota", "color": 0x00ffff},
    "larry": {"nombre": "Larry la Langosta 🦞", "precio": 2000, "rol": "Amigo de Larry 🦞", "tipo": "mascota", "color": 0xff4500},
    "nitro_fake": {"nombre": "Nitro Fake ✨", "precio": 3000, "rol": "✨ Nitro Fake", "tipo": "nitro", "color": 0xff73fa},
}


def cargar():
    if os.path.exists(CANGRE_FILE):
        try:
            with open(CANGRE_FILE, "r") as f:
                data = json.load(f)
                if data and isinstance(list(data.values())[0], dict) and "burgers" in list(data.values())[0]:
                    return {}
                return data
        except: return {}
    return {}

def guardar(data):
    with open(CANGRE_FILE, "w") as f: json.dump(data, f)

cangre_data = cargar()

def get_user_data(gid, uid):
    gid = str(gid)
    uid = str(uid)
    if gid not in cangre_data: cangre_data[gid] = {}
    if uid not in cangre_data[gid]: cangre_data[gid][uid] = {"burgers": 0, "nivel": 0, "mascotas": []}
    if "mascotas" not in cangre_data[gid][uid]: cangre_data[gid][uid]["mascotas"] = []
    return cangre_data[gid][uid]

def add_burgers(gid, uid, cantidad):
    user = get_user_data(gid, uid)
    user["burgers"] += cantidad
    nivel = user["burgers"] // 50
    subio = nivel > user["nivel"]
    user["nivel"] = nivel
    guardar(cangre_data)
    return subio, user

ROL_OWNER = "Bob esponja"
ROL_ADMIN = "Gerente del Crustáceo Cascarudo"
ROLES_MAP = {
    "🔵": "Color burger azul", "🩷": "Color burger rosa",
    "🟣": "Color burger morado", "🟠": "Color burger naranja",
    "🟢": "Color burger verde", "🔴": "Color burger roja",
    "🟡": "Color burger amarilla", "⚫": "Color burger negra",
}
RADIOS = {
    "lofi": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    "bob": "https://www.youtube.com/watch?v=r9L4AseD-aA",
    "fondo": "https://www.youtube.com/watch?v=QtXby3twMmI",
}
YTDL_OPTS_BASE = {
    'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
}

async def crear_roles_automatico(guild):
    me = guild.me
    for key, data in TIENDA.items():
        nombre_rol = data["rol"]
        if not discord.utils.get(guild.roles, name=nombre_rol):
            try:
                await guild.create_role(name=nombre_rol, color=discord.Color(data.get("color", 0x99aab5)), hoist=True, reason="Tienda Crustáceo")
                await asyncio.sleep(0.4)
            except: pass
    for nombre in ["Bob esponja", "NPC", "Gerentes del Crustáceo", "Gerente del Crustáceo Cascarudo"]:
        if not discord.utils.get(guild.roles, name=nombre):
            try:
                col = 0xe67e22 if "Gerente" in nombre else 0xf1c40f if nombre=="NPC" else 0x95a5a6
                await guild.create_role(name=nombre, color=discord.Color(col), hoist=True)
                await asyncio.sleep(0.4)
            except: pass
    try:
        await asyncio.sleep(2)
        orden = ["Gerentes del Crustáceo", "Gerente del Crustáceo Cascarudo", "NPC", "Bob esponja"] + [d["rol"] for d in TIENDA.values()]
        roles_dict = {r.name: r for r in guild.roles}
        pos_base = me.top_role.position - 1
        for nombre_rol in orden:
            rol = roles_dict.get(nombre_rol)
            if rol and rol!= me.top_role and rol.position < pos_base:
                try:
                    await rol.edit(position=pos_base)
                    pos_base -= 1
                    await asyncio.sleep(0.3)
                except: pass
    except: pass

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Listo {bot.user}")
    for guild in bot.guilds:
        try:
            await crear_roles_automatico(guild)
            bot_member = guild.get_member(bot.user.id)
            if bot_member:
                for n in ["Bob esponja", "NPC", "Gerentes del Crustáceo"]:
                    r = discord.utils.get(guild.roles, name=n)
                    if r:
                        try: await bot_member.add_roles(r)
                        except: pass
        except Exception as e:
            print(e)

@bot.event
async def on_member_join(member):
    canal = bot.get_channel(WELCOME_CHANNEL_ID)
    if not canal: return
    embed = discord.Embed(
        title="¡ESTOY LISTOOOOO! 🧽🍍",
        description=f"¡¡Llegó {member.mention} a Fondo de Bikini!! 🎉\n¡Holaaa {member.name}! 💛\n¡Ya somos **{member.guild.member_count}** habitantes! 🥳\n\nUsa `/puntos` para ver tus CangreBurgers 🍔\n¡Bienvenido a BIKINI BOTTOM! 🛟",
        color=0xFFEB3B
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url="attachment://bienvenida.jpg")
    embed.set_footer(text="Fondo de Bikini • ¡Estoy listo!")
    try:
        archivo = discord.File("bienvenida.jpg", filename="bienvenida.jpg")
        await canal.send(content=f"¡¡{member.mention} ESTOY LISTO!! 🧽🛟", embed=embed, file=archivo)
    except Exception as e:
        print(f"Error bienvenida: {e}")
        try:
            await canal.send(content=f"¡¡{member.mention} ESTOY LISTO!! 🧽", embed=embed)
        except: pass

@bot.tree.command(name="puntos", description="Mira tus CangreBurgers 🍔")
async def puntos(interaction: discord.Interaction):
    d = get_user_data(interaction.guild.id, interaction.user.id)
    await interaction.response.send_message(embed=discord.Embed(title="🍔 TUS CANGREBURGERS", description=f"{interaction.user.mention} tienes **{d['burgers']}** 🍔 (Nv {d['nivel']})"), ephemeral=True)

@bot.tree.command(name="top_bikini", description="Top CangreBurgers 🏆")
async def top_bikini(interaction: discord.Interaction):
    gid = str(interaction.guild.id)
    data_guild = cangre_data.get(gid, {})
    if not data_guild: await interaction.response.send_message("Nadie tiene burgers aún 💔"); return
    top = sorted(data_guild.items(), key=lambda x: x[1]["burgers"], reverse=True)[:10]
    desc = "\n".join([f"**{i+1}.** <@{uid}> - {d['burgers']} 🍔 (Nv {d['nivel']})" for i,(uid,d) in enumerate(top)])
    await interaction.response.send_message(embed=discord.Embed(title="🏆 TOP CANGREBURGERS", description=desc, color=0xFFD700))

@bot.tree.command(name="crustaceo_cascarudo", description="Tienda del Crustáceo Cascarudo 🍔")
async def crustaceo_cascarudo(interaction: discord.Interaction):
    desc = "**🎨 COLORES (100 🍔):**\n"
    for k,v in TIENDA.items():
        if v["tipo"]=="rol": desc+=f"`{k}` - {v['nombre']} - {v['precio']} 🍔\n"
    desc+="\n**🐾 MASCOTAS:**\n"
    for k,v in TIENDA.items():
        if v["tipo"]=="mascota": desc+=f"`{k}` - {v['nombre']} - {v['precio']} 🍔\n"
    desc+="\n**✨ ESPECIAL:**\n"
    for k,v in TIENDA.items():
        if v["tipo"]=="nitro": desc+=f"`{k}` - {v['nombre']} - {v['precio']} 🍔\n"
    desc+="\nUsa `/canjear nombre` y `/mascotas`"
    await interaction.response.send_message(embed=discord.Embed(title="🏪 CRUSTÁCEO CASCARUDO - TIENDA", description=desc, color=0xFFEB3B))

@bot.tree.command(name="mascotas", description="Mira tus mascotas 🐾")
async def mascotas_cmd(interaction: discord.Interaction):
    d = get_user_data(interaction.guild.id, interaction.user.id)
    masc = d.get("mascotas", [])
    if not masc:
        await interaction.response.send_message("🐾 No tienes mascotas aún.", ephemeral=True); return
    desc = "\n".join([f"• {m}" for m in masc])
    await interaction.response.send_message(embed=discord.Embed(title=f"🐾 Mascotas de {interaction.user.name}", description=desc))

@bot.tree.command(name="canjear", description="Canjea tus CangreBurgers 🍔")
async def canjear(interaction: discord.Interaction, item: str):
    item = item.lower()
    if item not in TIENDA:
        await interaction.response.send_message(f"❌ No existe. Usa `/crustaceo_cascarudo`", ephemeral=True); return
    uid = str(interaction.user.id)
    gid = str(interaction.guild.id)

    datos = get_user_data(gid, uid)
    tienda_item = TIENDA[item]
    rol_nombre = tienda_item.get("rol")

    # Bloquear si ya lo tiene
    if tienda_item["nombre"] in datos["mascotas"]:
        await interaction.response.send_message(f"❌ ¡Ya tienes **{tienda_item['nombre']}**!", ephemeral=True); return
    if rol_nombre and discord.utils.get(interaction.user.roles, name=rol_nombre):
        await interaction.response.send_message(f"❌ ¡Ya tienes el rol **{rol_nombre}**!", ephemeral=True); return

    if datos["burgers"] < tienda_item["precio"]:
        await interaction.response.send_message(f"❌ Te faltan 🍔. Tienes {datos['burgers']} y cuesta {tienda_item['precio']}", ephemeral=True); return

    datos["burgers"] -= tienda_item["precio"]
    if tienda_item["tipo"] in ["mascota", "nitro"]:
        datos["mascotas"].append(tienda_item["nombre"])
    guardar(cangre_data)
    
    if rol_nombre:
        # Si compra un color, quitarle los otros colores que tenga
        if tienda_item["tipo"] == "rol":
            for otro_nombre in ROLES_MAP.values():
                if otro_nombre!= rol_nombre:
                    otro_rol = discord.utils.get(interaction.guild.roles, name=otro_nombre)
                    if otro_rol and otro_rol in interaction.user.roles:
                        try: await interaction.user.remove_roles(otro_rol)
                        except: pass

        rol = discord.utils.get(interaction.guild.roles, name=rol_nombre)
        if not rol:
            try:
                color = discord.Color(tienda_item.get("color", 0x99aab5))
                rol = await interaction.guild.create_role(name=rol_nombre, color=color, hoist=True)
            except: pass
        if rol:
            try: await interaction.user.add_roles(rol)
            except: pass

    await interaction.response.send_message(embed=discord.Embed(title="¡CANJE EXITOSO! 🎉", description=f"Canjeaste **{tienda_item['nombre']}** por **{tienda_item['precio']}** 🍔\n¡Te quedan {cangre_data[uid]['burgers']} 🍔!", color=0x00FF00))
@bot.tree.command(name="dar_burgers", description="Dale CangreBurgers a alguien (Solo Gerentes) 🍔")
async def dar_burgers(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    tiene_owner = discord.utils.get(interaction.user.roles, name=ROL_OWNER)
    tiene_admin = discord.utils.get(interaction.user.roles, name=ROL_ADMIN)
    if not tiene_owner and not tiene_admin and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo Gerentes pueden dar burgers 🦀", ephemeral=True); return
    if cantidad <=0:
        await interaction.response.send_message("❌ Cantidad inválida", ephemeral=True); return
    subio, data = add_burgers(str(interaction.guild.id), str(usuario.id), cantidad)
    await interaction.response.send_message(embed=discord.Embed(title="🍔 ¡BURGERS ENTREGADAS!", description=f"¡Le diste **{cantidad}** 🍔 a {usuario.mention}!\nAhora tiene **{data['burgers']}** 🍔 (Nv {data['nivel']})", color=0x00FF00))

@bot.tree.command(name="caracola_magica", description="Preguntale a la caracola mágica 🐚")
async def caracola_magica(interaction: discord.Interaction, pregunta: str):
    r = ["Sí 🐚", "No 🐚", "Tal vez algún día", "Definitivamente sí ✨", "Ni de broma 💀", "Obvio que sí", "Obvio que no", "Pregunta de nuevo más tarde 🐚", "La caracola dice que sí 👍"]
    await interaction.response.send_message(embed=discord.Embed(title="🐚 CARACOLA MÁGICA", description=f"**Pregunta:** {pregunta}\n**Respuesta:** {random.choice(r)}", color=0xf1c40f))

@bot.tree.command(name="youtube", description="Busca un video de YouTube")
async def youtube(interaction: discord.Interaction, buscar: str):
    busqueda = buscar.replace(" ", "+")
    await interaction.response.send_message(embed=discord.Embed(title="🔍 BUSCADOR DE GARY 🐌", description=f"Buscaste: **{buscar}**\n▶️ https://www.youtube.com/results?search_query={busqueda}", color=0xFF0000))

@bot.tree.command(name="radio_fondo_bikini", description="Pon radio en tu canal de voz 📻")
async def radio_fondo_bikini(interaction: discord.Interaction, estacion: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ ¡Métete a un canal de voz primero! 🎺", ephemeral=True); return
    if estacion not in RADIOS:
        await interaction.response.send_message(f"❌ Estaciones: {', '.join(RADIOS.keys())}", ephemeral=True); return
    await interaction.response.defer()
    try:
        canal = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc and vc.is_connected(): await vc.move_to(canal)
        else: vc = await canal.connect()
        ydl_opts = {**YTDL_OPTS_BASE, 'format': 'bestaudio/best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(RADIOS[estacion], download=False)
            url = info['url']
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
        await interaction.followup.send(f"📻 **¡Radio {estacion} ON!** en {canal.mention}")
    except Exception as e:
        print(e); await interaction.followup.send("❌ No pude poner la radio.")

@bot.tree.command(name="apaga_radio", description="Apaga la radio")
async def apaga_radio(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("🔇 ¡Radio apagada! 🦑")
    else:
        await interaction.response.send_message("❌ No estoy en voz", ephemeral=True)

@bot.tree.command(name="cangreburger_para_llevar", description="Pide tu descarga de YouTube para llevar 🍔")
async def cangreburger_para_llevar(interaction: discord.Interaction, link: str):
    await interaction.response.defer()
    await interaction.followup.send("🍔 ¡Cocinando tu Cangreburger de YouTube...")
    try:
        ydl_opts = {**YTDL_OPTS_BASE, 'format': 'bestaudio/best','outtmpl': '/tmp/%(title)s.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',}],}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            archivo = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            titulo = info.get('title', 'Cangreburger')
        if os.path.getsize(archivo) > 25*1024*1024:
            await interaction.followup.send("❌ Pesa más de 25MB"); os.remove(archivo); return
        await interaction.followup.send(f"🍔 **{titulo}** ¡Provecho! 😋", file=discord.File(archivo))
        os.remove(archivo)
    except Exception as e:
        print(e); await interaction.followup.send("❌ No pude descargar ese link.")

@bot.tree.command(name="cangreburger_spotify", description="Pide tu canción de Spotify para llevar 🎵")
async def cangreburger_spotify(interaction: discord.Interaction, link_spotify: str):
    await interaction.response.defer()
    await interaction.followup.send("🎵 ¡Gary está buscando tu canción en Spotify... 🐌")
    try:
        ydl_opts_info = {**YTDL_OPTS_BASE}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info_spotify = ydl.extract_info(link_spotify, download=False)
            titulo_spotify = info_spotify.get('title', '')
            artista = info_spotify.get('artist', '') or info_spotify.get('creator', '')
            busqueda = f"{artista} {titulo_spotify}".strip()
            if not busqueda or len(busqueda) < 3: busqueda = titulo_spotify
        await interaction.followup.send(f"🔍 Encontré: **{busqueda}**\n🍔 Ahora lo estoy cocinando...")
        ydl_opts = {**YTDL_OPTS_BASE, 'format': 'bestaudio/best','outtmpl': '/tmp/%(title)s.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',}],'default_search': 'ytsearch1','noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{busqueda}", download=True)
            if 'entries' in info: info = info['entries'][0]
            archivo = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            titulo = info.get('title', busqueda)
        if os.path.getsize(archivo) > 25*1024*1024:
            await interaction.followup.send("❌ Pesa más de 25MB"); os.remove(archivo); return
        await interaction.followup.send(f"🎵 **{titulo}** ¡Tu Cangreburger musical lista! 🍔", file=discord.File(archivo))
        os.remove(archivo)
    except Exception as e:
        print(e); await interaction.followup.send("❌ No pude encontrar esa canción.")

@bot.tree.command(name="roles", description="Panel de Color Burguers")
async def roles(interaction: discord.Interaction):
    desc = ""
    for emoji, nombre in ROLES_MAP.items():
        rol = discord.utils.get(interaction.guild.roles, name=nombre)
        desc += f"{emoji} {rol.mention}\n" if rol else f"{emoji} {nombre}\n"
    embed = discord.Embed(title="🍔 COLOR BURGUERS 🌈", description=desc, color=0xFF69B4)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    for e in ROLES_MAP.keys():
        try: await msg.add_reaction(e)
        except: pass

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name not in ROLES_MAP: return
    guild = bot.get_guild(payload.guild_id)
    if not guild: return
    member = guild.get_member(payload.user_id)
    if not member or member.bot: return

    tiene_color = False
    for nombre_rol in ROLES_MAP.values():
        if discord.utils.get(member.roles, name=nombre_rol):
            tiene_color = True
            break

    if tiene_color:
        try:
            channel = guild.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, member)
        except: pass
        return

    rol_nombre = ROLES_MAP[payload.emoji.name]
    rol = discord.utils.get(guild.roles, name=rol_nombre)
    if rol:
        try: await member.add_roles(rol)
        except: pass

@bot.event
async def on_raw_reaction_remove(payload):
    return

class CazaMedusasView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.cazadas = 0
        self.user = user
    @discord.ui.button(label="¡CAZAR!", style=discord.ButtonStyle.primary, emoji="🪼")
    async def cazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id!= self.user.id:
            await interaction.response.send_message("❌ Esta es la caza de otro!", ephemeral=True); return
        self.cazadas += 1
        await interaction.response.send_message(f"¡Cazaste {self.cazadas}/5 medusas! 🪼", ephemeral=True)
        if self.cazadas >= 5:
            subio, data = add_burgers(str(interaction.guild.id), str(self.user.id), 5)
            self.stop()
            await interaction.followup.send(f"🏆 ¡{interaction.user.mention} cazó 5 medusas y ganó **5** 🍔! ¡Tienes {data['burgers']} 🍔!")

class GaryView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=30)
        self.pos = random.randint(0, 8)
        self.user = user
        for i in range(9):
            btn = discord.ui.Button(label="❓", style=discord.ButtonStyle.secondary, custom_id=str(i))
            btn.callback = self.buscar
            self.add_item(btn)
    async def buscar(self, interaction: discord.Interaction):
        if interaction.user.id!= self.user.id:
            await interaction.response.send_message("❌ No es tu juego!", ephemeral=True); return
        if int(interaction.data["custom_id"]) == self.pos:
            subio, data = add_burgers(str(interaction.guild.id), str(self.user.id), 10)
            await interaction.response.send_message(f"¡{interaction.user.mention} ENCONTRÓ A GARY! 🐌💛 ¡Ganaste 10 🍔! Tienes {data['burgers']} 🍔")
            self.stop()
        else:
            await interaction.response.send_message("¡No está ahí! 👀", ephemeral=True)

@bot.tree.command(name="caza_medusas", description="¡Caza 5 medusas! 🪼")
async def caza_medusas(interaction: discord.Interaction):
    view = CazaMedusasView(interaction.user)
    await interaction.response.send_message("🪼 ¡LAS MEDUSAS ESCAPARON! ¡Dale al botón 5 veces! (+5 🍔)", view=view)

@bot.tree.command(name="busca_a_gary", description="¡Encuentra a Gary! 🐌")
async def busca_a_gary(interaction: discord.Interaction):
    view = GaryView(interaction.user)
    await interaction.response.send_message("🐌 ¡Gary se escondió! ¡Hay 9 casitas, toca una! (+10 🍔)", view=view)

@bot.tree.command(name="help", description="Ver TODOS los comandos")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    todos = bot.tree.get_commands()
    texto = "\n".join([f"`/{c.name}` - {c.description}" for c in sorted(todos, key=lambda x: x.name)])
    embed = discord.Embed(title="🍔 Comandos - Crustáceo Cascarudo", description=texto[:4000], color=0xFFD700)
    embed.set_footer(text=f"Total: {len(todos)} comandos | Yo estoy listo!")
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="atrapa_cangreburger", description="¡Atrapa la Cangreburger! 🍔")
async def atrapa_cangreburger(interaction: discord.Interaction):
    await interaction.response.send_message("🍔 ¡La Cangreburger está cayendo! ¡Escribe **ATRAPAR** en el chat en 5 segundos! (+15 🍔)")
    def check(m): return m.channel == interaction.channel and "atrapar" in m.content.lower() and not m.author.bot
    try:
        msg = await bot.wait_for('message', check=check, timeout=5.0)
        subio, data = add_burgers(str(interaction.guild.id), str(msg.author.id), 15)
        await interaction.followup.send(f"¡{msg.author.mention} ATRAPÓ LA CANGREBURGER! 🍔🏆 +15 🍔 (Total: {data['burgers']} 🍔)")
    except asyncio.TimeoutError:
        await interaction.followup.send("💀 ¡Se cayó! Nadie la atrapó!")

@bot.tree.command(name="banear", description="Banea a un usuario (solo gerentes)")
async def banear(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razon"):
    rol_gerente = discord.utils.get(interaction.user.roles, name="gerentes del Crustáceo")
    if not rol_gerente and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo los gerentes del Crustáceo pueden banear", ephemeral=True)
        return

    if usuario.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message("❌ No lo puedo banear, tiene rol mas alto que yo", ephemeral=True)
        return

    try:
        await usuario.ban(reason=f"{razon} | Por: {interaction.user.name}")
        await interaction.response.send_message(f"🔨 **{usuario.name}** fue baneado por {interaction.user.mention}\nRazón: {razon}")
    except:
        await interaction.response.send_message("❌ No pude banearlo", ephemeral=True)

@bot.tree.command(name="kickear", description="Expulsa a un usuario (solo gerentes)")
async def kickear(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razon"):
    rol_gerente = discord.utils.get(interaction.user.roles, name="gerentes del Crustáceo")
    if not rol_gerente and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo los gerentes del Crustáceo pueden kickear", ephemeral=True)
        return
    try:
        await usuario.kick(reason=razon)
        await interaction.response.send_message(f"👢 {usuario.mention} fue expulsado. Razón: {razon}")
    except:
        await interaction.response.send_message("❌ No lo pude kickear", ephemeral=True)
   
@bot.tree.command(name="confesar", description="Dile algo al oso confesoso 🐻")
async def confesar(interaction: discord.Interaction, dile_algo_al_oso: str):
    CONF_CHANNEL_ID = 1537279895892140092 # tu canal
    canal = bot.get_channel(CONF_CHANNEL_ID)
    uid = str(interaction.user.id)
    secretos_data["total"] += 1
    guardar_json(SECRETOS_FILE, secretos_data)
    secretos_user[uid] = secretos_user.get(uid, 0) + 1
    guardar_json(SECRETOS_USER_FILE, secretos_user)
    bonus = ""
    if secretos_user[uid] >= 10:
        secretos_user[uid] -= 10
        carnada_data[uid] = carnada_data.get(uid, 0) + 5
        guardar_json(SECRETOS_USER_FILE, secretos_user)
        guardar_json(CARNADA_FILE, carnada_data)
        bonus = f"\n¡Juntaste 10 secretos! +5 carnadas 🦀"
    embed = discord.Embed(description=dile_algo_al_oso, color=0x8B5A2B)
    embed.set_author(name="El oso confesoso a soltado un secreto")
    embed.set_footer(text=f"El oso confesoso lo guardo en la grabadora | Secreto #{secretos_data['total']}")
    await canal.send(embed=embed)
    await interaction.response.send_message(f"Llevas {secretos_user.get(uid, 0)}/10 secretos para 5 carnadas{bonus}\nTienes {carnada_data.get(uid, 0)} carnadas 🦀", ephemeral=True)

@bot.tree.command(name="grabadora", description="Ve cuantos secretos lleva el oso")
async def grabadora(interaction: discord.Interaction):
    await interaction.response.send_message(f"📼 El oso lleva **{secretos_data.get('total', 0)} secretos** guardados en la grabadora", ephemeral=True)

@bot.tree.command(name="canjear_carnada", description="Canjea 30 carnadas por 1 CangreBurger")
async def canjear_carnada(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    gid = str(interaction.guild.id)
    tiene = carnada_data.get(uid, 0)
    if tiene < 30:
        return await interaction.response.send_message(f"Tienes {tiene}/30 carnadas 🦐", ephemeral=True)
    carnada_data[uid] -= 30
    guardar_json(CARNADA_FILE, carnada_data)

    datos = get_user_data(gid, uid)
    datos["burgers"] += 1
    guardar(cangre_data)
    await interaction.response.send_message(f"Canjeaste 30 carnadas 🦐 por **1 CangreBurger** 🍔\nAhora tienes {datos['burgers']} 🍔")

GIFS_LISTA = {
    "abrazar": [
        "https://media1.tenor.com/m/MsE7K-BD-YkAAAAC/blacrswan.gif",
        "https://media1.tenor.com/m/jb1EDjVD2AwAAAAC/hug-spongebob.gif",
        "https://media1.tenor.com/m/IhPzM0Dde4MAAAAC/spongebob-squarepants-gary-the-snail.gif",
        "https://media1.tenor.com/m/wXbo11Ml4nsAAAAC/amoeba-spongebob.gif"
    ],
    "pat": [
        "https://media1.tenor.com/m/UazOKY8-RwgAAAAC/love-muah.gif"
    ],
    "acariciar": [
        "https://media1.tenor.com/m/siCgp4GNgTQAAAAC/%E0%A4%9A%E0%A5%81%E0%A4%AE%E0%A5%8D%E0%A4%AE%E0%A4%BE-spongebob.gif",
        "https://media1.tenor.com/m/p3LmzCWPAMoAAAAC/bubbles-love-you.gif"
    ],
    "besar": [
        "https://media1.tenor.com/m/-2ACdOGMSHMAAAAC/spongebob-bubble-blowing-tech.gif",
        "https://media1.tenor.com/m/6L7ewdJ0BmAAAAAC/bubble-buddy-spongebob.gif"
    ],
    "burbujas": [
        "https://media1.tenor.com/m/ebmZeRqeb20AAAAC/spongebob-spongebob-meme.gif"
    ],
    "boda": [
        "https://media1.tenor.com/m/GbQHupn6ttsAAAAC/bob-squarepants-grilling.gif",
        "https://media1.tenor.com/m/Qh2AM1tVZ7IAAAAC/sponge-bob-squarepants-burger.gif"
    ],
    "cocinar": [
        "https://media1.tenor.com/m/VSEIJCPl620AAAAC/spongebob-fry-cook.gif",
        "https://media1.tenor.com/m/JlSdyg72uv8AAAAC/burger-spongebob.gif"
    ],
    "comida": [
        "https://media1.tenor.com/m/Zckwf2ALjhAAAAAC/spongebob-spongebob-squarepants.gif",
        "https://media1.tenor.com/m/OdRISn_e-fMAAAAC/stay-cool.gif"
    ],
    "feliz": [
        "https://media1.tenor.com/m/PfU8EnthxfoAAAAC/broken-heart-heartbroken.gif"
    ],
    "triste": [
        "https://media1.tenor.com/m/jECLAOyljO4AAAAC/sad-spongebob.gif",
        "https://media1.tenor.com/m/VJOdd2gnzQgAAAAC/triste-tristeza.gif"
    ],
    "llorar": [
        "https://media1.tenor.com/m/VJOdd2gnzQgAAAAC/triste-tristeza.gif"
    ],
    "enojado": [
        "https://media1.tenor.com/m/AjDAGXOwHeQAAAAC/spongebob-angry.gif",
        "https://media1.tenor.com/m/dn5UFCxaVkUAAAAC/spongebob-choking-mr-krabs-angry-spongebob.gif"
    ],
    "dormir": [
        "https://media1.tenor.com/m/y05bQXbwBIYAAAAC/sponge-bob-sleep.gif",
        "https://media1.tenor.com/m/wIdsJiNbypUAAAAC/sponge-bob-seulisasoo.gif"
    ],
    "lamer": [
        "https://media1.tenor.com/m/9oCgrxjPMMsAAAAd/comfort-licking.gif",
        "https://media1.tenor.com/m/A7ARFmcg3acAAAAC/lick-jadedkiara.gif"
    ],
    "imaginacion": [
        "https://media1.tenor.com/m/S-TQKsUL38YAAAAC/rainbow-spongebob.gif"
    ],
    "karate": [
        "https://media1.tenor.com/m/bBM-I7ynzF8AAAAC/enhailed.gif",
        "https://media1.tenor.com/m/6uag6-PeISAAAAAd/sandy-cheeks-spongebob.gif"
    ],
    "pegar": [
        "https://media1.tenor.com/m/ioNXahL9oi8AAAAC/spongebob-gary-hits-spongebob.gif",
        "https://media1.tenor.com/m/_mHmsrgup2EAAAAC/spongebob-beat.gif"
    ],
    "sonrojar": [
        "https://media1.tenor.com/m/qwvaDwQLtowAAAAC/patrick-blush.gif",
        "https://media1.tenor.com/m/5dDIprU-_J8AAAAC/embarrassed-shy.gif"
    ],
    "listo": [
        "https://media1.tenor.com/m/rVIB2eOKwHgAAAAC/spongebob-waiting.gif",
        "https://media1.tenor.com/m/46uUIZlSBuIAAAAC/jellyfishing-spongebob.gif"
    ],
    "luna": [
        "https://media1.tenor.com/m/5oVPGC_xlFUAAAAC/spongebob-smile-fading.gif",
        "https://media1.tenor.com/m/rTN9H5qy5VUAAAAC/bob-esponja-spongebob.gif"
    ],
    "propuesta": [
        "https://media1.tenor.com/m/J3y2aL7vQpwAAAAC/spongebob-dancing.gif"
    ],
    "medusas": [
        "https://media1.tenor.com/m/46uUIZlSBuIAAAAC/jellyfishing-spongebob.gif"
    ],
    "morder": [
        "https://media1.tenor.com/m/dn5UFCxaVkUAAAAC/spongebob-choking-mr-krabs-angry-spongebob.gif"
    ]
}
async def get_gif(tipo):
    return random.choice(GIFS_LISTA.get(tipo, GIFS_LISTA["abrazar"]))

contador_data = {}

def rp_count(tipo, id1, id2):
    key = f"{tipo}_{id1}_{id2}"
    contador_data[key] = contador_data.get(key, 0) + 1
    return contador_data[key]

async def rol(interaction, tipo, usuario, verbo, texto_rol, color=0xffa6c9):
    conteo = rp_count(tipo, interaction.user.id, usuario.id)
    await interaction.response.defer()
    gif_url = await get_gif(tipo)
    embed = discord.Embed(color=color)
    embed.description = f"**{texto_rol}**\n\n{interaction.user.mention} {verbo} {usuario.mention}\n\n*{conteo} veces*"
    embed.set_image(url=gif_url)
    embed.set_footer(text="Crustáceo Cascarudo Roleplay 🍔")
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="abrazar", description="Abraza a alguien")
async def abrazar(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "abrazar", usuario, "abrazó", "🤗 Se dieron un abrazo bien esponjoso", 0xFFEB3B)

@bot.tree.command(name="besar", description="Besa a alguien")
async def besar(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "besar", usuario, "besó", "😘 Muak! Beso de cangreburger", 0xFF69B4)

@bot.tree.command(name="pegar", description="Pega a alguien")
async def pegar(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "pegar", usuario, "golpeó", "💥 ¡PUM! Golpe de karate de Arenita", 0xFF0000)

@bot.tree.command(name="morder", description="Muerde a alguien")
async def morder(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "morder", usuario, "mordió", "🐱 ¡Auch! Mordida de Gary", 0xFF8C00)

@bot.tree.command(name="acariciar", description="Acaricia a alguien")
async def acariciar(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "acariciar", usuario, "acarició", "🥰 Pat pat en la cabeza", 0xFFB6C1)

@bot.tree.command(name="pat", description="Hazle pat pat a alguien")
async def pat(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "pat", usuario, "le hizo pat pat a", "🥰 ¡Pat pat esponjoso!", 0xFFB6C1)

@bot.tree.command(name="lamer", description="Lame a alguien")
async def lamer(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "lamer", usuario, "lamió", "👅 ¡Que asco! Te lamieron", 0x9B59B6)

@bot.tree.command(name="darcomida", description="Dale cangreburger a alguien")
async def darcomida(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "comida", usuario, "alimentó", "🍔 Le diste una cangreburger", 0xFFA500)

@bot.tree.command(name="dormir", description="Duerme")
async def dormir(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"😴 **{interaction.user.display_name} se fue a dormir a su piña**", color=0x3498db)
    embed.set_image(url=await get_gif("dormir"))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="sonrojar", description="Te sonrojas")
async def sonrojar(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"😳 **{interaction.user.display_name} se sonrojó**", color=0xFF69B4)
    embed.set_image(url=await get_gif("sonrojar"))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="cocinar", description="Cocina")
async def cocinar(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"🍳 **{interaction.user.display_name} está cocinando en el Crustáceo**", color=0xFFA500)
    embed.set_image(url=await get_gif("cocinar"))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="feliz", description="Estas feliz")
async def feliz(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"😁 **{interaction.user.display_name} está feliz**", color=0xFFEB3B)
    embed.set_image(url=await get_gif("feliz"))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="triste", description="Estas triste")
async def triste(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"😔 **{interaction.user.display_name} está triste**", color=0x3498db)
    embed.set_image(url=await get_gif("triste"))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="enojado", description="Estas enojado")
async def enojado(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"😡 **{interaction.user.display_name} está enojado**", color=0xFF0000)
    embed.set_image(url=await get_gif("enojado"))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="llorar", description="Estas llorando")
async def llorar(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"😭 **{interaction.user.display_name} está llorando**", color=0x3498db)
    embed.set_image(url=await get_gif("llorar"))
    await interaction.followup.send(embed=embed)
@bot.tree.command(name="boda", description="Casate con alguien en Fondo de Bikini")
async def boda(interaction: discord.Interaction, usuario: discord.User):
    if usuario.id == interaction.user.id:
        await interaction.response.send_message("😒 No te puedes casar contigo mismo, Bob!", ephemeral=True)
        return
    
        conteo = rp_count("boda", interaction.user.id, usuario.id)
    await interaction.response.defer()
    gif_url = await get_gif("boda")
    embed = discord.Embed(color=0xFF6BC1, title="💍 ¡BODA EN FONDO DE BIKINI! 💒")
    embed.description = f"**¡Se han casado!**\n\n{interaction.user.mention} 💖 {usuario.mention}\n¡Se han casado **{conteo} veces**!"
    embed.set_image(url=gif_url)
    embed.set_footer(text="Oficiado por el mismísimo Bob Esponja 🧽")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="divorcio", description="Divorciate de alguien")
async def divorcio(interaction: discord.Interaction, usuario: discord.User):
    await interaction.response.defer()
    gif_url = await get_gif("triste")
    embed = discord.Embed(color=0x000000, title="💔 DIVORCIO EN FONDO DE BIKINI")
    embed.description = f"😭 {interaction.user.mention} se divorció de {usuario.mention}\n\n*Don Cangrejo les va a cobrar los papeles*"
    embed.set_image(url=gif_url)
    await interaction.followup.send(embed=embed)

# --- PACK EXTRA BOB ESPONJA ---
@bot.tree.command(name="propuesta", description="Proponle matrimonio a alguien")
async def propuesta(interaction: discord.Interaction, usuario: discord.User):
    conteo = rp_count("propuesta", interaction.user.id, usuario.id)
    await interaction.response.defer()
    gif_url = await get_gif("boda") # usa query de boda
    embed = discord.Embed(color=0xFFD700, title="💍 ¡PROPUESTA DE MATRIMONIO!")
    embed.description = f"**¡OMG!**\n\n{interaction.user.mention} le propuso matrimonio a {usuario.mention} **{conteo} veces**\n\n*¿Aceptas? Di que sí con /boda*"
    embed.set_image(url=gif_url)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="luna", description="Luna de miel en Fondo de Bikini")
async def luna(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "luna", usuario, "se fue de luna de miel con", "🌙 ¡Luna de miel en la Piña!", 0xFF69B4)

@bot.tree.command(name="karate", description="Pelea de karate con alguien")
async def karate(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "karate", usuario, "hizo karate con", "🥋 ¡HI-YA! Hora de karate", 0xFF0000)

@bot.tree.command(name="medusas", description="Atrapen medusas juntos")
async def medusas(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "medusas", usuario, "atrapó medusas con", "🪼 ¡A atrapar medusas!", 0x00BFFF)

@bot.tree.command(name="burbujas", description="Sopla burbujas con alguien")
async def burbujas(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "burbujas", usuario, "sopló burbujas con", "🫧 Burbujas de jabón bien bonitas", 0x87CEEB)

@bot.tree.command(name="imaginacion", description="Usa la imaginación con alguien")
async def imaginacion(interaction: discord.Interaction, usuario: discord.User):
    await rol(interaction, "imaginacion", usuario, "usó la imaginación con", "🌈 ¡IMAGINACIOOON!", 0x9B59B6)
    
@bot.tree.command(name="listo", description="Estoy listo!!!")
async def listo(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"**¡ESTOY LISTO! ¡ESTOY LISTO!** - {interaction.user.mention}", color=0xFFEB3B)
    embed.set_image(url=await get_gif("feliz"))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="cangreburguer", description="Cocina una cangreburguer")
async def cangreburguer(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(description=f"🍔 **{interaction.user.display_name} preparó una Cangreburguer bien sabrosa**", color=0xFFA500)
    embed.set_image(url=await get_gif("comida"))
    await interaction.followup.send(embed=embed)

ultimo_mensaje_id = set()
ultimas_respuestas = {}

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.id in ultimo_mensaje_id: return
    ultimo_mensaje_id.add(message.id)
    if len(ultimo_mensaje_id) > 1000: ultimo_mensaje_id.clear()

    # Burgers por hablar (solo server)
    if not isinstance(message.channel, discord.DMChannel):
        if not message.content.startswith("!") and not message.content.startswith(")"):
            ganados = random.randint(1, 3)
            if message.guild:
                subio, data = add_burgers(str(message.guild.id), str(message.author.id), ganados)
            else:
                subio, data = False, {}
            if subio:
                canal = bot.get_channel(CANGRE_CHANNEL_ID)
                if canal:
                    embed = discord.Embed(title="¡SUBISTE DE NIVEL! 🎉", description=f"¡¡{message.author.mention} subió al nivel **{data['nivel']}**!! 🧽✨\n¡Tienes {data['burgers']} CangreBurgers! 🍔", color=0xFFEB3B)
                    try: await canal.send(embed=embed)
                    except: pass

    es_dm = isinstance(message.channel, discord.DMChannel)
    es_mencionado = bot.user in message.mentions
    if not es_dm and not es_mencionado:
        await bot.process_commands(message)
        return

    texto_original_full = message.content
    texto = re.sub(r'<@!?\d+>', '', texto_original_full.lower()).strip()
    texto_original = re.sub(r'<@!?\d+>', '', texto_original_full).strip()
    if texto == "": texto = "hola"; texto_original = "hola"

        # --- TODAS LAS RESPUESTAS ---
    respuestas_hola = [
        f"¡Hola soy Bob Esponja! ¿Has visto a Gary? Se escondió otra vez 🐌 ¡Hola {message.author.name}!",
        f"¡Hola {message.author.name}! ¡Soy Bob Esponja! ¿Quieres ir a cazar medusas?",
        f"¡Hola! ¡Soy Bob Esponja! Vivo en una piña debajo del mar 🍍 ¿Y tú cómo estás {message.author.name}?",
        f"¡Hola {message.author.name}! ¡Estoy listo! ¡Estoy listo! ¿Qué vamos a hacer? 🧽",
    ]
    respuestas_como_estas = [
        f"¡Hola {message.author.name}! ¿Cómo estás? ¡Yo estoy listo, listo, listo!",
        f"¡Yo estoy muy feliz {message.author.name}! ¿Y tú cómo estás?",
        f"¡Estoy muy bien {message.author.name}! ¿Y tú qué tal?",
    ]
    respuestas_cangreburger = [
        f"¡Oh! ¿Quieres una CangreBurger {message.author.name}? Don Cangrejo me dijo que no regale... pero solo una 🤫 🍔",
        f"¡Claro que sí {message.author.name}! Toma tu CangreBurger 🍔✨",
    ]
    respuestas_te_quiero = [
        f"¡Yo también te quiero mucho {message.author.name}! ¡Eres mi amigo favorito! 💛",
        f"¡Awww {message.author.name}! ¡Yo también te quiero! 🐌💕",
    ]
    respuestas_amigo = [
        f"¡Claro que eres mi amigo {message.author.name}! ¡Vamos a cazar medusas! 👯‍♂️",
        f"¡Por supuesto que somos amigos {message.author.name}! ¡Amigos por siempre!",
    ]
    respuestas_risa = [
        f"¡Jajajajajajaja! {message.author.name} ¡Eso me dio mucha risa! 😂",
        f"¡Hahahahahaha! ¡Eres muy gracioso {message.author.name}! 🤣",
    ]
    respuestas_tierno = [
        f"¡Awww uwu! ¡Qué tierno {message.author.name}! ¡Me hiciste sonrojar! 🥺💛",
        f"¡Uwu! ¡Eso fue muy tierno {message.author.name}!",
    ]
    respuestas_enojado = [
        f"¡Oye {message.author.name}! ¡No te enojes! ¡Vamos a hacer burbujas para calmarnos! 🫧",
        f"¡No estés enojado {message.author.name}! ¡No queremos ser como Calamardo cuando se enoja! 😠",
    ]
    respuestas_carita_triste = [
        f"¡Oh no {message.author.name}! ¿Por qué esa carita? ¡Te doy un abrazo! 🤗",
        f"¡{message.author.name}! ¿Estás triste? ¡Yo estoy aquí contigo! 💛",
    ]
    respuestas_random = [
        f"¡Jajaja {texto_original_full}! ¡Eso me recuerda a Patricio! 😃",
        f"¡{texto_original_full}? ¡Eso dijo Calamardo que nunca! 😮",
        f"¡Imagínate! ¡{texto_original_full} en Fondo de Bikini! ✨",
        f"¡Santa madre de Gary! ¡{texto_original_full}! ¡Qué locura!",
        f"¡Patricio, {texto_original_full}! ¿Qué opinas? ⭐",
    ]
    respuestas_triste = [
        f"Oh no {message.author.name}... ¿Estás triste? Ven, te doy un abrazo muy fuerte 🤗💛",
        f"No estés triste {message.author.name}, mañana será un día mejor y yo estaré aquí contigo 💛",
        f"{message.author.name}, si tú estás triste yo también me pongo triste... ¿Te regalo una sonrisa? 😊",
    ]
    respuestas_me_siento_mal = [
        f"{message.author.name}, lamento que te sientas así... Quiero que sepas que eres muy importante para mí 💛",
        f"No me gusta verte así {message.author.name}... ¿Quieres que me quede aquí contigo un ratito? 🍍",
        f"Está bien sentirse mal a veces {message.author.name}, no tienes que ser fuerte todo el tiempo. Te acompaño 🤗",
        f"Te mando un abrazo de Gary 🐌💛 Todo va a estar bien, te lo prometo",
    ]
    respuestas_bonito = [
        f"¡Qué lindo eres {message.author.name}! Me hiciste muy feliz con eso 🥺💛",
        f"Aww {message.author.name} ¡Tú también eres increíble! Gracias por ser tan amable 💛",
        f"¡Me hiciste sonrojar {message.author.name}! 🥰 Eres el mejor amigo de Fondo de Bikini",
    ]
    respuestas_medusas = [
        f"¡Sí! ¡Claro que puedes acompañarme {message.author.name}! ¡Vamos a cazar medusas! 🪼",
        f"¡Estoy listo! ¡Estoy listo! ¡Vamos a cazar medusas juntos {message.author.name}! 🪼✨",
        f"¡Sí, vamos! Traje mi red, ¿Tú trajiste la tuya {message.author.name}? ¡Vamos por la medusa gigante!",
        f"¡Me encantaría que me acompañes {message.author.name}! Será la mejor cazada de medusas de todas 💛",
    ]
    respuestas_jugar = [
        f"¡Sí quiero jugar contigo {message.author.name}! ¿A qué jugamos? 🎮",
        f"¡Claro que sí {message.author.name}! Jugar contigo siempre es divertido ⭐",
        f"¡Vamos a jugar {message.author.name}! Yo invito las CangreBurgers después 🍔",
    ]

    async with message.channel.typing():
        await asyncio.sleep(0.6)
        if any(p in texto for p in ["quien es mejor del server", "quién es el mejor del server", "quien es el mejor", "mejor del server"]):
            miembros = [m for m in message.guild.members if not m.bot] if message.guild else []
            if miembros:
                elegido = random.choice(miembros)
                resp = f"¡El mejor del server es {elegido.mention}! ¡Es una estrella! ⭐"
            else:
                resp = f"¡El mejor eres tú {message.author.name}! 💛"
        elif any(p in texto for p in ["me siento mal", "me siento triste", "estoy mal", "me siento horrible", "me siento fatal"]):
            if any(p in texto for p in ["solo", "sin amigos", "no tengo amigos"]):
                resp = f"{message.author.name}, sé que te sientes solo, pero vas a conseguir amigos que te quieran mucho. Yo ya soy tu amigo y no te voy a dejar solo 💛⭐"
            elif any(p in texto for p in ["nadie me quiere", "no me quieren", "me odian"]):
                resp = f"{message.author.name}, yo sí te quiero muchísimo. Eres una persona muy especial y vales mucho para mí 💛🤗"
            else:
                resp = random.choice(respuestas_me_siento_mal)
        elif any(p in texto for p in ["vas a cazar medusas", "vas a pescar medusas", "cazar medusas", "pescar medusas", "vamos a cazar medusas"]):
            resp = random.choice(respuestas_medusas)
        elif any(p in texto for p in ["quieres jugar", "jugamos", "juegas conmigo", "quieres jugar conmigo"]):
            resp = random.choice(respuestas_jugar)
        elif any(p in texto for p in ["eres lindo", "te amo bob", "te quiero mucho", "eres tierno", "eres hermoso", "que bonito"]):
            resp = random.choice(respuestas_bonito)
        elif any(p in texto for p in ["estoy triste", "toy triste", "esa carita"]):
            resp = random.choice(respuestas_triste)
        elif "cangreburger" in texto:
            resp = random.choice(respuestas_cangreburger)
        elif any(p in texto for p in ["te quiero", "te amo", "tqm"]):
            resp = random.choice(respuestas_te_quiero)
        elif any(p in texto for p in ["eres mi amigo", "somos amigos"]):
            resp = random.choice(respuestas_amigo)
        elif any(p in texto for p in ["como estas", "cómo estás", "como andas"]):
            resp = random.choice(respuestas_como_estas)
        elif any(p in texto for p in ["xd", "jajaja", "jeje", "jaja", "lol"]):
            resp = random.choice(respuestas_risa)
        elif any(p in texto for p in ["uwu", "owo", "🥺"]):
            resp = random.choice(respuestas_tierno)
        elif any(p in texto for p in [">:(", "> :v", "enojado", "😠", "😡"]):
            resp = random.choice(respuestas_enojado)
        elif any(p in texto for p in [":(", ":'(", "triste", "😢", "😭"]):
            resp = random.choice(respuestas_carita_triste)
        elif any(p in texto for p in ["hola", "ola", "hey", "buenas", "holu"]):
            resp = random.choice(respuestas_hola)
        else:
            resp = random.choice(respuestas_random)

        uid = message.author.id
        ultima = ultimas_respuestas.get(uid)
        while resp == ultima and len(respuestas_random) > 1:
            resp = random.choice(respuestas_random)
        ultimas_respuestas[uid] = resp
        await message.channel.send(resp)
        return

keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
bot.run(TOKEN)
