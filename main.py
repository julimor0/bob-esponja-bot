import discord, random, os, yt_dlp, asyncio, re, json
from discord.ext import commands, tasks
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=["!", "."], intents=intents)

# --- ARCHIVOS JSON ---
CANGRE_FILE = "cangre.json"
CONF_CANALES_FILE = "conf_canales.json"
CARNADA_FILE = "carnada.json"
SECRETOS_FILE = "secretos.json"
SECRETOS_USER_FILE = "secretos_user.json"
WELCOME_FILE = "welcome.json"
BIENVENIDA_FILE = "bienvenida.json"
NIVELES_FILE = "niveles.json"
CUMPLES_FILE = "cumples.json"
CUMPLES_CANALES_FILE = "cumples_canales.json"

def cargar_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return json.load(f)
        except: return default
    return default

def guardar_json(path, data):
    with open(path, "w") as f: json.dump(data, f)

conf_canales = cargar_json(CONF_CANALES_FILE)
carnada_data = cargar_json(CARNADA_FILE)
secretos_data = cargar_json(SECRETOS_FILE)
if "total" not in secretos_data: secretos_data = {"total": 0}
secretos_user = cargar_json(SECRETOS_USER_FILE)

cumples_data = cargar_json(CUMPLES_FILE, {})
cumples_canales = cargar_json(CUMPLES_CANALES_FILE, {})
cumples_felicitados = {}

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
async def on_member_join(member):
    gid=str(member.guild.id)
    canal=None
    if gid in conf_canales and "bienvenida" in conf_canales[gid]:
        canal=bot.get_channel(conf_canales[gid]["bienvenida"])
    if not canal:
        for ch in member.guild.text_channels:
            if ch.permissions_for(member.guild.me).send_messages:
                canal=ch
                break
    if not canal: return
    embed=discord.Embed(title="¡ESTOY LISTOOOOO! 🧽🍍", description=f"¡¡Llegó {member.mention}!! Ya somos {member.guild.member_count} 🥳", color=0xFFEB3B)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url="attachment://bienvenida.jpg")
    try:
        archivo=discord.File("bienvenida.jpg", filename="bienvenida.jpg")
        await canal.send(content=f"¡¡{member.mention} ESTOY LISTO!!", embed=embed, file=archivo)
    except:
        await canal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    gid = str(member.guild.id)
    canal = None
    if gid in conf_canales and "despedidas" in conf_canales[gid]:
        canal = bot.get_channel(conf_canales[gid]["despedidas"])
    if not canal:
        return

    embed = discord.Embed(
        title="¡ESTOY TRISTEEEE! 🥜🍍",
        description=(
            f"¡¡Se fue **{member.display_name}** de Fondo de Bikini!!\n"
            f"¡Adiós {member.display_name}! 💛\n"
            f"¡Ya somos **{member.guild.member_count}** habitantes! 🥺\n\n"
            f"**Estoy listo tristeza**"
        ),
        color=0xFFEB3B
    )
    if member.display_avatar:
        embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.name} • ¡Te extrañaré! 🍍")

    await canal.send(content=f"¡¡**{member.display_name}** SE FUE!! 🥜", embed=embed)
    await canal.send("https://media.tenor.com/2UyENRuvVhsAAAAC/bob-esponja-triste.gif")

@bot.tree.command(name="setdespedidas", description="Pon el canal de despedidas para este server 🍍")
async def setdespedidas(interaction: discord.Interaction, canal: discord.TextChannel = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Solo admins 🦀", ephemeral=True)
        return

    if canal is None:
        canal = interaction.channel

    gid = str(interaction.guild.id)
    if gid not in conf_canales:
        conf_canales[gid] = {}
    conf_canales[gid]["despedidas"] = canal.id
    guardar_json(CONF_CANALES_FILE, conf_canales)

    await interaction.response.send_message(f"✅ Despedidas de este server en {canal.mention} 🍍\nAhora cuando alguien se vaya saldrá como en tu foto, con la piña y el *Estoy listo... para la tristeza*")

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
    if not interaction.user.guild_permissions.administrator:
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
    if not interaction.user.guild_permissions.ban_members and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo gente con permiso de Banear puede banear", ephemeral=True)
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
    if not interaction.user.guild_permissions.kick_members and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo gente con permiso de Kickear puede kickear", ephemeral=True)
        return
    
    try:
        await usuario.kick(reason=razon)
        await interaction.response.send_message(f"👢 {usuario.mention} fue expulsado. Razón: {razon}")
    except:
        await interaction.response.send_message("❌ No lo pude kickear", ephemeral=True)
   
@bot.tree.command(name="confesar", description="Dile algo al oso confesoso 🐻")
async def confesar(interaction: discord.Interaction, dile_algo_al_oso: str):
    gid_conf=str(interaction.guild.id)
    conf=conf_canales.get(gid_conf,{})
    canal_id=conf.get("confesiones")
    canal=bot.get_channel(canal_id) if canal_id else interaction.channel
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

@bot.tree.command(name="set_bienvenida", description="Configura bienvenida de ESTE server")
async def set_bienvenida(interaction: discord.Interaction):
    canal = interaction.channel
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo admins", ephemeral=True)
    gid=str(interaction.guild.id)
    if gid not in conf_canales: conf_canales[gid]={}
    conf_canales[gid]["bienvenida"]=canal.id
    guardar_json(CONF_CANALES_FILE, conf_canales)
    await interaction.response.send_message(f"✅ Bienvenida en {canal.mention}", ephemeral=True)

@bot.tree.command(name="set_niveles", description="Configura niveles")
async def set_niveles(interaction: discord.Interaction):
    canal = interaction.channel
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo admins", ephemeral=True)
    gid=str(interaction.guild.id)
    if gid not in conf_canales: conf_canales[gid]={}
    conf_canales[gid]["cangre"]=canal.id
    guardar_json(CONF_CANALES_FILE, conf_canales)
    await interaction.response.send_message(f"✅ Niveles en {canal.mention}", ephemeral=True)

@bot.tree.command(name="set_confesiones", description="Configura confesiones")
async def set_confesiones(interaction: discord.Interaction):
    canal = interaction.channel
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo admins", ephemeral=True)
    gid=str(interaction.guild.id)
    if gid not in conf_canales: conf_canales[gid]={}
    conf_canales[gid]["confesiones"]=canal.id
    guardar_json(CONF_CANALES_FILE, conf_canales)
    await interaction.response.send_message(f"✅ Confesiones en {canal.mention}", ephemeral=True)

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
        await interaction.response.send_message("😅 No te puedes casar contigo mismo!", ephemeral=True)
        return
    conteo = rp_count("boda", interaction.user.id, usuario.id)
    await interaction.response.defer()
    gif_url = await get_gif("boda")
    embed = discord.Embed(color=0xFF68C1, title="💍 ¡BODA EN FONDO DE BIKINI! 💒")
    embed.description = f"**¡Se han casado!**\n\n{interaction.user.mention} 💖 {usuario.mention}"
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

# ===== SISTEMA CUMPLES ESTILO MEJOR DIA - PRIVADO =====
from discord.ext import tasks
import datetime

class CumpleView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="🎶 El Mejor Día De Todos", url="https://www.youtube.com/watch?v=a2RA0Vs2Knc", style=discord.ButtonStyle.link))

