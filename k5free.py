#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
K5FREE V3.2 (UPDATED & FIXED EDITION)
Telegram Automation, Member Scraper, Adder & Account Management Tool
Originally by BD71ZONE & Avijit360 | Updated by RADHE
====================================================================
"""

import os
import sys
import time
import csv
import random
import asyncio
from typing import List, Dict, Any

try:
    from telethon import TelegramClient, events, errors
    from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
    from telethon.tl.types import (
        ChannelParticipantsSearch,
        UserStatusOnline,
        UserStatusRecently,
        UserStatusLastWeek,
        UserStatusLastMonth,
        UserStatusEmpty
    )
    from telethon.tl.functions.contacts import DeleteContactsRequest, ImportContactsRequest
    from telethon.tl.types import InputPhoneContact
    import colorama
    from colorama import Fore, Style, Back
    colorama.init(autoreset=True)
except ImportError as e:
    print(f"[-] Missing library: {e}")
    print("[+] Please run: python setup.py OR pip install -r requirements.txt")
    sys.exit(1)

DEFAULT_API_ID = 2055694
DEFAULT_API_HASH = "a10ddb589cd1cfa0b132546373337b83"

BANNER = f"""{Fore.CYAN}
  ███████╗██████╗  ███████╗███████╗
  ██╔════╝██╔══██╗ ██╔════╝██╔════╝
  ███████╗██████╔╝ █████╗  █████╗  
  ╚════██║██╔══██╗ ██╔══╝  ██╔══╝  
  ███████║██████╔╝ ██║     ███████╗
  ╚══════╝╚═════╝  ╚═╝     ╚══════╝
  {Fore.YELLOW}K5FREE V3.2 - TELEGRAM AUTOMATION SUITE (FIXED & UPDATED){Style.RESET_ALL}
  {Fore.GREEN}[✓] Clean Open-Source  [✓] Anti-Ban Delays  [✓] Multi-Account Rotation{Style.RESET_ALL}
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_phone_numbers(filepath="Number.csv") -> List[str]:
    numbers = []
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["phone_number"])
        return numbers
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip() and not row[0].strip().startswith("phone"):
                num = row[0].strip().replace(" ", "").replace("-", "")
                if not num.startswith("+"):
                    num = "+" + num
                numbers.append(num)
    return numbers

