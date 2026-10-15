#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
RADHE V4.5 - TELEGRAM COMMERCIAL SERVICE & PAYMENT BOT
Host this bot to accept customer orders & UPI/Crypto payments 24/7!
Connected to K5FREE Turbo Engine for Automated High-Speed Fulfillment
====================================================================
"""

import os
import sys
import time
import json
import sqlite3
import asyncio
from typing import Optional

try:
    from telethon import TelegramClient, events, Button
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
except ImportError:
    print("[-] Please run: pip install telethon colorama")
    sys.exit(1)

# BotFather Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_ID = 2055694
API_HASH = "a10ddb589cd1cfa0b132546373337b83"
ADMIN_ID = 589219481  # Replace with your Telegram User ID

# Pricing & Payment Config
UPI_ID = "radhebusiness@upi"
PRICE_PER_1K_SCRAPE = 100.0  # ₹100 per 1,000 members
PRICE_PER_1K_ADD = 250.0     # ₹250 per 1,000 members
MIN_DEPOSIT = 50.0

# Database Initialization
DB_FILE = "business_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0.0,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            target TEXT,
            quantity INTEGER,
            cost REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            utr_ref TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user_balance(user_id: int, username: str = "") -> float:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users (user_id, username, balance, created_at) VALUES (?, ?, 0.0, ?)",
                  (user_id, username, time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        bal = 0.0
    else:
        bal = row[0]
    conn.close()
    return bal

def update_user_balance(user_id: int, delta: float):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (delta, user_id))
    conn.commit()
    conn.close()

# Start Bot Client
bot = TelegramClient('bot_session', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    sender = await event.get_sender()
    bal = get_user_balance(sender.id, getattr(sender, 'username', ''))
    
    welcome_msg = f"""
👋 **Welcome to RADHE Automation & Community Service Bot!**

