import discord, random, os, yt_dlp, asyncio, re
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

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Listo {bot.user}")

@bot.tree.command(name="caracola_magica", description="Preguntale a la caracola mágica")
async def caracola_magica(interaction: discord.Interaction, pregunta: str):
    r = ["Sí 🐚", "No 🐚", "Tal vez algún día", "Definitivamente sí ✨", "Ni de broma 💀", "Obvio que sí", "Obvio que no"]
    await interaction.response.send_message(embed=discord.Embed(title="🐚 CARACOLA MÁGICA", description=f"**Pregunta:** {pregunta}\n**Respuesta:** {random.choice(r)}", color=0xf1c40f))

@bot.tree.command(name="caracola_vdd", description="La caracola te dice una verdad")
async def caracola_vdd(interaction: discord.Interaction):
    v = ["Manda la última foto de tu galería", "Di quién te gusta de verdad", "Di tu última mentira", "Muestra tu fondo de pantalla"]
    await interaction.response.send_message(embed=discord.Embed(title="🐚 CARACOLA DE LA VERDAD", description=random.choice(v), color=0x9b59b6))

@bot.tree.command(name="caracola_destino", description="Tu destino por un día en Fondo de Bikini")
async def caracola_destino(interaction: discord.Interaction):
    d = ["Hoy eres Don Cangrejo 🦀", "Hoy eres Bob Esponja 🧽", "Hoy eres Patricio ⭐", "Hoy eres Calamardo 🦑"]
    await interaction.response.send_message(embed=discord.Embed(title="🐚 TU DESTINO", description=random.choice(d), color=0x3498db))

@bot.tree.command(name="youtube", description="Busca un video de YouTube")
async def youtube(interaction: discord.Interaction, buscar: str):
    busqueda = buscar.replace(" ", "+")
    await interaction.response.send_message(embed=discord.Embed(title="🔍 BUSCADOR DE GARY 🐌", description=f"Buscaste: **{buscar}**\n▶️ https://www.youtube.com/results?search_query={busqueda}", color=0xFF0000))

@bot.tree.command(name="radio_fondo_bikini", description="Pon radio en tu canal de voz 📻")
async def radio_fondo_bikini(interaction: discord.Interaction, estacion: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ ¡Métete a un canal de voz primero! 🎺", ephemeral=True)
        return
    if estacion not in RADIOS:
        await interaction.response.send_message(f"❌ Estaciones: {', '.join(RADIOS.keys())}", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        canal = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc and vc.is_connected(): await vc.move_to(canal)
        else: vc = await canal.connect()
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(RADIOS[estacion], download=False)
            url = info['url']
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
        await interaction.followup.send(f"📻 **¡Radio {estacion} ON!** en {canal.mention}")
    except Exception as e:
        print(e)
        await interaction.followup.send("❌ No pude poner la radio.")

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
        ydl_opts = {'format': 'bestaudio/best','outtmpl': '/tmp/%(title)s.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',}],'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            archivo = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            titulo = info.get('title', 'Cangreburger')
        if os.path.getsize(archivo) > 25*1024*1024:
            await interaction.followup.send("❌ Pesa más de 25MB")
            os.remove(archivo)
            return
        await interaction.followup.send(f"🍔 **{titulo}** ¡Provecho! 😋", file=discord.File(archivo))
        os.remove(archivo)
    except Exception as e:
        print(e)
        await interaction.followup.send("❌ No pude descargar ese link.")

@bot.tree.command(name="cangreburger_spotify", description="Pide tu canción de Spotify para llevar 🎵")
async def cangreburger_spotify(interaction: discord.Interaction, link_spotify: str):
    await interaction.response.defer()
    await interaction.followup.send("🎵 ¡Gary está buscando tu canción en Spotify... 🐌")
    try:
        ydl_opts_info = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info_spotify = ydl.extract_info(link_spotify, download=False)
            titulo_spotify = info_spotify.get('title', '')
            artista = info_spotify.get('artist', '') or info_spotify.get('creator', '')
            busqueda = f"{artista} {titulo_spotify}".strip()
            if not busqueda or len(busqueda) < 3:
                busqueda = titulo_spotify
        await interaction.followup.send(f"🔍 Encontré: **{busqueda}**\n🍔 Ahora lo estoy cocinando...")
        ydl_opts = {'format': 'bestaudio/best','outtmpl': '/tmp/%(title)s.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',}],'quiet': True,'default_search': 'ytsearch1','noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{busqueda}", download=True)
            if 'entries' in info:
                info = info['entries'][0]
            archivo = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            titulo = info.get('title', busqueda)
        if os.path.getsize(archivo) > 25*1024*1024:
            await interaction.followup.send("❌ Pesa más de 25MB")
            os.remove(archivo)
            return
        await interaction.followup.send(f"🎵 **{titulo}** ¡Tu Cangreburger musical lista! 🍔", file=discord.File(archivo))
        os.remove(archivo)
    except Exception as e:
        print(e)
        await interaction.followup.send("❌ No pude encontrar esa canción de Spotify.")