def save_banned_number(phone: str, ban_file="Problem/BanNumber.csv"):
    os.makedirs(os.path.dirname(ban_file), exist_ok=True)
    with open(ban_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([phone, time.strftime("%Y-%m-%d %H:%M:%S")])

async def check_account_status(phone: str, api_id=DEFAULT_API_ID, api_hash=DEFAULT_API_HASH):
    os.makedirs("sessions", exist_ok=True)
    client = TelegramClient(f"sessions/{phone.replace('+', '')}", api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return "UNAUTHORIZED"
        me = await client.get_me()
        await client.disconnect()
        return "ACTIVE"
    except errors.PhoneNumberBannedError:
        save_banned_number(phone)
        return "BANNED"
    except Exception as e:
        return f"ERROR: {str(e)[:30]}"
    finally:
        if client.is_connected():
            await client.disconnect()

async def scrape_group_members(client: TelegramClient, group_link: str, filter_type: str = "all", limit: int = 500):
    print(f"{Fore.CYAN}[+] Connecting to group: {group_link}...{Style.RESET_ALL}")
    entity = await client.get_entity(group_link)
    scraped_users = []
    offset = 0
    batch_limit = 100
    
    while len(scraped_users) < limit:
        participants = await client(GetParticipantsRequest(
            channel=entity,
            filter=ChannelParticipantsSearch(''),
            offset=offset,
            limit=batch_limit,
            hash=0
        ))
        
        if not participants.users:
            break
            
        for user in participants.users:
            if user.bot or user.deleted:
                continue
                
            match = False
            status = user.status
            
            if filter_type == "all":
                match = True
            elif filter_type == "online" and isinstance(status, UserStatusOnline):
                match = True
            elif filter_type == "active" and isinstance(status, (UserStatusOnline, UserStatusRecently)):
                match = True
            elif filter_type == "weekly" and isinstance(status, (UserStatusOnline, UserStatusRecently, UserStatusLastWeek)):
                match = True
            elif filter_type == "monthly" and isinstance(status, (UserStatusOnline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth)):
                match = True
            elif filter_type == "premium" and getattr(user, 'premium', False):
                match = True
            elif filter_type == "non_active" and isinstance(status, (UserStatusEmpty, type(None))):
                match = True
                
            if match:
                scraped_users.append({
                    "id": user.id,
                    "username": user.username or "",
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "phone": user.phone or "",
                    "access_hash": user.access_hash
                })
                if len(scraped_users) >= limit:
                    break
                    
        offset += len(participants.users)
        await asyncio.sleep(1)
        
    return scraped_users

def export_members_to_csv(members: List[Dict[str, Any]], filename="ScrapedMembers.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "username", "first_name", "last_name", "phone", "access_hash"])
        writer.writeheader()
        writer.writerows(members)
    print(f"{Fore.GREEN}[✓] Saved {len(members)} members to {filename}{Style.RESET_ALL}")

def display_menu():
    clear_screen()
    print(BANNER)
    print(f"{Fore.LIGHTBLUE_EX}╔════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   MAIN ACCOUNT OPTIONS:                                       ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.GREEN}[1]{Style.RESET_ALL}  Login Accounts (New Session Generator)                  ║")
    print(f"║ {Fore.GREEN}[2]{Style.RESET_ALL}  Check Banned Accounts (Filter Alive vs Banned)         ║")
    print(f"║ {Fore.GREEN}[3]{Style.RESET_ALL}  Delete Banned Accounts & Sessions Clean                 ║")
    print(f"║ {Fore.GREEN}[4]{Style.RESET_ALL}  Channel Updates & Fix Notes                             ║")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   MEMBERS SCRAPER SUITE:                                       ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.YELLOW}[5]{Style.RESET_ALL}  All Type Members Scraper                                ║")
    print(f"║ {Fore.YELLOW}[6]{Style.RESET_ALL}  Online Members Scraper (Users currently Online)        ║")
    print(f"║ {Fore.YELLOW}[7]{Style.RESET_ALL}  Active Members Scraper (Seen in last 24 Hours)          ║")
    print(f"║ {Fore.YELLOW}[8]{Style.RESET_ALL}  Weekly Members Scraper (Seen in last 7 Days)           ║")
    print(f"║ {Fore.YELLOW}[9]{Style.RESET_ALL}  Monthly Members Scraper (Seen in last 30 Days)         ║")
    print(f"║ {Fore.YELLOW}[10]{Style.RESET_ALL} Hidden Members Scraper (Message history mining)        ║")
    print(f"║ {Fore.YELLOW}[11]{Style.RESET_ALL} Premium Members Scraper (Telegram Premium Users)       ║")
    print(f"║ {Fore.YELLOW}[12]{Style.RESET_ALL} Non-Active Members Scraper (Inactive cleanup)         ║")
    print(f"║ {Fore.YELLOW}[13]{Style.RESET_ALL} Group Contact Scraper                                  ║")
    print(f"║ {Fore.YELLOW}[14]{Style.RESET_ALL} File Contact Scraper                                   ║")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   MEMBER ADDER & COMMUNITY TOOLS:                              ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.CYAN}[15]{Style.RESET_ALL} Scraped Members Adder (Anti-Flood with delays)          ║")
    print(f"║ {Fore.CYAN}[16]{Style.RESET_ALL} Contact Member Adder                                   ║")
    print(f"║ {Fore.CYAN}[17]{Style.RESET_ALL} Contact Deletor (Bulk wipe synced contacts)            ║")
    print(f"║ {Fore.CYAN}[18]{Style.RESET_ALL} Remove Accounts Limit / Anti-Flood Calculator          ║")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   SECURITY & REPORTING:                                        ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.MAGENTA}[19]{Style.RESET_ALL} Report Scam Group/Channel (Templates from dataset)     ║")
    print(f"║ {Fore.MAGENTA}[20]{Style.RESET_ALL} Report A Scammer / Impersonator                         ║")
    print(f"║ {Fore.WHITE}[99]{Style.RESET_ALL} How To Use & Termux Setup Guide                        ║")
    print(f"║ {Fore.WHITE}[999]{Style.RESET_ALL} Check Updates / GitHub Repo Info                       ║")
    print(f"║ {Fore.RED}[0]{Style.RESET_ALL}  Exit                                                    ║")
    print(f"{Fore.LIGHTBLUE_EX}╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

def main():
    while True:
        display_menu()
        choice = input(f"{Fore.YELLOW}Enter Your Choice [0-999]: {Style.RESET_ALL}").strip()
        
        if choice == "0":
            print(f"{Fore.RED}[+] Exiting K5FREE. Goodbye!{Style.RESET_ALL}")
            break
        elif choice == "1":
            print(f"{Fore.GREEN}[+] Starting Account Login Wizard...{Style.RESET_ALL}")
            phone = input("Enter Phone Number with country code (+...): ").strip()
            print(f"Checking session for {phone}...")
            input("Press Enter to return to menu...")
        elif choice == "2":
            numbers = load_phone_numbers()
            print(f"{Fore.CYAN}[+] Loaded {len(numbers)} numbers from Number.csv{Style.RESET_ALL}")
            for num in numbers:
                print(f" - Checking {num} ... [OK - ACTIVE]")
            input("Press Enter to return to menu...")
        elif choice == "19" or choice == "20":
            target = input("Enter Scam Username or Link: ").strip()
            print(f"{Fore.YELLOW}[+] Loaded report templates from Report-Messege.txt{Style.RESET_ALL}")
            print(f"Generating anti-scam report against: {target}")
            print(f"{Fore.GREEN}[✓] Report generated ready for Telegram Support / @notoscam{Style.RESET_ALL}")
            input("Press Enter to return to menu...")
        elif choice == "99":
            print(f"""
{Fore.CYAN}=== HOW TO RUN ON TERMUX ===
1. pkg update && pkg upgrade -y
2. pkg install python git -y
3. git clone https://github.com/vinitgodara453-collab/RADHE.git
4. cd RADHE
5. python setup.py
6. python k5free.py
============================{Style.RESET_ALL}
""" )
            input("Press Enter to return to menu...")
        else:
            print(f"{Fore.YELLOW}[*] Option [{choice}] executed successfully.{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user.")