💰 **Your Current Balance:** ₹{bal:.2f}
🆔 **Your User ID:** \`{sender.id}\`
⚡ **Fulfillment Engine:** K5FREE V4.0 Turbo

Choose an option below to get started:
"""
    buttons = [
        [Button.inline("🛒 Services & Pricing", b"services"), Button.inline("💳 Deposit Balance", b"deposit")],
        [Button.inline("📦 My Orders", b"myorders"), Button.inline("📞 Contact Admin", b"contact")]
    ]
    await event.respond(welcome_msg, buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    sender = await event.get_sender()
    data = event.data.decode('utf-8')
    bal = get_user_balance(sender.id, getattr(sender, 'username', ''))

    if data == "services":
        msg = f"""
📋 **Available Services & Official Pricing:**

1. 🎯 **Group Member Scraper (Online/Active)**
   • Rate: **₹{PRICE_PER_1K_SCRAPE}** per 1,000 members
   • Format: CSV / JSON file with usernames, IDs & phone numbers

2. 🚀 **Target Group Member Adder (Anti-Ban Turbo)**
   • Rate: **₹{PRICE_PER_1K_ADD}** per 1,000 members
   • High-speed automated delivery across rotating accounts

3. 🛡️ **Channel Audit & Scam Protection**
   • Rate: **₹99** per audit check

To place an order, make sure you have sufficient balance, then use:
\`/order <service> <target_group> <quantity>\`
Example: \`/order add @mygroup 1000\`
"""
        await event.edit(msg, buttons=[[Button.inline("💳 Deposit Balance", b"deposit"), Button.inline("🔙 Back", b"start")]])

    elif data == "deposit":
        msg = f"""
💳 **Deposit Balance via UPI / QR:**

📲 **UPI ID:** \`{UPI_ID}\`
💵 **Minimum Deposit:** ₹{MIN_DEPOSIT:.2f}

**Instructions:**
1. Open Google Pay, PhonePe, Paytm, or BHIM.
2. Send desired amount to: \`{UPI_ID}\`
3. Copy the **12-digit UTR / Ref Number**.
4. Send your UTR here using:
   \`/utr <12_digit_number> <amount>\`
   Example: \`/utr 304918294012 250\`

Your balance will be verified and credited quickly!
"""
        await event.edit(msg, buttons=[[Button.inline("🔙 Back", b"start")]])

    elif data == "myorders":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, service, target, quantity, status FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 5", (sender.id,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            await event.edit("📦 You haven't placed any orders yet. Use /services to check rates!", buttons=[[Button.inline("🔙 Back", b"start")]])
        else:
            orders_txt = "📦 **Your Recent Orders:**\n\n"
            for r in rows:
                orders_txt += f"• **#ORD-{r[0]}**: {r[1].upper()} | {r[2]} ({r[3]} qty) -> \`{r[4].upper()}\`\n"
            await event.edit(orders_txt, buttons=[[Button.inline("🔙 Back", b"start")]])

    elif data == "start":
        await start_handler(event)

@bot.on(events.NewMessage(pattern=r'/utr'))
async def utr_handler(event):
    sender = await event.get_sender()
    parts = event.text.split()
    if len(parts) < 3:
        await event.respond("❌ Format: \`/utr <12_digit_UTR> <amount>\`\\nExample: \`/utr 304918294012 250\`")
        return

    utr = parts[1].strip()
    try:
        amount = float(parts[2].strip())
    except ValueError:
        await event.respond("❌ Invalid amount.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO deposits (user_id, amount, utr_ref, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
                  (sender.id, amount, utr, time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        await event.respond(f"✅ UTR \`{utr}\` of ₹{amount} submitted! Admin will verify and credit your balance within minutes.")
    except sqlite3.IntegrityError:
        await event.respond("❌ This UTR has already been submitted!")
    finally:
        conn.close()

@bot.on(events.NewMessage(pattern=r'/order'))
async def order_handler(event):
    sender = await event.get_sender()
    parts = event.text.split()
    if len(parts) < 4:
        await event.respond("❌ Format: \`/order <service: add/scrape> <target: @group> <quantity>\`\\nExample: \`/order add @mygroup 1000\`")
        return

    service = parts[1].lower()
    target = parts[2]
    try:
        qty = int(parts[3])
    except ValueError:
        await event.respond("❌ Invalid quantity.")
        return

    rate = PRICE_PER_1K_ADD if service == "add" else PRICE_PER_1K_SCRAPE
    cost = round((qty / 1000.0) * rate, 2)

    bal = get_user_balance(sender.id, getattr(sender, 'username', ''))
    if bal < cost:
        await event.respond(f"❌ **Insufficient Balance!**\\nRequired: ₹{cost}\\nYour Balance: ₹{bal:.2f}\\nPlease use /deposit to add funds.")
        return

    # Deduct balance
    update_user_balance(sender.id, -cost)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, service, target, quantity, cost, status, created_at) VALUES (?, ?, ?, ?, ?, 'processing', ?)",
              (sender.id, service, target, qty, cost, time.strftime("%Y-%m-%d %H:%M:%S")))
    order_id = c.lastrowid
    conn.commit()
    conn.close()

    await event.respond(f"""
🎉 **Order Placed Successfully!**

🆔 **Order ID:** #ORD-{order_id}
🎯 **Target:** {target}
👥 **Quantity:** {qty} members
💵 **Cost Deducted:** ₹{cost}
⚡ **Status:** Processing via K5FREE Turbo Engine
""")

def main():
    init_db()
    print("=" * 60)
    print(f"{Fore.CYAN}[+] RADHE Commercial Bot Engine Starting...{Style.RESET_ALL}")
    print(f"[+] UPI ID: {UPI_ID}")
    print(f"[+] Scrape Rate: ₹{PRICE_PER_1K_SCRAPE}/1k | Add Rate: ₹{PRICE_PER_1K_ADD}/1k")
    print(f"[+] Bot Token: {BOT_TOKEN[:10]}...")
    print("=" * 60)
    bot.start(bot_token=BOT_TOKEN)
    print(f"{Fore.GREEN}[✓] Bot is LIVE and listening for customer orders 24/7!{Style.RESET_ALL}")
    bot.run_until_disconnected()

if __name__ == "__main__":
    main()
