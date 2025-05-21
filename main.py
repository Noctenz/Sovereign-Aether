import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
from pytz import timezone
import asyncio
import logging
import os
import json
import random
import string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set up logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# File paths
REPUTATION_FILE = 'reputation.json'
POINTS_FILE = 'points.json'
DAILY_LOG_FILE = 'daily_log.json'
PRODUCT_FILE = 'products.json'
PURCHASE_FILE = 'purchases.json'
ALLOWED_CHANNEL_ID = 1374323715445096479

# Reputation counter
if os.path.exists(REPUTATION_FILE):
    with open(REPUTATION_FILE, 'r') as f:
        reputation_counter = json.load(f).get('counter', 0)
else:
    reputation_counter = 0

def save_reputation(count):
    with open(REPUTATION_FILE, 'w') as f:
        json.dump({'counter': count}, f)

def load_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_points(points):
    with open(POINTS_FILE, 'w') as f:
        json.dump(points, f, indent=4)

def load_daily_log():
    if os.path.exists(DAILY_LOG_FILE):
        with open(DAILY_LOG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_daily_log(log):
    with open(DAILY_LOG_FILE, 'w') as f:
        json.dump(log, f, indent=4)

def load_products():
    if os.path.exists(PRODUCT_FILE):
        with open(PRODUCT_FILE, 'r') as f:
            return json.load(f)
    return {}

def generate_code(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def load_purchases():
    if os.path.exists(PURCHASE_FILE):
        with open(PURCHASE_FILE, 'r') as f:
            return json.load(f)
    return []

def save_purchases(purchases):
    with open(PURCHASE_FILE, 'w') as f:
        json.dump(purchases, f, indent=4)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!payment"))
    print(f"We are ready to go in, {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
    send_auto_message.start()

@tasks.loop(minutes=1)
async def send_auto_message():
    now = datetime.now(timezone('Asia/Jakarta'))
    current_time = now.strftime('%H:%M')
    target_times = {
        '06:00': "🌅 **Selamat Pagi!** - Auto Message\nSemoga harimu menyenangkan. Jangan lupa sarapan ya! 🍳\n\nDelete in 30m",
        '12:00': "☀️ **Selamat Siang!** - Auto Message\nIstirahat sejenak dari aktivitasmu. Jangan lupa makan siang! 🍛\n\nDelete in 30m",
        '19:00': "🌙 **Selamat Malam!** - Auto Message\nSaatnya istirahat setelah hari yang panjang. Selamat beristirahat! 😴\n\nDelete in 30m"
    }

    if current_time in target_times:
        channel_id = 1236499828205289494 
        channel = bot.get_channel(channel_id)
        if channel:
            message = await channel.send(target_times[current_time])
            await asyncio.sleep(1800)
            await message.delete()

@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title=f"🌟 Welcome to Sovereign Studio {member.display_name}!",
        description=(
            "Thank you for visiting Sovereign Studio - The best place to find your favorite products!\n\n"
            "Don't hesitate to ask if there's anything you want to know. We're here to help make your shopping experience even more exciting!\n"
            "Need help? Just open a ticket. I'm ready to help whenever you need it.\n\n"
            "See you in blocky world of adventure~ 🎉"
        ),
        color=0x1c1c1c
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1236494866544852993/1372895940754804846/Live.gif")
    embed.set_footer(text="© 2025 Sovereign Studio")
    await member.send(embed=embed)

@bot.command()
async def payment(ctx):
    embed = discord.Embed(
        title="<:ss:1343504117468889119> | Sovereign Studio - Payment",
        color=0xd4c32c
    )
    embed.add_field(name="<:WhiteSmallDot:1316762166262497301> Paypal", value="```ma8421714@gmail.com```", inline=False)
    embed.add_field(name="<:WhiteSmallDot:1316762166262497301> Dana / Gopay", value="```089570444574```", inline=True)
    embed.add_field(name="<:WhiteSmallDot:1316762166262497301> SeaBank", value="```981176108251```", inline=True)
    embed.add_field(name="<:WhiteSmallDot:1316762166262497301> Qris - Indonesia, Malaysia, Singapore", value="```(Qris All payment Bank / E-Wallet)```", inline=False)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1334061169492754432/1361904906990129232/1744773816618.png")
    await ctx.send(embed=embed)

@bot.tree.command(name="reps", description="Send feedback")
@app_commands.describe(
    stars="Number of stars (1-5)",
    reviewmessage="Customer review message"
)
@app_commands.choices(
    stars=[
        app_commands.Choice(name="⭐", value=1),
        app_commands.Choice(name="⭐⭐", value=2),
        app_commands.Choice(name="⭐⭐⭐", value=3),
        app_commands.Choice(name="⭐⭐⭐⭐", value=4),
        app_commands.Choice(name="⭐⭐⭐⭐⭐", value=5),
    ]
)
async def reps(interaction: discord.Interaction, stars: app_commands.Choice[int], reviewmessage: str):
    if interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message("<:1476redsmalldot:1316385340180664373> You can only use this command on <#1374323715445096479>", ephemeral=True)
        return

    await interaction.response.defer()
    global reputation_counter
    reputation_counter += 1
    save_reputation(reputation_counter)

    embed = discord.Embed(title="Sovereign Studio • Reputation", color=0xd4c32c)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="Customers:", value=f"<@{interaction.user.id}>", inline=True)
    embed.add_field(name="Rating:", value="<:rstar:1374610560636817458>" * stars.value, inline=True)
    embed.add_field(name="Reps No:", value=f"`{reputation_counter}`", inline=False)
    embed.add_field(name="Review:", value=reviewmessage, inline=False)
    current_datetime = datetime.utcnow()
    formatted_date = current_datetime.strftime("%d %B %Y")
    embed.set_footer(text=f"© {current_datetime.year} Sovereign Studio  - {formatted_date}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="daily", description="Claim 10 point harian kamu!")
async def daily(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)

        user_id = str(interaction.user.id)
        jakarta = timezone('Asia/Jakarta')
        now = datetime.now(jakarta).date()

        daily_log = load_daily_log()
        last_claim = daily_log.get(user_id)

        if last_claim == str(now):
            # Hitung waktu menuju tengah malam (reset claim)
            now_time = datetime.now(jakarta)
            reset_time = jakarta.localize(datetime.combine(now + timedelta(days=1), datetime.min.time()))
            remaining = reset_time - now_time
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)

            return await interaction.followup.send(
                f"<:4366orangesmalldot:1316385342911287348> Kamu sudah klaim hari ini! Coba lagi dalam **{hours} jam {minutes} menit**.",
                ephemeral=True
            )

        # Tambahkan 10 poin
        points = load_points()
        points[user_id] = points.get(user_id, 0) + 10
        save_points(points)

        # Simpan tanggal klaim hari ini
        daily_log[user_id] = str(now)
        save_daily_log(daily_log)

        await interaction.followup.send(
            f"<:8484greensmalldot:1316385337903419433> Kamu berhasil klaim **10 Point** hari ini! Total: `{points[user_id]}`",
            ephemeral=True
        )

    except Exception as e:
        print(f"❌ Error in /daily: {e}")
        try:
            await interaction.followup.send("❌ Terjadi kesalahan saat klaim poin. Coba lagi nanti.", ephemeral=True)
        except:
            pass

@bot.tree.command(name="addpoint", description="(ADMIN) Tambah point ke user")
@app_commands.describe(user="User yang ingin diberi poin", amount="Jumlah poin yang ditambahkan")
async def addpoint(interaction: discord.Interaction, user: discord.User, amount: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("<:1476redsmalldot:1316385340180664373> Hanya admin yang bisa pakai command ini.", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("<:4366orangesmalldot:1316385342911287348> Jumlah harus lebih dari 0.", ephemeral=True)
        return

    user_id = str(user.id)
    points = load_points()
    points[user_id] = points.get(user_id, 0) + amount
    save_points(points)

    await interaction.response.send_message(f"<:8484greensmalldot:1316385337903419433> {user.mention} mendapat **{amount} Point**. Total: `{points[user_id]}`")

@bot.tree.command(name="checkpoint", description="Lihat jumlah poin kamu saat ini")
async def checkpoint(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    points = load_points()
    total = points.get(user_id, 0)
    await interaction.response.send_message(f"Total poin kamu saat ini adalah: `{total}`", ephemeral=True)

@bot.tree.command(name="store", description="Lihat daftar produk yang bisa dibeli dengan poin")
async def store(interaction: discord.Interaction):
    products = load_products()
    if not products:
        await interaction.response.send_message("<:1476redsmalldot:1316385340180664373> Tidak ada produk tersedia saat ini.", ephemeral=True)
        return

    embed = discord.Embed(title="Free Resources", color=0xd4c32c)
    for pid, product in products.items():
        embed.add_field(name=f"{product['name']} (ID: {pid})", value=f"Harga: {product['price']} Point", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="buy", description="Beli produk dengan poin")
@app_commands.describe(idproduct="ID produk yang ingin dibeli")
async def buy(interaction: discord.Interaction, idproduct: str):
    products = load_products()
    product = products.get(idproduct)

    if not product:
        await interaction.response.send_message("<:1476redsmalldot:1316385340180664373> Produk tidak ditemukan.", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    points = load_points()
    if points.get(user_id, 0) < product['price']:
        await interaction.response.send_message("<:4366orangesmalldot:1316385342911287348> Poin kamu tidak cukup untuk membeli produk ini.", ephemeral=True)
        return

    points[user_id] -= product['price']
    save_points(points)

    code = generate_code()

    purchases = load_purchases()
    purchases.append({
        "user_id": user_id,
        "username": interaction.user.name,
        "product_id": idproduct,
        "product_name": product['name'],
        "code": code,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_purchases(purchases)

    embed = discord.Embed(title="Pembelian Berhasil", color=0xd4c32c)
    embed.add_field(name="Nama Produk", value=product['name'], inline=False)
    embed.add_field(name="ID Produk", value=idproduct, inline=False)
    embed.add_field(name="Detail Produk", value=product['description'], inline=False)
    embed.add_field(name="Kode Klaim", value=f"`{code}` (Kirim ke owner untuk klaim)", inline=False)
    embed.set_footer(text="Terima kasih telah berbelanja di Sovereign Studio!")

    try:
        await interaction.user.send(embed=embed)
        await interaction.response.send_message("<:8484greensmalldot:1316385337903419433> Produk berhasil dibeli! Cek DM kamu untuk detailnya.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("<:1476redsmalldot:1316385340180664373> Gagal mengirim DM. Pastikan DM kamu terbuka.", ephemeral=True)

@bot.tree.command(name="checkcode", description="(ADMIN) Lihat semua kode pembelian yang telah terkirim")
async def checkcode(interaction: discord.Interaction):
    purchases = load_purchases()
    user_id = str(interaction.user.id)
    user_purchases = [p for p in purchases if p['user_id'] == user_id]
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("<:1476redsmalldot:1316385340180664373> Hanya admin yang bisa menggunakan perintah ini.", ephemeral=True)
        return

    purchases = load_purchases()
    if not purchases:
        await interaction.response.send_message("<:1476redsmalldot:1316385340180664373> Belum ada pembelian tercatat.", ephemeral=True)
        return

    embed = discord.Embed(title="Daftar Kode Pembelian", color=0xd4c32c)
    for i, p in enumerate(purchases, start=1): 
        user = await bot.fetch_user(p['user_id'])
        embed.add_field(
            name=f"{i}. {p['product_name']}",
            value=f"Kode: `{p['code']}`\nID Produk: `{p['product_id']}`\nUser: {user.mention}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Run the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)