@bot.tree.command(name="roles", description="Panel de Color Burguers")
async def roles(interaction: discord.Interaction):
    tiene_owner = discord.utils.get(interaction.user.roles, name=ROL_OWNER)
    tiene_admin = discord.utils.get(interaction.user.roles, name=ROL_ADMIN)
    if not tiene_owner and not tiene_admin and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(f"❌ Solo jefes", ephemeral=True)
        return
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
    if not payload.member or payload.member.bot or payload.emoji.name not in ROLES_MAP: return
    g = bot.get_guild(payload.guild_id)
    rol = discord.utils.get(g.roles, name=ROLES_MAP[payload.emoji.name])
    if rol: await payload.member.add_roles(rol)

@bot.event
async def on_raw_reaction_remove(payload):
    g = bot.get_guild(payload.guild_id)
    m = g.get_member(payload.user_id)
    if not m or m.bot or payload.emoji.name not in ROLES_MAP: return
    rol = discord.utils.get(g.roles, name=ROLES_MAP[payload.emoji.name])
    if rol: await m.remove_roles(rol)

# ========== JUEGOS FONDO DE BIKINI ==========
class CazaMedusasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.cazadas = 0
    @discord.ui.button(label="¡CAZAR!", style=discord.ButtonStyle.primary, emoji="🪼")
    async def cazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cazadas += 1
        await interaction.response.send_message(f"¡Cazaste {self.cazadas}/5 medusas! 🪼", ephemeral=True)
        if self.cazadas >= 5:
            self.stop()
            await interaction.followup.send(f"🏆 ¡{interaction.user.mention} cazó 5 medusas! ¡Eres el mejor!")

class GaryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.pos = random.randint(0, 8)
        for i in range(9):
            btn = discord.ui.Button(label="❓", style=discord.ButtonStyle.secondary, custom_id=str(i))
            btn.callback = self.buscar
            self.add_item(btn)
    async def buscar(self, interaction: discord.Interaction):
        if int(interaction.data["custom_id"]) == self.pos:
            await interaction.response.send_message(f"¡{interaction.user.mention} ENCONTRÓ A GARY! 🐌💛 ¡Miau!")
            self.stop()
        else:
            await interaction.response.send_message("¡No está ahí! 👀", ephemeral=True)

@bot.tree.command(name="caza_medusas", description="¡Caza 5 medusas! 🪼")
async def caza_medusas(interaction: discord.Interaction):
    view = CazaMedusasView()
    await interaction.response.send_message("🪼 ¡LAS MEDUSAS ESCAPARON! ¡Dale al botón 5 veces para cazarlas!", view=view)

@bot.tree.command(name="busca_a_gary", description="¡Encuentra a Gary! 🐌")
async def busca_a_gary(interaction: discord.Interaction):
    view = GaryView()
    await interaction.response.send_message("🐌 ¡Gary se escondió! ¡Hay 9 casitas, toca una!", view=view)

@bot.tree.command(name="piedra_papel_tijera", description="Juega con Patricio ⭐")
async def piedra_papel_tijera(interaction: discord.Interaction, eleccion: str):
    opciones = ["piedra", "papel", "tijera"]
    eleccion = eleccion.lower()
    if eleccion not in opciones:
        await interaction.response.send_message("Usa: piedra, papel o tijera", ephemeral=True)
        return
    bot_c = random.choice(opciones)
    res = "Empate 😐"
    if (eleccion == "piedra" and bot_c == "tijera") or (eleccion == "papel" and bot_c == "piedra") or (eleccion == "tijera" and bot_c == "papel"):
        res = "¡Ganaste! 🎉"
    elif eleccion!= bot_c:
        res = "¡Patricio ganó! ⭐ es un genio"
    await interaction.response.send_message(f"Tú: **{eleccion}** vs Patricio: **{bot_c}**\n{res}")