@bot.tree.command(name="mi_cumple", description="Guarda tu cumpleaños en privado 🎂")
async def mi_cumple(interaction: discord.Interaction, dia: int, mes: int, edad: int = None):
    # PRIVADO COMO OSO CONFESOSO - ephemeral
    if dia < 1 or dia > 31 or mes < 1 or mes > 12:
        return await interaction.response.send_message("❌ Fecha inválida. Usa: `/mi_cumple 15 8` o `/mi_cumple 15 8 17` si quieres poner edad", ephemeral=True)
    if edad is not None and (edad < 1 or edad > 100):
        return await interaction.response.send_message("❌ Edad inválida", ephemeral=True)

    uid = str(interaction.user.id)
    cumples_data[uid] = {"dia": dia, "mes": mes, "edad": edad}
    guardar_json(CUMPLES_FILE, cumples_data)

    if edad:
        msg = f"✅ ¡Guardado en privado! Tu cumple es **{dia}/{mes}** y cumples **{edad}** 🎉\n🔒 Nadie verá esto, solo Bob te felicitará ese día."
    else:
        msg = f"✅ ¡Guardado en privado! Tu cumple es **{dia}/{mes}** 🎉\n🔒 Nadie verá esto, solo Bob te felicitará ese día.\n💡 Tip: Si quieres poner tu edad usa `/mi_cumple {dia} {mes} 17`"

    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="set_cumples", description="Canal donde Bob felicitará con colores Bob")
async def set_cumples(interaction: discord.Interaction):
    canal = interaction.channel
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo admins", ephemeral=True)
    cumples_canales[str(interaction.guild.id)] = canal.id
    guardar_json(CUMPLES_CANALES_FILE, cumples_canales)
    await interaction.response.send_message(f"✅ Bob felicitará los cumpleaños en {canal.mention} con colores Bob Esponja 🎨💛", ephemeral=True)

@tasks.loop(minutes=60)
async def revisar_cumples():
    ahora = datetime.datetime.now()
    dia_hoy = ahora.day
    mes_hoy = ahora.month
    fecha_hoy_str = f"{dia_hoy}-{mes_hoy}-{ahora.year}"

    for guild in bot.guilds:
        gid = str(guild.id)
        if gid not in cumples_canales: continue
        canal = guild.get_channel(cumples_canales[gid])
        if not canal: continue

        for uid, data in cumples_data.items():
            if data["dia"] == dia_hoy and data["mes"] == mes_hoy:
                key = f"{gid}-{uid}-{fecha_hoy_str}"
                if key in cumples_felicitados: continue
                try:
                    member = guild.get_member(int(uid))
                    if not member: continue

                    # EDAD OPCIONAL
                    edad_text = ""
                    if data.get("edad"):
                        edad_text = f" ¡Hoy cumples **{data['edad']}** años! 🎂"

                    embed = discord.Embed(
                        title="☀️ ¡EL MEJOR DÍA DE TODOS! 🎉",
                        description=(
                            f"## 💛💙 ¡¡ @everyone ES EL MEJOR DÍA DE TODOS!!! 💙💛\n"
                            f"### 🎂 Hoy es el cumple de {member.mention}{edad_text} 🎈\n\n"
                            f"🎤 **Bob Esponja canta:**\n"
                            f"```\n"
                            f"El sol ha salido y me ha sonreído\n"
                            f"Que seria un buen día me ha prometido\n\n"
                            f"Salte de la cama con mucha alegría\n"
                            f"Sintiéndome como nunca\n\n"
                            f"Y el mejor día es (es el mejor)\n"
                            f"El mejor día es (es el mejor)\n"
                            f"```\n"
                            f"🐌 *Hola Gary, ¿porqué es el mejor día?*\n"
                            f"🧽 *¡Porque hoy es el cumple de **{member.display_name}**!*\n"
                            f"🌸 *Hoy voy a darle vida a una nueva generación de flores*\n"
                            f"🎈 *y salgo así, con globos y regalos para festejar*\n"
                            f"🎉 *con una gran fiesta con Arenita*\n"
                            f"🎁 *y una tarde entera celebrando con Patricio*\n"
                            f"🎂 *donde revelaremos el pastel de lujo profesional*\n"
                            f"🥳 *¡Y para el gran final, todos cantaremos Feliz Cumpleaños!*\n"
                            f"¡Estoy tan emocionado creo que voy a explotar!*\n\n"
                            f"🎤 **¡TODOS CANTAMOS!**\n"
                            f"```diff\n"
                            f"+ El mejor día es (es el mejor) 🎂\n"
                            f"+ El mejor día es (es el mejor) 🎉\n"
                            f"+ ¡FELIZ CUMPLEAÑOS {member.display_name.upper()}!\n"
                            f"+ ¡El mejor día es! (¡es el mejor!) 🎶\n"
                            f"```\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"# 💛 ¡FELIZ CUMPLEAÑOS! 💛"
                        ),
                        color=0xFFD700 # Amarillo Bob Esponja
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_image(url="https://media.tenor.com/8aXv5g3yY5AAAAAi/spongebob-best-day-ever.gif")
                    embed.set_footer(text=f"💛💙 Bob Esponja | 🎂 {dia_hoy}/{mes_hoy} | ¡El Mejor Día De Todos!", icon_url=bot.user.display_avatar.url)
                    embed.set_author(name=f"🎤 ¡Hoy es el cumple de {member.display_name}!")

                    await canal.send(
                        content=f"@everyone 💛💙☀️ ¡¡¡EL MEJOR DÍA DE TODOS!!! Hoy cumple {member.mention} 🎉🎂🎈",
                        embed=embed,
                        view=CumpleView()
                    )
                    cumples_felicitados[key] = True
                except Exception as e:
                    print(f"Error cumple: {e}")

@revisar_cumples.before_loop
async def before_cumples():
    await bot.wait_until_ready()

ultimo_mensaje_id = set()
ultimas_respuestas = {}

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.id in ultimo_mensaje_id: return
    ultimo_mensaje_id.add(message.id)
    if len(ultimo_mensaje_id) > 1000: ultimo_mensaje_id.clear()

        # Burgers por hablar (solo servidor)
    if not isinstance(message.channel, discord.DMChannel):
        if not message.content.startswith("!") and not message.content.startswith("."):
            ganados = random.randint(1, 3)
            subio, data = add_burgers(str(message.guild.id), str(message.author.id), ganados)
            if subio:
                canal = bot.get_channel(CANGRE_CHANNEL_ID)
                if canal:
                    embed = discord.Embed(title="¡SUBISTE DE NIVEL! 🎉", description=f"¡{message.author.mention} subió a nivel {data['nivel']}!", color=0xFFD700)
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
        # --- PARTE 1 - MEGA PACK ---
    respuestas_patricio = [f"¡PATRICIOOO {message.author.name}! ¡Mi mejor amigo! ⭐💛", f"¡Patricio estrella {message.author.name}! ¡Brilla! ⭐✨", f"¡No, esto es Patricio! 🪨 {message.author.name} ¡Jajaja! 😂", f"¡Patricio ¿Es mayonesa un instrumento? 🥜 {message.author.name}!", f"¡Patricio y yo medusas {message.author.name}! ¡Estoy listo! 🪼⭐🙋‍♂️", f"¡Patricio roca y yo piña {message.author.name}! 🪨🍍👯‍♂️", f"¡Patricio se comió mi dona {message.author.name}! 🍩⭐", f"¡Yo wumbo tú wumbo {message.author.name}! ⭐📚"]
    respuestas_calamardo = [f"¡CALAMARDOOO {message.author.name}! ¡Hola vecino! 🗿💛", f"¡Calamardo clarinete {message.author.name}! ¡Piii! 🎶🗿", f"¡Otra vez Bob Esponja! {message.author.name} ¡Sí soy yo! 🗿🧽😂", f"¡Calamardo artista {message.author.name}! ¡Fan #1! 🎨🗿👏", f"¡Casa Moai elegante {message.author.name}! 🗿🏛️", f"¡Calamardo gruñón pero lo quiero {message.author.name}! 🗿💛", f"¡Calamardo famoso {message.author.name}! 🌟🗿", f"¡Vecino Calamardo {message.author.name}! ¡Vamos a jugar! 🗿🧽"]
    respuestas_arenita = [f"¡ARENITAAA {message.author.name}! ¡YEE-HAW! 🐿️🤠", f"¡Karate con Arenita {message.author.name}! ¡HI-YA! 🐿️🥋🙋‍♂️", f"¡Arenita inventa cohetes {message.author.name}! 🚀🐿️", f"¡Arenita la más fuerte {message.author.name}! 💪🐿️", f"¡Arenita domo con aire {message.author.name}! 🌳🤠", f"¡Yee-haw y Estoy listo {message.author.name}! 🤠🙋‍♂️", f"¡Arenita me ganó karate {message.author.name}! 🐿️🥋😅", f"¡Arenita astronauta {message.author.name}! 👨‍🚀🐿️✨"]
    respuestas_don_cangrejo_n = [f"¡DON CANGREJO {message.author.name}! ¡Mi jefe! 💰🦀", f"¡Don Cangrejo dinero {message.author.name}! ¡Yo CangreBurgers! 💰🍔", f"¡Dinero dinero dice {message.author.name}! 💰🙋‍♂️", f"¡Trabajo en Crustáceo {message.author.name}! ¡El mejor! 🍔🏪", f"¡Ancla fuerte {message.author.name}! ⚓🦀", f"¡Fórmula secreta jefe {message.author.name}! 🤫💰🍔", f"¡Cuenta monedas {message.author.name}! 💰😵‍💫", f"¡Jefe tacañito pero lo quiero {message.author.name}! 🦀💛"]
    respuestas_plankton_n = [f"¡PLANKTON {message.author.name}! ¡Chiquito! 🦠🍔", f"¡Plankton y Karen {message.author.name}! 🦠💻💕", f"¡Maldito Cangrejo dice {message.author.name}! 🦠😂", f"¡Quiere ser grande {message.author.name}! 🦠🙋‍♂️", f"¡Falló otra vez {message.author.name}! 🦠🍔💛", f"¡Vive en Balde solito {message.author.name}! 🪣🧽", f"¡Karen ¡Oh Plankton! {message.author.name} 💻😂", f"¡Corazón grandote {message.author.name}! 🦠💛🐌"]
    respuestas_perlita = [f"¡PERLITAAA {message.author.name}! ¡Ballena cool! 🐳💅✨", f"¡Perlita de compras {message.author.name}! 🐳🛍️💰", f"¡Perlita canta {message.author.name}! 🐳🎤💛", f"¡Perlita y papá Cangrejo {message.author.name}! 🐳🦀💛", f"¡Perlita gigante tierna {message.author.name}! 🐳🧸💛", f"¡Fiesta ballena {message.author.name}! 🐳🎉", f"¡Perlita adolescente cool {message.author.name}! 🐳😎", f"¡Perlita centro comercial {message.author.name}! 🐳🏬"]
    respuestas_sra_puff = [f"¡SRA PUFF {message.author.name}! ¡Perdón choqué! 🚤💥🥺", f"¡Sra Puff globo {message.author.name}! 🎈🚤😂", f"¡Respira Bob dice {message.author.name}! 🚤🫁🙋‍♂️", f"¡Maestra favorita {message.author.name}! 🚤💛", f"¡Me reprobó otra vez {message.author.name}! 🚤😭", f"¡Bote bonito {message.author.name}! 🚤✨", f"¡Te quiero maestra {message.author.name}! 🚤💛📚", f"¡Voy a pasar examen {message.author.name}! 🚤🙋‍♂️"]
    respuestas_larry = [f"¡LARRY {message.author.name}! ¡Músculos! 🦞💪", f"¡Vive como Larry {message.author.name}! 🦞🙋‍♂️", f"¡Salvavidas Goo Lagoon {message.author.name}! 🦞🏖️", f"¡Músculos espagueti {message.author.name}! 🦞🧽😂", f"¡Levanta pesas {message.author.name}! 🏋️🦞", f"¡Héroe musculoso {message.author.name}! 🦞🦸‍♂️", f"¡Vamos a entrenar {message.author.name}! 🏋️🙋‍♂️", f"¡Bronceado cool {message.author.name}! 🦞☀️😎"]
    respuestas_holandes = [f"¡HOLANDÉS {message.author.name}! ¡BOOO! 👻😂", f"¡Barco fantasma {message.author.name}! 👻🚢", f"¡Soy el Holandés {message.author.name}! 👻🧽", f"¡Amigo fantasma {message.author.name}! 👻💛", f"¡BOOO me asusté {message.author.name}! 👻😅", f"¡Tesoro sustos {message.author.name}! 👻💰", f"¡Nadie escapa dice {message.author.name}! 👻🫧", f"¡Barba verde {message.author.name}! 👻🧔💚"]
    respuestas_gary_n = [f"¡GARYYYY {message.author.name}! ¡Mi bebé! 🐌💛💛💛", f"¡Gary se escondió {message.author.name}! 🔍🐌", f"¡Gary miau te quiero {message.author.name}! 🐌💛", f"¡Gary lee libros {message.author.name}! 📚🐌", f"¡Gary come ñam ñam {message.author.name}! 🐌🍽️💛", f"¡Mochilita caparazón {message.author.name}! 🐌🎒✨", f"¡No te vayas Gary {message.author.name}! 🐌😭", f"¡Equipo caracol esponja {message.author.name}! 🐌🧽👯‍♂️", f"¡Gary duerme tierno {message.author.name}! 😴🐌💛", f"¡Gary precioso {message.author.name}! ¡El mejor! 🐌👑💛"]
        # --- PARTE 2 - Lugares y Cosas ---
    respuestas_pina = [f"¡Mi piña {message.author.name}! ¡Ven te invito! 🍍🏠💛", f"¡Piña debajo del mar {message.author.name}! 🍍🧽", f"¡Piña naranja sol {message.author.name}! 🍍☀️", f"¡Ventana piña hola {message.author.name}! 🍍👋🧽", f"¡3 cuartos piña {message.author.name}! 🍍🐌🧽", f"¡Amo mi piña hogar {message.author.name}! 🍍🏠💛", f"¡Piña brilla noche {message.author.name}! 🍍🌟", f"¡Piña y CangreBurger {message.author.name}! 🍍🍔💛"]
    respuestas_roca = [f"¡Roca Patricio {message.author.name}! ¡No es Bikini es Patricio! 🪨⭐😂", f"¡Roca se abre {message.author.name}! ¡Ahí está! 🪨👀", f"¡Roca sin nada {message.author.name}! ¡Solo palito! 🪨", f"¡Roca de mi amigo {message.author.name}! 🪨⭐💛", f"¡Toca roca Patricio {message.author.name}! 🪨🔔⭐"]
    respuestas_balde = [f"¡Balde Carnada puaj {message.author.name}! 🪣🤢", f"¡Nadie va al Balde {message.author.name}! 🪣🤮", f"¡Balde vacío {message.author.name}! 🪣😂", f"¡Balde solito {message.author.name}! 🪣🧽💛", f"¡Huele a calcetín {message.author.name}! 🪣🧦😂"]
    respuestas_formula = [f"¡Fórmula secreta {message.author.name}! ¡Lleva amor! 🤫💛🍔", f"¡Caja fuerte escondida {message.author.name}! 🔒🍔", f"¡Plankton no la tendrá {message.author.name}! 🤫🦠", f"¡Fórmula con Gary {message.author.name}! 🤫🐌💛", f"¡Secreto de jefes {message.author.name}! 🤫💰"]
    respuestas_medus = [f"¡MEDUSAS {message.author.name}! ¡A cazar! ¡Listo! 🪼🙋‍♂️", f"¡Campo Medusas favorito {message.author.name}! 🪼⭐", f"¡Medusita rosa te quiero {message.author.name}! 🪼💗💛", f"¡Medusas bailando brillan {message.author.name}! 🪼✨💃", f"¡Picadura auch pero feliz {message.author.name}! 🪼😅💛", f"¡Reina medusas gigante {message.author.name}! 👑🪼", f"¡Red lista vamos {message.author.name}! 🪼🪤⭐", f"¡Medusas woo woo {message.author.name}! 🪼🎶"]
    respuestas_karate = [f"¡KARATE {message.author.name}! ¡HI-YA! 🥋🐿️", f"¡Karate con Arenita {message.author.name}! 🐿️🥋💛", f"¡Patada voladora {message.author.name}! 🥋💥", f"¡Cinturón burbuja {message.author.name}! 🥋🫧", f"¡Chop chop {message.author.name}! 🥋✂️", f"¡Karate feliz sonrisa {message.author.name}! 🥋😊💛", f"¡Karate y medusas {message.author.name}! 🪼🥋", f"¡HI-YA Bob {message.author.name}! 🙋‍♂️🥋✨"]
    respuestas_burbujas = [f"¡BURBUJAS {message.author.name}! ¡Patito elefante! 🫧🦆🐘", f"¡Burbujas bonitas amor {message.author.name}! 🫧💛", f"¡Burbujas gigantes {message.author.name}! 🫧✨", f"¡Burbujas amistad regalo {message.author.name}! 🫧💛🎁", f"¡Mi hobby burbujas {message.author.name}! 🫧🧽", f"¡Burbujas corazón para ti {message.author.name}! 🫧💕", f"¡Burbujas colores arcoíris {message.author.name}! 🌈🫧", f"¡Pop burbuja {message.author.name}! 🫧💥😂"]
    respuestas_glove = [f"¡GUANTE WORLD {message.author.name}! ¡Vamos! 🎢🧤", f"¡Montaña rusa guantes {message.author.name}! 🎢🧤😲", f"¡Guante World divertido {message.author.name}! 🎢⭐🧽", f"¡Guante World helado guante {message.author.name}! 🍦🧤", f"¡Luces Guante World {message.author.name}! 🎢✨🧤", f"¡Mi favorito después Crustáceo {message.author.name}! 🏪🎢💛", f"¡Gorrito guante {message.author.name}! 🧢🧤😂", f"¡Gritos yuju Guante World {message.author.name}! 🎢📢😊"]
    respuestas_goo = [f"¡GOO LAGOON {message.author.name}! ¡Playa! 🏖️☀️", f"¡Goo Lagoon lodo Goo {message.author.name}! 🏖️😂", f"¡Larry en Goo Lagoon {message.author.name}! 🦞🏖️", f"¡Castillos arena Patricio {message.author.name}! 🏖️🏰⭐", f"¡Sol me quemo esponja {message.author.name}! ☀️🧽😂", f"¡Helado alga {message.author.name}! 🍦🏖️", f"¡Medusas en playa {message.author.name}! 🏖️🪼", f"¡Mi playa favorita {message.author.name}! 🏖️💛🧽"]
    respuestas_chocolate_n = [f"¡CHOCOLATE {message.author.name}! ¡CHOCOLATEEE! 🍫😍", f"¡Chocolate cacahuate ñam {message.author.name}! 🥜🍫", f"¡Patricio ama chocolate {message.author.name}! 🍫⭐", f"¡Chocolate gigante {message.author.name}! 🍫😲", f"¡CHOCOLATE grito Patricio {message.author.name}! 📢🍫", f"¡Chocolate oscuro blanco {message.author.name}! 🍫🤍🤎", f"¡Chocolate se derrite {message.author.name}! 🍫🏖️☀️", f"¡Chocolate con Gary miau {message.author.name}! 🐌🍫💛"]
        # --- PARTE 3 - Frases épicas ---
    respuestas_pierna = [f"¡MI PIERNA {message.author.name}! 🦵😱", f"¡Fred MI PIERNA siempre {message.author.name}! 🦵📢😂", f"¡Me caí pierna {message.author.name}! 🦵😅", f"¡Pierna baila {message.author.name}! 🦵💃", f"¡MI PIERNA y ESTOY LISTO {message.author.name}! 🦵🙋‍♂️", f"¡Pierna esponja estira {message.author.name}! 🦵🧽✨", f"¡Corriendo medusas pierna {message.author.name}! 🦵🪼🏃‍♂️", f"¡Pierna feliz contigo {message.author.name}! 🦵👯‍♂️💛"]
    respuestas_cacahuate = [f"¡SOY UN CACAHUATE {message.author.name}! 🥜😂", f"¡Cacahuate power {message.author.name}! 🥜✨", f"¡Cacahuate chocolate mejor {message.author.name}! 🥜🍫", f"¡Cacahuate salado mar {message.author.name}! 🥜🌊", f"¡Cacahuate gigante Patricio {message.author.name}! 🥜⭐", f"¡Cacahuate chiquito Plankton {message.author.name}! 🥜🦠", f"¡Cacahuate feliz saltando {message.author.name}! 🥜😊", f"¡Equipo cacahuate Bob {message.author.name}! 🥜🧽👯‍♂️"]
    respuestas_imaginacion_n = [f"¡IMAGINACIÓN {message.author.name}! 🌈✨", f"¡Con imaginación todo {message.author.name}! 🌈💭", f"¡Arcoíris imaginación {message.author.name}! 🌈👀", f"¡Puedo volar avión {message.author.name}! ✈️🌈", f"¡Imaginación burbujas mejor {message.author.name}! 🌈🫧", f"¡Colores imaginación {message.author.name}! 🌈🎨", f"¡Sin fin amistad {message.author.name}! 🌈♾️💛", f"¡Gary miau imaginación {message.author.name}! 🐌🌈💭"]
    respuestas_listo = [f"¡ESTOY LISTO {message.author.name}! ¡ESTOY LISTO! 🙋‍♂️✨", f"¡Estoy listo siempre {message.author.name}! 🙋‍♂️💛", f"¡ESTOY LISTOOO fuerte {message.author.name}! 🔊🧽", f"¡Estoy listo tristeza te vas {message.author.name}! 🥺🍍", f"¡Listo trabajo Crustáceo {message.author.name}! 🍔🏪🙋‍♂️", f"¡Listo medusas {message.author.name}! 🪼🙋‍♂️", f"¡Listo karate {message.author.name}! 🥋🙋‍♂️", f"¡Listo burbujas {message.author.name}! 🫧🙋‍♂️", f"¡Listo CangreBurgers {message.author.name}! 🍔🙋‍♂️", f"¡Listo y feliz {message.author.name}! 😊🙋‍♂️✨"]
    respuestas_dona = [f"¡Mi dona chocolate {message.author.name}! ¡Patricio se la comió! 🍩⭐😭", f"¡Dona glaseada chispas {message.author.name}! 🍩✨", f"¡Quiero mi dona {message.author.name}! ¡Devuélvela Patricio! 🍩⭐", f"¡Dona de Bob {message.author.name}! ¡Mi favorita! 🍩💛🧽", f"¡Dona con amor {message.author.name}! 🍩💛"]
    respuestas_tartar = [f"¡Tartar salsa {message.author.name}! ¡Mala palabra! 🤬🤐", f"¡No digas tartar salsa {message.author.name}! 🤬", f"¡Shhh delfines escuchan {message.author.name}! 🐬🤐😂", f"¡Dijiste tartar {message.author.name}! ¡Ohhh! 🤐", f"¡Tartar salsa no se dice {message.author.name}! 🤬💛"]
    respuestas_mejor_dia = [f"¡Mejor día de todos {message.author.name}! ¡Sol sonrió! ☀️🎶💛", f"¡Hoy mejor día {message.author.name}! ¡Como siempre! ☀️🧽", f"¡Mejor día con Patricio Gary {message.author.name}! ☀️⭐🐌", f"¡El mejor día contigo {message.author.name}! ☀️👯‍♂️💛", f"¡Mejor día canción {message.author.name}! 🎶☀️🧽"]
    respuestas_kevin = [f"¡KEVIN pepino inteligente {message.author.name}! 🥒🧠", f"¡Kevin presumido {message.author.name}! 🥒😏", f"¡Club pepinos Kevin {message.author.name}! 🥒🤓", f"¡Hola Kevin {message.author.name}! ¡Quiero ser tu club! 🥒🥺💛", f"¡Pepino Kevin cool {message.author.name}! 🥒✨"]
    respuestas_neptuno = [f"¡REY NEPTUNO {message.author.name}! ¡Rey del mar! 👑🔱", f"¡Tridente poderoso {message.author.name}! 🔱👑💪", f"¡Neptuno calvo shhh {message.author.name}! 👑😂", f"¡Por poder Neptuno {message.author.name}! 👑🔱✨", f"¡Neptuno calzones rosas {message.author.name}! 👑👙😂"]
    respuestas_barnaculo = [f"¡Oh barnáculo {message.author.name}! ¡Problemas! 🤬🧽", f"¡Oh barnáculo Fred y yo {message.author.name}! 🤬", f"¡Barnáculo no puedo {message.author.name}! 🤬😂", f"¡Dije barnáculo {message.author.name}! 🤐🤬", f"¡Oh barnáculo feliz {message.author.name}! 🤬✨😊"]
        # --- PARTE 4 - Héroes + CangreBurgers ---
    respuestas_sireno = [f"¡SIRENO MAN {message.author.name}! ¡Mi héroe! ¡EVIL! 🦸‍♂️👴✨", f"¡Sireno Man Chico Percebe ídolos {message.author.name}! 🦸‍♂️👓💛", f"¡A la baticueva Sireno {message.author.name}! 🦸‍♂️🏪", f"¡Sireno viejito fuerte {message.author.name}! 🦸‍♂️💪👴", f"¡El bien gana {message.author.name}! 💛🦸‍♂️", f"¡Capa toalla Sireno {message.author.name}! 🦸‍♂️🧽😂", f"¡Cinturón ZAP BAM {message.author.name}! 💥🦸‍♂️", f"¡Firma mi espátula {message.author.name}! 🦸‍♂️✍️🍳", f"¡EL MAL detener {message.author.name}! 🦹‍♂️🦸‍♂️", f"¡Asilo héroes cool {message.author.name}! 🦸‍♂️🏠👴"]
    respuestas_chico = [f"¡CHICO PERCEBE {message.author.name}! ¡Compañero Sireno! 👓🦸‍♂️⭐💛", f"¡Chico lentes inteligente {message.author.name}! 👓🧠", f"¡Sireno Man mira dice {message.author.name}! 👓⭐", f"¡Chico joven como yo {message.author.name}! 👓🙋‍♂️", f"¡Equipo super como nosotros {message.author.name}! 👓🦸‍♂️🧽⭐", f"¡Me saludó Chico {message.author.name}! 👓💛😊", f"¡Gorrito bonito Chico {message.author.name}! 👓🧢✨", f"¡Lucha contra mal {message.author.name}! 🦹‍♂️👓🦸‍♂️", f"¡EVIL dice también {message.author.name}! 👓😂", f"¡Mejor ayudante {message.author.name}! 👓🏆💛"]
    respuestas_mal = [f"¡EL MAAAAL {message.author.name}! ¡Detener mal! 🦸‍♂️🦹‍♂️🙋‍♂️", f"¡EVIL grita Sireno {message.author.name}! 🦸‍♂️😂💛", f"¡Mal nunca gana {message.author.name}! 🦸‍♂️🦹‍♂️💛", f"¡EL MAL con Sireno {message.author.name}! 🦸‍♂️🦹‍♂️✨", f"¡Vamos contra EL MAL {message.author.name}! ¡Listo! 🦹‍♂️🙋‍♂️"]
    respuestas_cangre_extra1 = [f"¡CANGREBURGER {message.author.name}! ¡Con amor Bob! 🍔💛🧽✨", f"¡Calientita recién salida {message.author.name}! 🍔🔥💛", f"¡Con queso se derrite {message.author.name}! 🍔🧀😊", f"¡Mejor del océano yo mero {message.author.name}! 🍔🙋‍♂️", f"¡Doble con pepinillos {message.author.name}! 🍔🥒", f"¡Otra y otra no paro {message.author.name}! 🍔🍔🍔", f"¡Para mi amigo extra Bob {message.author.name}! 🍔🧽✨", f"¡Cantando CangreBurger {message.author.name}! 🎶🍔"]
    respuestas_cangre_extra2 = [f"¡Gigante más grande piña {message.author.name}! 🍔🍍😲", f"¡20 como Patricio {message.author.name}! 🍔⭐", f"¡Colores arcoíris {message.author.name}! 🌈🍔", f"¡Medianoche amor nocturno {message.author.name}! 🌙🍔", f"¡Picante karate {message.author.name}! 🍔🔥🥋", f"¡Dorada brilla espátula {message.author.name}! 🍔✨🍳", f"¡Voladora burbujas {message.author.name}! 🍔🫧", f"¡Sorpresa tiene amor {message.author.name}! 🍔🎁💛"]
    respuestas_cangre_extra3 = [f"¡Fórmula amor amistad {message.author.name}! 🤫💛🍔", f"¡100 Estoy listo {message.author.name}! 🙋‍♂️🍔", f"¡Sin CangreBurgers no hay Bob {message.author.name}! 🍔🧽💛", f"¡Amor ingrediente secreto {message.author.name}! 💛🍔", f"¡Para Fondo Bikini invito {message.author.name}! 🍔🌊💰😂", f"¡Y refresco sonrisa gratis {message.author.name}! 🍔🥤😊", f"¡Manitas cuadradas hice {message.author.name}! 🍔🧽👋", f"¡Perfecta redonda feliz {message.author.name}! 🍔😊🧽"]
    respuestas_mucha_cangre = [f"¡MONTAÑA CANGREBURGERS {message.author.name}! 🍔⛰️🤤", f"¡Lluvia CangreBurgers abre boca {message.author.name}! 🍔🌧️😋", f"¡Muchas fiesta {message.author.name}! 🍔🍔🎉💛", f"¡Por todos lados piña cama corazón {message.author.name}! 🍍💛🍔", f"¡Infinita amistad {message.author.name}! 🍔♾️💛🧽", f"¡Desayuno comida cena {message.author.name}! 🍔🌅🌙", f"¡Extra todo extra Bob {message.author.name}! 🍔✨🧽💛", f"¡Volando medusas burgers {message.author.name}! 🍔🪼😂"]
    respuestas_fondo_cangre = [f"¡Crustáceo Cascarudo casa {message.author.name}! 🍔🏪💛🙋‍♂️", f"¡Huele a CangreBurger felicidad {message.author.name}! 🍔👃💛", f"¡Mi segundo hogar parrilla {message.author.name}! 🍔🏠", f"¡Crustáceo solo CangreBurgers {message.author.name}! 🍔🏪", f"¡Crustáceo brilla {message.author.name}! 🍔✨🏪"]

    # --- PREGUNTAS CON RANDOM - PEGALO AL FINAL DE TODO ---
    if "que es para ti patricio" in texto or "quien es patricio" in texto:
        resp = random.choice(respuestas_patricio)
    elif "que es para ti calamardo" in texto:
        resp = random.choice(respuestas_calamardo)
    elif "que es para ti arenita" in texto:
        resp = random.choice(respuestas_arenita)
    elif "que es para ti don cangrejo" in texto or "que es para ti cangrejo" in texto and "burger" not in texto:
        resp = random.choice(respuestas_don_cangrejo_n)
    elif "que es para ti plankton" in texto:
        resp = random.choice(respuestas_plankton_n)
    elif "que es para ti perlita" in texto:
        resp = random.choice(respuestas_perlita)
    elif "que es para ti sra puff" in texto or "que es para ti puff" in texto:
        resp = random.choice(respuestas_sra_puff)
    elif "que es para ti larry" in texto:
        resp = random.choice(respuestas_larry)
    elif "que es para ti holandes" in texto:
        resp = random.choice(respuestas_holandes)
    elif "que es para ti gary" in texto:
        resp = random.choice(respuestas_gary_n)
    elif "que es para ti sireno" in texto:
        resp = random.choice(respuestas_sireno)
    elif "que es para ti chico percebe" in texto:
        resp = random.choice(respuestas_chico)
    elif "que es para ti cangreburger" in texto:
        resp = random.choice(respuestas_cangre_extra1 + respuestas_cangre_extra2 + respuestas_cangre_extra3)

    elif "patricio" in texto: resp = random.choice(respuestas_patricio)
    elif "calamardo" in texto: resp = random.choice(respuestas_calamardo)
    elif "arenita" in texto: resp = random.choice(respuestas_arenita)
    elif "don cangrejo" in texto or "cangrejo" in texto and "burger" not in texto: resp = random.choice(respuestas_don_cangrejo_n)
    elif "plankton" in texto: resp = random.choice(respuestas_plankton_n)
    elif "perlita" in texto: resp = random.choice(respuestas_perlita)
    elif "sra puff" in texto or "puff" in texto: resp = random.choice(respuestas_sra_puff)
    elif "larry" in texto: resp = random.choice(respuestas_larry)
    elif "holandes" in texto: resp = random.choice(respuestas_holandes)
    elif "gary" in texto: resp = random.choice(respuestas_gary_n)
    elif "piña" in texto or "pina" in texto: resp = random.choice(respuestas_pina)
    elif "roca" in texto: resp = random.choice(respuestas_roca)
    elif "balde" in texto: resp = random.choice(respuestas_balde)
    elif "formula" in texto: resp = random.choice(respuestas_formula)
    elif "medusa" in texto: resp = random.choice(respuestas_medusas)
    elif "karate" in texto: resp = random.choice(respuestas_karate)
    elif "burbuja" in texto: resp = random.choice(respuestas_burbujas)
    elif "guante" in texto: resp = random.choice(respuestas_glove)
    elif "goo" in texto: resp = random.choice(respuestas_goo)
    elif "chocolate" in texto: resp = random.choice(respuestas_chocolate_n)
    elif "pierna" in texto: resp = random.choice(respuestas_pierna)
    elif "cacahuate" in texto: resp = random.choice(respuestas_cacahuate)
    elif "imaginacion" in texto: resp = random.choice(respuestas_imaginacion_n)
    elif "estoy listo" in texto: resp = random.choice(respuestas_listo)
    elif "dona" in texto: resp = random.choice(respuestas_dona)
    elif "tartar" in texto: resp = random.choice(respuestas_tartar)
    elif "mejor dia" in texto: resp = random.choice(respuestas_mejor_dia)
    elif "kevin" in texto: resp = random.choice(respuestas_kevin)
    elif "neptuno" in texto: resp = random.choice(respuestas_neptuno)
    elif "barnaculo" in texto: resp = random.choice(respuestas_barnaculo)
    elif "sireno" in texto: resp = random.choice(respuestas_sireno)
    elif "percebe" in texto: resp = random.choice(respuestas_chico)
    elif "el mal" in texto: resp = random.choice(respuestas_mal)
    elif "cangreburger" in texto: resp = random.choice(respuestas_cangre_extra1 + respuestas_cangre_extra2 + respuestas_cangre_extra3 + respuestas_mucha_cangre)
    elif "crustaceo" in texto or "cascarudo" in texto: resp = random.choice(respuestas_fondo_cangre)
    
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
ya_sincronizado = False

@bot.event
async def on_ready():
    global ya_sincronizado
    if ya_sincronizado:
        return
    ya_sincronizado = True
    if not revisar_cumples.is_running():
        revisar_cumples.start()
    print(f"Bob conectado: {bot.user}")
    try:
        # Sincroniza instantáneo en cada servidor donde está Bob
        for guild in bot.guilds:
            try:
                await bot.tree.sync(guild=guild)
                print(f"Slash sincronizados en {guild.name}")
            except Exception as e:
                print(f"Error en {guild.name}: {e}")
        # También global por si acaso
        synced = await bot.tree.sync()
        print(f"Slash globales: {len(synced)}")
    except Exception as e:
        print(e)

TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
bot.run(TOKEN)