@bot.tree.command(name="trivia_bikini", description="Trivia de Bob Esponja 🧽")
async def trivia_bikini(interaction: discord.Interaction):
    preguntas = [
        ("¿Cómo se llama el vecino de Bob que toca clarinete?", ["Calamardo", "Patricio", "Don Cangrejo"], 0),
        ("¿Dónde vive Bob Esponja?", ["En una piña", "En una roca", "En un castillo"], 0),
        ("¿Qué odia Calamardo?", ["A Bob", "Las Cangreburgers", "Todo lo anterior"], 2),
        ("¿Cómo se llama la mascota de Bob?", ["Gary", "Larry", "Coco"], 0),
    ]
    q, ops, corr = random.choice(preguntas)
    embed = discord.Embed(title="🧠 TRIVIA BIKINI", description=f"**{q}**\n\n🔵 {ops[0]}\n🟣 {ops[1]}\n🟢 {ops[2]}", color=0xFFFF00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="atrapa_cangreburger", description="¡Atrapa la Cangreburger! 🍔")
async def atrapa_cangreburger(interaction: discord.Interaction):
    await interaction.response.send_message("🍔 ¡La Cangreburger está cayendo! ¡Escribe **ATRAPAR** en el chat en 5 segundos!")
    def check(m): return m.channel == interaction.channel and "atrapar" in m.content.lower() and not m.author.bot
    try:
        msg = await bot.wait_for('message', check=check, timeout=5.0)
        await interaction.followup.send(f"¡{msg.author.mention} ATRAPÓ LA CANGREBURGER! 🍔🏆")
    except asyncio.TimeoutError:
        await interaction.followup.send("💀 ¡Se cayó! Nadie la atrapó!")

# ========== FIN JUEGOS ==========

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        texto_original = message.content.strip()
        texto = texto_original.lower()
        
        async with message.channel.typing():
            await asyncio.sleep(random.uniform(0.9, 1.6))

            chistes_bob = [
                "¿Qué le dijo una Cangreburger a otra? ¡Qué pan contigo! 🍔",
                "Patricio: ¿Qué es más divertido que 24? ¡25! ⭐",
                "¿Por qué Calamardo no juega a escondidas? ¡Siempre lo encuentran amargado! 🦑",
                "¡Toc toc! ¿Quién es? ¡Yo! ¿Yo quién? ¡Yo estoy liiiiisto! 🧽",
                "¿Por qué Gary no usa celular? ¡Prefiere el Gari-mail! 🐌",
                "Don Cangrejo: ¡Amo el dinero! Yo: ¡Yo amo la amistad!",
                "¿Qué hace Bob con frío? ¡Se pone doble corbatita! 👔",
                "¡Mi lápiz de imaginación dibujó 20 chistes! 🖍️🌈",
                "¿Qué hace Gary el domingo? ¡Dice miau! 🐌",
                "¡Vivo en una piña debajo del mar! 🍍",
                "Patricio: ¡El interior de mi cabeza da miedo!",
                "Sra Puff: ¡Reprobaste! Yo: ¡Estoy listo para reprobar otra vez! ⛵",
                "¿Por qué Patricio llevó escalera? ¡Quería llegar alto!",
                "¡Imagiiiinación! 🌈",
                "¿Qué hace Bob en el gym? ¡Esponjaguetis!",
                "Calamardo tocó clarinete y todos nos fuimos 🎶",
                "Plankton: ¡Robaré la fórmula! Karen: ¡Lava trastes!",
                "¿Qué le dijo el mar a la esponja? ¡Ola!",
                "Arenita: ¡No seas tonto Bob! Yo: ¡Soy Bob el tonto!",
                "¡Estoy listo para contarte otro chiste! 😂"
            ]

            if re.match(r'^[\d\s\+\-\*\/\(\)\.x\^%]+$', texto) and any(c in texto for c in "0123456789"):
                try:
                    formula = texto.replace('x', '*').replace('^', '**')
                    resultado = eval(formula, {"__builtins__": {}})
                    await message.channel.send(f"¡Con mi lápiz de imaginación! {texto_original} = **{resultado}** 🧠")
                    return
                except: pass

            if any(p in texto for p in ["chiste", "broma", "hazme reir"]):
                await message.channel.send(random.choice(chistes_bob))
                return

            # CON CARISMA DE BOB - YO TAMBIEN TE QUIERO Y TODO ESTARA BIEN
            if any(p in texto for p in ["te quiero", "te amo", "tqm", "te kiero", "tkm", "love you"]):
                await message.channel.send(random.choice([
                    f"¡Awww {message.author.name}! ¡Yo también te quiero muchísimo! 💛 ¡Eres mi mejor amigo de todo Fondo de Bikini! ¡Abrazo de esponja bien apretado! 🧽🍍",
                    "¡Yo también te quiero con todo mi corazón de esponja! ¡Más que a las Cangreburgers! ¡Tú y yo amigos por siempre como yo y Patricio! ⭐💛",
                    f"¡{message.author.name}! ¡Yo también te quiero! ¡Me haces sentir el mejor día del mundo! ¡Gracias por ser mi amigo! 🥺💛"
                ]))
                return

            if any(p in texto for p in ["me siento mal", "me siento triste", "estoy triste", "estoy mal", "me siento solo", "estoy solo", "quiero llorar", "estoy deprimido", "tengo ansiedad", "no puedo mas"]):
                await message.channel.send(random.choice([
                    f"Holaaaa {message.author.name}! 🥺💛 ¡Nooo no estés triste! Siento mucho que te sientas así. ¡Ven, te doy un abracito de piña! 🍍 ¡Todo estará bien, te lo prometo! Como dice Gary ¡Miau! que significa ¡Te quiero!",
                    f"¡Ey {message.author.name}! ¡Yo estoy aquí! 🧽 ¡No te preocupes, todo estará bien! ¿Has visto a Arenita? ¡Ella dice que cuando estoy triste haga karate! 🥋 ¿Quieres que hagamos algo juntos? Podemos: 🎶 escuchar música, 🖍️ dibujar con mi lápiz de imaginación, 🪼 cazar medusas, o 🍔 comer Cangreburgers imaginarias. ¿Qué te late más?",
                    f"¡Ohhh {message.author.name}! ¡Mi corazón de esponja se pone chiquito al leerte así! 💛 Pero escúchame, ¡eres increíble! ¡Más increíble que la caja secreta de Patricio! Todo estará bien, aunque ahora no se sienta así. ¿Quieres dibujar un ratito conmigo? ¡Yo dibujo a Gary y tú dibujas lo que sientas! 🎨🐌",
                    f"Holaaaa! ¡Soy Bob! 🧽 ¡Gracias por decirme que te sientes mal, eso es de valientes! No tienes que estar feliz siempre. Si te sientes muy cargado, habla con alguien de confianza, a mí me ayuda hablar con Patricio. Yo aquí sigo contigo. ¿Ponemos musiquita de Fondo de Bikini y respiramos juntos? 🌊💛 ¡Yo también te quiero mucho!"
                ]))
                return

            if any(p in texto for p in ["hola", "ola", "hey", "buenas", "holi", "que onda", "wenas"]):
                await message.channel.send(random.choice([
                    f"¡Holaaaaa {message.author.name}! 🍍 ¡Estoy liiiiisto! ¿Has visto a Patricio? ¡Se escondió otra vez! ⭐",
                    f"¡Holaaaa! ¡Soy Bob Esponja! 🧽 ¡Vivo en una piña debajo del mar! ¿Has visto a Arenita? ¡Me enseñó karate! 🥋",
                    f"¡Holaaaaa {message.author.name}! ¡Qué bueno verte! ¿Has visto a Gary? ¡Dijo miau! 🐌 ¡Significa hola!",
                ]))
                return

            if any(p in texto for p in ["arenita", "patricio", "calamardo", "gary", "don cangrejo"]):
                await message.channel.send(f"¡Amooo a {texto_original}! ¡Es mi amiguito! ¡Vamos a jugar con él en Fondo de Bikini! ¿Quieres? 🍍🥳 ¡Yo también te quiero por jugar conmigo!")
                return

            # Respuesta general con carisma
            await message.channel.send(random.choice([
                f"¡Órale! ¿{texto_original}? ¡Eso suena a aventura! ¡Como cuando fui con Patricio a buscar la corona! ⭐ ¿Y luego qué pasó? Te escucho 💛",
                f"¡Wuju! ¡{texto_original}! ¡Me imagino con mi cerebro de esponja! 🌈 ¡Cuéntame más, estoy listísimo!",
                f"¡Jajaja! ¡Lo de '{texto_original}' me dio risa de esponja! 😂 ¡Eres bien divertido {message.author.name}! ¡Yo también te quiero por hacerme reír!",
                f"¡Holaaaa! ¿{texto_original}? ¡No lo había pensado! ¡Vamos a preguntarle a Arenita, ella es inteligente! 🤠 ¡Tú y yo somos gran equipo!"
            ]))
        return

    await bot.process_commands(message)
keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
bot.run(TOKEN)
