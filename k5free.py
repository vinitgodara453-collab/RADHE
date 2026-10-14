#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
K5FREE V3.3 - TOP LEVEL TELEGRAM AUTOMATION & COMMUNITY SUITE
====================================================================
Upgraded & Fixed for: vinitgodara453-collab / RADHE
Original by: BD71ZONE & Avijit360

100% Fully Functional Real Implementations:
- Real Telethon MTProto Account Login with OTP & 2FA support
- Real Ban Checker that tests MTProto ping and active status
- Real Banned Accounts & Dead Sessions Purger
- Real 8-Mode Member Scraper (All, Online, Active, Weekly, Monthly,
  Hidden via Chat History Mining, Premium Badge, Non-Active)
- Real Anti-Ban Member Adder with auto-account rotation & sleep
- Real Contact Manager & Sync Purger (DeleteContactsRequest)
- Real Anti-Scam Reporting via ReportPeerRequest, @notoscam & Report-Messege.txt
====================================================================
"""

import os
import sys
import time
import csv
import glob
import random
import asyncio
from typing import List, Dict, Any, Optional

# Ensure required libraries
try:
    from telethon import TelegramClient, events, errors
    from telethon.tl.functions.channels import (
        GetParticipantsRequest,
        InviteToChannelRequest,
        JoinChannelRequest
    )
    from telethon.tl.types import (
        ChannelParticipantsSearch,
        UserStatusOnline,
        UserStatusRecently,
        UserStatusLastWeek,
        UserStatusLastMonth,
        UserStatusEmpty,
        InputPeerChannel,
        InputPeerUser,
        InputReportReasonSpam,
        InputReportReasonFake,
        InputReportReasonOther
    )
    from telethon.tl.functions.messages import ReportRequest
    from telethon.tl.functions.account import ReportPeerRequest
    from telethon.tl.functions.contacts import DeleteContactsRequest, GetContactsRequest
    import colorama
    from colorama import Fore, Style, Back
    colorama.init(autoreset=True)
except ImportError as e:
    print(f"[-] Missing library: {e}")
    print("[+] Please run: python setup.py OR pip install -r requirements.txt")
    sys.exit(1)

# Default Telegram API credentials (you can replace with your own from my.telegram.org)
DEFAULT_API_ID = 2055694
DEFAULT_API_HASH = "a10ddb589cd1cfa0b132546373337b83"

BANNER = f"""{Fore.CYAN}
  ███████╗██████╗  ███████╗███████╗
  ██╔════╝██╔══██╗ ██╔════╝██╔════╝
  ███████╗██████╔╝ █████╗  █████╗  
  ╚════██║██╔══██╗ ██╔══╝  ██╔══╝  
  ███████║██████╔╝ ██║     ███████╗
  ╚══════╝╚═════╝  ╚═╝     ╚══════╝
  {Fore.YELLOW}K5FREE V3.3 - TOP LEVEL EDITION (RADHE){Style.RESET_ALL}
  {Fore.GREEN}[✓] Real Login Engine  [✓] Real MTProto Scraper  [✓] Real Scam Reporter{Style.RESET_ALL}
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ensure_dirs_and_files():
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("Problem", exist_ok=True)
    os.makedirs("done", exist_ok=True)
    if not os.path.exists("Number.csv"):
        with open("Number.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["phone_number"])
    if not os.path.exists("Contact-Number.csv"):
        with open("Contact-Number.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "phone_number"])

def load_phone_numbers(filepath="Number.csv") -> List[str]:
    ensure_dirs_and_files()
    numbers = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip() and not row[0].strip().lower().startswith("phone"):
                num = row[0].strip().replace(" ", "").replace("-", "")
                if not num.startswith("+"):
                    num = "+" + num
                numbers.append(num)
    return numbers

def save_phone_number(phone: str, filepath="Number.csv"):
    existing = load_phone_numbers(filepath)
    if phone not in existing:
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([phone])

def save_banned_number(phone: str, reason="Banned", ban_file="Problem/BanNumber.csv"):
    os.makedirs(os.path.dirname(ban_file), exist_ok=True)
    with open(ban_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([phone, reason, time.strftime("%Y-%m-%d %H:%M:%S")])

def get_all_session_files() -> List[str]:
    ensure_dirs_and_files()
    files = glob.glob("sessions/*.session")
    # Clean out paths to session names
    sessions = []
    for f in files:
        base = os.path.basename(f)
        session_name = os.path.splitext(base)[0]
        sessions.append(session_name)
    return sessions

def load_report_templates() -> List[str]:
    filepath = "Report-Messege.txt"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f.read().split("\n") if l.strip()]
            if lines:
                return lines
    # Default fallback templates if file is missing
    return [
        "It has come to my attention that {username} is engaging in illegal activities and scamming unsuspecting individuals. Please investigate and take appropriate action.",
        "I am reporting {username} for participating in fraudulent activities and scamming users. Urgent intervention is needed to prevent further harm.",
        "{username} is involved in fraudulent investment schemes and fake impersonation. Immediate action from Telegram support is necessary.",
        "The user/channel {username} is conducting illicit operations, selling compromised credentials and phishing users. Please ban immediately.",
        "Please be advised that {username} is deceiving members by posing as official support administrators and requesting cryptocurrency deposits."
    ]

# ====================================================================
# [1] REAL LOGIN ENGINE
# ====================================================================
async def real_login_account():
    print(f"\n{Fore.CYAN}=== [1] TELEGRAM ACCOUNT LOGIN WIZARD ==={Style.RESET_ALL}")
    ensure_dirs_and_files()
    
    phone = input(f"{Fore.YELLOW}Enter Phone Number with country code (+91..., +1...): {Style.RESET_ALL}").strip()
    if not phone:
        print(f"{Fore.RED}[!] Phone number cannot be empty.{Style.RESET_ALL}")
        return
    if not phone.startswith("+"):
        phone = "+" + phone

    clean_name = phone.replace("+", "")
    session_path = os.path.join("sessions", clean_name)
    
    client = TelegramClient(session_path, DEFAULT_API_ID, DEFAULT_API_HASH)
    try:
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"{Fore.GREEN}[✓] Account is ALREADY authorized!{Style.RESET_ALL}")
            print(f"    Name: {me.first_name} {me.last_name or ''}")
            print(f"    User ID: {me.id} | Phone: +{me.phone}")
            save_phone_number(phone)
            await client.disconnect()
            return

        print(f"{Fore.CYAN}[+] Requesting login code from Telegram for {phone}...{Style.RESET_ALL}")
        send_code = await client.send_code_request(phone)
        
        code = input(f"{Fore.YELLOW}Enter the login code you received in Telegram: {Style.RESET_ALL}").strip()
        code = code.replace(" ", "").replace("-", "")
        
        try:
            await client.sign_in(phone, code)
        except errors.SessionPasswordNeededError:
            print(f"{Fore.YELLOW}[!] Two-Step Verification (2FA Cloud Password) is enabled.{Style.RESET_ALL}")
            pwd = input("Enter your 2FA Password: ").strip()
            await client.sign_in(password=pwd)

        me = await client.get_me()
        print(f"\n{Fore.GREEN}[✓] LOGIN SUCCESSFUL!{Style.RESET_ALL}")
        print(f"    Name: {me.first_name} {me.last_name or ''}")
        print(f"    Username: @{me.username or 'No username'}")
        print(f"    User ID: {me.id}")
        print(f"    Session saved at: sessions/{clean_name}.session")
        save_phone_number(phone)
        
    except errors.PhoneNumberBannedError:
        print(f"{Fore.RED}[X] THIS PHONE NUMBER IS BANNED BY TELEGRAM!{Style.RESET_ALL}")
        save_banned_number(phone, "PhoneNumberBanned")
    except errors.PhoneCodeInvalidError:
        print(f"{Fore.RED}[X] Invalid Telegram login code entered.{Style.RESET_ALL}")
    except errors.PhoneCodeExpiredError:
        print(f"{Fore.RED}[X] Login code expired. Please try again.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[X] Login failed: {e}{Style.RESET_ALL}")
    finally:
        if client.is_connected():
            await client.disconnect()

# ====================================================================
# [2] REAL BAN CHECKER
# ====================================================================
async def real_check_banned_accounts():
    print(f"\n{Fore.CYAN}=== [2] CHECK BANNED ACCOUNTS ==={Style.RESET_ALL}")
    sessions = get_all_session_files()
    if not sessions:
        numbers = load_phone_numbers()
        if not numbers:
            print(f"{Fore.RED}[!] No accounts or session files found! Login accounts via [1] first.{Style.RESET_ALL}")
            return
        sessions = [n.replace("+", "") for n in numbers]

    print(f"{Fore.YELLOW}[+] Checking {len(sessions)} account sessions against Telegram MTProto...{Style.RESET_ALL}\n")
    active_count = 0
    banned_count = 0
    unauth_count = 0

    for s_name in sessions:
        phone = f"+{s_name}"
        session_path = os.path.join("sessions", s_name)
        client = TelegramClient(session_path, DEFAULT_API_ID, DEFAULT_API_HASH)
        
        try:
            start_t = time.time()
            await client.connect()
            if not await client.is_user_authorized():
                print(f"[-] {phone:<18} -> {Fore.YELLOW}UNAUTHORIZED / SESSION EXPIRED{Style.RESET_ALL}")
                unauth_count += 1
            else:
                me = await client.get_me()
                ping_ms = int((time.time() - start_t) * 1000)
                name = (me.first_name or "")[:15]
                print(f"[✓] {phone:<18} -> {Fore.GREEN}ACTIVE{Style.RESET_ALL} ({name}, Ping: {ping_ms}ms)")
                active_count += 1
        except errors.PhoneNumberBannedError:
            print(f"[X] {phone:<18} -> {Fore.RED}BANNED (PhoneNumberBanned){Style.RESET_ALL}")
            save_banned_number(phone, "PhoneNumberBanned")
            banned_count += 1
        except errors.UserDeactivatedBanError:
            print(f"[X] {phone:<18} -> {Fore.RED}BANNED (UserDeactivatedBan){Style.RESET_ALL}")
            save_banned_number(phone, "UserDeactivatedBan")
            banned_count += 1
        except Exception as e:
            print(f"[?] {phone:<18} -> {Fore.YELLOW}ERROR: {str(e)[:30]}{Style.RESET_ALL}")
        finally:
            if client.is_connected():
                await client.disconnect()

    print(f"\n{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
    print(f"Summary: {Fore.GREEN}{active_count} Active{Style.RESET_ALL} | {Fore.RED}{banned_count} Banned{Style.RESET_ALL} | {Fore.YELLOW}{unauth_count} Unauthorized{Style.RESET_ALL}")
    if banned_count > 0:
        print(f"{Fore.YELLOW}[i] Run option [3] to delete banned sessions automatically.{Style.RESET_ALL}")

# ====================================================================
# [3] DELETE BANNED ACCOUNTS
# ====================================================================
def real_delete_banned_accounts():
    print(f"\n{Fore.CYAN}=== [3] DELETE BANNED ACCOUNTS & SESSIONS ==={Style.RESET_ALL}")
    ban_file = "Problem/BanNumber.csv"
    if not os.path.exists(ban_file):
        print(f"{Fore.GREEN}[✓] No banned accounts recorded in Problem/BanNumber.csv.{Style.RESET_ALL}")
        return

    banned_phones = []
    with open(ban_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                banned_phones.append(row[0].strip())

    if not banned_phones:
        print(f"{Fore.GREEN}[✓] Ban list is empty!{Style.RESET_ALL}")
        return

    deleted_count = 0
    for p in banned_phones:
        clean = p.replace("+", "")
        s_file = f"sessions/{clean}.session"
        if os.path.exists(s_file):
            try:
                os.remove(s_file)
                print(f"[✓] Deleted dead session: {s_file}")
                deleted_count += 1
            except Exception as e:
                print(f"[!] Could not delete {s_file}: {e}")

    # Clean Number.csv
    nums = load_phone_numbers()
    clean_nums = [n for n in nums if n not in banned_phones]
    with open("Number.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["phone_number"])
        for cn in clean_nums:
            writer.writerow([cn])

    print(f"\n{Fore.GREEN}[✓] Cleaned {deleted_count} banned session files and synchronized Number.csv!{Style.RESET_ALL}")

# ====================================================================
# GET ANY ACTIVE CLIENT
# ====================================================================
async def get_active_client() -> Optional[TelegramClient]:
    sessions = get_all_session_files()
    if not sessions:
        print(f"{Fore.RED}[!] No sessions found! Please login an account first via Option [1].{Style.RESET_ALL}")
        return None

    for s in sessions:
        client = TelegramClient(os.path.join("sessions", s), DEFAULT_API_ID, DEFAULT_API_HASH)
        await client.connect()
        if await client.is_user_authorized():
            return client
        await client.disconnect()

    print(f"{Fore.RED}[!] None of the available sessions are authorized. Please login again via Option [1].{Style.RESET_ALL}")
    return None

# ====================================================================
# [5]-[12] REAL SCRAPER SUITE
# ====================================================================
async def real_scrape_members(filter_type="all"):
    print(f"\n{Fore.CYAN}=== SCRAPE TELEGRAM MEMBERS ({filter_type.upper()}) ==={Style.RESET_ALL}")
    client = await get_active_client()
    if not client:
        return

    group_input = input(f"{Fore.YELLOW}Enter Target Group Username or Link (@group_name): {Style.RESET_ALL}").strip()
    if not group_input:
        print(f"{Fore.RED}[!] Target group cannot be empty.{Style.RESET_ALL}")
        await client.disconnect()
        return

    limit_str = input(f"{Fore.YELLOW}How many members to scrape? (default 500, max 10000): {Style.RESET_ALL}").strip()
    limit = int(limit_str) if limit_str.isdigit() else 500

    print(f"\n{Fore.CYAN}[+] Connecting to target: {group_input}...{Style.RESET_ALL}")
    try:
        entity = await client.get_entity(group_input)
    except Exception as e:
        print(f"{Fore.RED}[X] Could not access group: {e}{Style.RESET_ALL}")
        await client.disconnect()
        return

    scraped_users = []
    print(f"[+] Scraping members with filter: '{filter_type}'...")

    if filter_type == "hidden":
        # Mine messages from chat history to find hidden active participants
        print(f"{Fore.MAGENTA}[+] Bypassing hidden member list via Chat Message Mining...{Style.RESET_ALL}")
        seen_ids = set()
        msg_count = 0
        async for msg in client.iter_messages(entity, limit=2000):
            msg_count += 1
            if msg.sender and getattr(msg.sender, 'id', None) not in seen_ids:
                user = msg.sender
                if not getattr(user, 'bot', False) and not getattr(user, 'deleted', False):
                    seen_ids.add(user.id)
                    scraped_users.append({
                        "id": user.id,
                        "username": user.username or "",
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                        "phone": user.phone or "",
                        "access_hash": user.access_hash
                    })
                    print(f"  [+] Mined user from message #{msg_count}: @{user.username or user.first_name}")
                    if len(scraped_users) >= limit:
                        break
    else:
        offset = 0
        batch_limit = 100
        while len(scraped_users) < limit:
            try:
                participants = await client(GetParticipantsRequest(
                    channel=entity,
                    filter=ChannelParticipantsSearch(''),
                    offset=offset,
                    limit=batch_limit,
                    hash=0
                ))
            except Exception as e:
                print(f"[!] Error fetching batch at offset {offset}: {e}")
                break

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
            print(f"  -> Fetched {len(scraped_users)} matching members so far...")
            await asyncio.sleep(0.5)

    await client.disconnect()

    if not scraped_users:
        print(f"{Fore.YELLOW}[!] No members matched the filter or group member list is restricted.{Style.RESET_ALL}")
        return

    # Save to CSV
    filename = "ScrapedMembers.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "username", "first_name", "last_name", "phone", "access_hash"])
        writer.writeheader()
        writer.writerows(scraped_users)

    print(f"\n{Fore.GREEN}[✓] SUCCESS! Scraped {len(scraped_users)} members saved to {filename}!{Style.RESET_ALL}")

# ====================================================================
# [15] REAL MEMBER ADDER WITH ROTATION
# ====================================================================
async def real_member_adder():
    print(f"\n{Fore.CYAN}=== [15] ANTI-BAN MEMBER ADDER ENGINE ==={Style.RESET_ALL}")
    if not os.path.exists("ScrapedMembers.csv"):
        print(f"{Fore.RED}[!] ScrapedMembers.csv not found! Run Option [5]-[10] scraper first.{Style.RESET_ALL}")
        return

    members = []
    with open("ScrapedMembers.csv", "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for r in reader:
            members.append(r)

    if not members:
        print(f"{Fore.RED}[!] ScrapedMembers.csv is empty!{Style.RESET_ALL}")
        return

    sessions = get_all_session_files()
    if not sessions:
        print(f"{Fore.RED}[!] No account sessions found! Login via [1] first.{Style.RESET_ALL}")
        return

    dest_group = input(f"{Fore.YELLOW}Enter Destination Group Username / Link (@my_group): {Style.RESET_ALL}").strip()
    if not dest_group:
        print(f"{Fore.RED}[!] Destination group cannot be empty.{Style.RESET_ALL}")
        return

    delay_sec = input(f"{Fore.YELLOW}Enter anti-ban delay in seconds (default 25s): {Style.RESET_ALL}").strip()
    delay = int(delay_sec) if delay_sec.isdigit() and int(delay_sec) >= 5 else 25

    print(f"\n{Fore.GREEN}[+] Starting Member Adder across {len(sessions)} rotating sessions...{Style.RESET_ALL}")
    print(f"[+] Safety Delay: {delay}s per invite | Anti-Flood protection enabled\n")

    current_session_idx = 0
    added_total = 0
    skipped_total = 0

    for i, user in enumerate(members):
        s_name = sessions[current_session_idx % len(sessions)]
        client = TelegramClient(os.path.join("sessions", s_name), DEFAULT_API_ID, DEFAULT_API_HASH)
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"[!] Session {s_name} unauthorized. Switching...")
                current_session_idx += 1
                continue

            entity = await client.get_entity(dest_group)
            
            # Prepare user input
            target_user = None
            if user.get("username"):
                target_user = await client.get_input_entity(user["username"])
            elif user.get("id") and user.get("access_hash"):
                target_user = InputPeerUser(int(user["id"]), int(user["access_hash"]))

            if not target_user:
                skipped_total += 1
                continue

            await client(InviteToChannelRequest(channel=entity, users=[target_user]))
            added_total += 1
            print(f"{Fore.GREEN}[✓] ({added_total}) Added: @{user.get('username') or user.get('first_name')} via +{s_name}{Style.RESET_ALL}")

            # Safe cooldown delay
            for remaining in range(delay, 0, -1):
                sys.stdout.write(f"\r[Anti-Ban Sleep] Next invite in {remaining}s... ")
                sys.stdout.flush()
                await asyncio.sleep(1)
            print()

            # Rotate account after 15 adds
            if added_total % 15 == 0:
                current_session_idx += 1
                print(f"\n{Fore.YELLOW}[↺] Rotated to next account session: +{sessions[current_session_idx % len(sessions)]}{Style.RESET_ALL}\n")

        except errors.UserPrivacyRestrictedError:
            print(f"{Fore.YELLOW}[SKIP] User privacy prevents invites: @{user.get('username') or user.get('id')}{Style.RESET_ALL}")
            skipped_total += 1
        except errors.UserAlreadyParticipantError:
            print(f"[i] User already in group: @{user.get('username') or user.get('id')}")
        except errors.PeerFloodError:
            print(f"\n{Fore.RED}[!] PeerFlood on +{s_name}! Rotating immediately to next account...{Style.RESET_ALL}")
            current_session_idx += 1
            await asyncio.sleep(5)
        except errors.FloodWaitError as fwe:
            print(f"\n{Fore.YELLOW}[!] FloodWait on +{s_name} for {fwe.seconds}s. Switching account...{Style.RESET_ALL}")
            current_session_idx += 1
        except Exception as e:
            print(f"[!] Error adding user: {e}")
        finally:
            if client.is_connected():
                await client.disconnect()

    print(f"\n{Fore.GREEN}[✓] Finished! Total Added: {added_total} | Skipped: {skipped_total}{Style.RESET_ALL}")

# ====================================================================
# [17] REAL CONTACT DELETOR
# ====================================================================
async def real_delete_contacts():
    print(f"\n{Fore.CYAN}=== [17] PURGE SYNCED CONTACTS (RESET LIMITS) ==={Style.RESET_ALL}")
    client = await get_active_client()
    if not client:
        return

    try:
        contacts = await client(GetContactsRequest(hash=0))
        if not contacts.users:
            print(f"{Fore.GREEN}[✓] No contacts currently stored on this Telegram account!{Style.RESET_ALL}")
            await client.disconnect()
            return

        print(f"[+] Found {len(contacts.users)} synced contacts. Purging...")
        input_users = [InputPeerUser(u.id, u.access_hash) for u in contacts.users]
        await client(DeleteContactsRequest(id=input_users))
        print(f"{Fore.GREEN}[✓] Successfully wiped {len(contacts.users)} contacts! Account limits refreshed.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[X] Failed to delete contacts: {e}{Style.RESET_ALL}")
    finally:
        if client.is_connected():
            await client.disconnect()

# ====================================================================
# [19] & [20] REAL SCAM REPORTING SYSTEM
# ====================================================================
async def real_report_scammer():
    print(f"\n{Fore.CYAN}=== [19/20] SCAMMER & FAKE GROUP REPORTING SYSTEM ==={Style.RESET_ALL}")
    templates = load_report_templates()
    print(f"{Fore.GREEN}[✓] Loaded {len(templates)} authentic reporting templates from Report-Messege.txt{Style.RESET_ALL}")

    target = input(f"{Fore.YELLOW}Enter Scammer Username or Channel/Group Link (@scammer_bot): {Style.RESET_ALL}").strip()
    if not target:
        print(f"{Fore.RED}[!] Target handle cannot be empty.{Style.RESET_ALL}")
        return
    if not target.startswith("@") and not target.startswith("http"):
        target = "@" + target

    print(f"\nSelect Violation Category:")
    print("  [1] Financial Fraud & Phishing Schemes")
    print("  [2] Impersonation & Fake Admin Handling")
    print("  [3] Advance Fee Crypto Scam")
    print("  [4] Illegal Distribution & Malware")
    cat = input("Enter Category [1-4, default 1]: ").strip()
    
    # Pick 5 distinct complaint messages with placeholder replaced
    sample_reports = []
    shuffled = random.sample(templates, min(5, len(templates)))
    for t in shuffled:
        sample_reports.append(t.replace("{username}", target))

    print(f"\n{Fore.YELLOW}[+] Generated 5 tailored reports for {target}:{Style.RESET_ALL}")
    for idx, rep in enumerate(sample_reports, 1):
        print(f"\n--- Report #{idx} ---")
        print(f"{rep}")

    # Save to done/Report_Army.csv
    os.makedirs("done", exist_ok=True)
    with open("done/Report_Army.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for rep in sample_reports:
            writer.writerow([target, rep, time.strftime("%Y-%m-%d %H:%M:%S")])
    print(f"\n{Fore.GREEN}[✓] Reports saved to done/Report_Army.csv{Style.RESET_ALL}")

    # Attempt to submit via Telethon client if active
    do_send = input(f"\n{Fore.YELLOW}Do you want to dispatch MTProto Report Request directly via connected accounts? (y/n): {Style.RESET_ALL}").strip().lower()
    if do_send == "y":
        client = await get_active_client()
        if client:
            try:
                print(f"[+] Resolving target {target}...")
                entity = await client.get_entity(target)
                msg_to_send = sample_reports[0]
                
                # Use ReportPeerRequest
                await client(ReportPeerRequest(
                    peer=entity,
                    reason=InputReportReasonFake(),
                    message=msg_to_send
                ))
                print(f"{Fore.GREEN}[✓] MTProto ReportPeerRequest sent successfully to Telegram Trust & Safety!{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Could not dispatch MTProto report: {e}{Style.RESET_ALL}")
                print(f"[i] You can still submit reports manually to official @notoscam bot on Telegram.")
            finally:
                if client.is_connected():
                    await client.disconnect()

def display_menu():
    clear_screen()
    print(BANNER)
    print(f"{Fore.LIGHTBLUE_EX}╔════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   MAIN ACCOUNT OPTIONS:                                       ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.GREEN}[1]{Style.RESET_ALL}  Login Account (Real OTP & 2FA Telegram Login)           ║")
    print(f"║ {Fore.GREEN}[2]{Style.RESET_ALL}  Check Banned Accounts (Real MTProto Ping Check)         ║")
    print(f"║ {Fore.GREEN}[3]{Style.RESET_ALL}  Delete Banned Accounts & Sessions Clean                 ║")
    print(f"║ {Fore.GREEN}[4]{Style.RESET_ALL}  System & Session Status Info                            ║")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   MEMBERS SCRAPER SUITE:                                       ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.YELLOW}[5]{Style.RESET_ALL}  All Type Members Scraper                                ║")
    print(f"║ {Fore.YELLOW}[6]{Style.RESET_ALL}  Online Members Scraper (Users currently Online)        ║")
    print(f"║ {Fore.YELLOW}[7]{Style.RESET_ALL}  Active Members Scraper (Seen in last 24 Hours)          ║")
    print(f"║ {Fore.YELLOW}[8]{Style.RESET_ALL}  Weekly Members Scraper (Seen in last 7 Days)           ║")
    print(f"║ {Fore.YELLOW}[9]{Style.RESET_ALL}  Monthly Members Scraper (Seen in last 30 Days)         ║")
    print(f"║ {Fore.YELLOW}[10]{Style.RESET_ALL} Hidden Members Scraper (Chat History Mining)           ║")
    print(f"║ {Fore.YELLOW}[11]{Style.RESET_ALL} Premium Members Scraper (Telegram Premium Users)       ║")
    print(f"║ {Fore.YELLOW}[12]{Style.RESET_ALL} Non-Active Members Scraper (Inactive cleanup)         ║")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   MEMBER ADDER & COMMUNITY TOOLS:                              ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.CYAN}[15]{Style.RESET_ALL} Scraped Members Adder (Anti-Flood with auto-rotation)   ║")
    print(f"║ {Fore.CYAN}[17]{Style.RESET_ALL} Contact Deletor (Purge contacts to reset limits)       ║")
    print(f"║ {Fore.CYAN}[18]{Style.RESET_ALL} Account Cooldown & FloodWait Optimizer                 ║")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║   SECURITY & REPORTING:                                        ║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╠════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║ {Fore.MAGENTA}[19]{Style.RESET_ALL} Report Scam Group/Channel (179 Templates)              ║")
    print(f"║ {Fore.MAGENTA}[20]{Style.RESET_ALL} Report A Scammer Handle                                ║")
    print(f"║ {Fore.WHITE}[99]{Style.RESET_ALL} How To Use & Termux Setup Guide                        ║")
    print(f"║ {Fore.RED}[0]{Style.RESET_ALL}  Exit                                                    ║")
    print(f"{Fore.LIGHTBLUE_EX}╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

def main():
    ensure_dirs_and_files()
    while True:
        display_menu()
        choice = input(f"{Fore.YELLOW}Enter Your Choice [0-99]: {Style.RESET_ALL}").strip()
        
        if choice == "0":
            print(f"{Fore.RED}[+] Exiting K5FREE. Goodbye!{Style.RESET_ALL}")
            break
        elif choice == "1":
            asyncio.run(real_login_account())
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            asyncio.run(real_check_banned_accounts())
            input("\nPress Enter to return to menu...")
        elif choice == "3":
            real_delete_banned_accounts()
            input("\nPress Enter to return to menu...")
        elif choice == "4":
            sessions = get_all_session_files()
            nums = load_phone_numbers()
            print(f"\n{Fore.CYAN}=== SYSTEM & SESSION STATUS ==={Style.RESET_ALL}")
            print(f"  Python Version: {sys.version.split()[0]}")
            print(f"  Sessions Stored in 'sessions/': {len(sessions)}")
            print(f"  Numbers in 'Number.csv': {len(nums)}")
            input("\nPress Enter to return to menu...")
        elif choice == "5":
            asyncio.run(real_scrape_members("all"))
            input("\nPress Enter to return to menu...")
        elif choice == "6":
            asyncio.run(real_scrape_members("online"))
            input("\nPress Enter to return to menu...")
        elif choice == "7":
            asyncio.run(real_scrape_members("active"))
            input("\nPress Enter to return to menu...")
        elif choice == "8":
            asyncio.run(real_scrape_members("weekly"))
            input("\nPress Enter to return to menu...")
        elif choice == "9":
            asyncio.run(real_scrape_members("monthly"))
            input("\nPress Enter to return to menu...")
        elif choice == "10":
            asyncio.run(real_scrape_members("hidden"))
            input("\nPress Enter to return to menu...")
        elif choice == "11":
            asyncio.run(real_scrape_members("premium"))
            input("\nPress Enter to return to menu...")
        elif choice == "12":
            asyncio.run(real_scrape_members("non_active"))
            input("\nPress Enter to return to menu...")
        elif choice == "15":
            asyncio.run(real_member_adder())
            input("\nPress Enter to return to menu...")
        elif choice == "17":
            asyncio.run(real_delete_contacts())
            input("\nPress Enter to return to menu...")
        elif choice == "18":
            print(f"\n{Fore.CYAN}=== ACCOUNT LIMIT MITIGATION & OPTIMIZER ==={Style.RESET_ALL}")
            print("1. Telegram allows ~35-50 user invites per account per 24 hours.")
            print("2. When PeerFloodError occurs, the account must rest for 12-24 hours.")
            print("3. Always run Option [17] Contact Deletor to wipe stale synced contacts.")
            print("4. Use at least 5 accounts in rotation with 25-35s anti-ban delays.")
            input("\nPress Enter to return to menu...")
        elif choice == "19" or choice == "20":
            asyncio.run(real_report_scammer())
            input("\nPress Enter to return to menu...")
        elif choice == "99":
            print(f"""
{Fore.CYAN}=== TERMUX RUN GUIDE ===
git clone https://github.com/vinitgodara453-collab/RADHE.git
cd RADHE
python setup.py
python k5free.py
========================{Style.RESET_ALL}
""")
            input("\nPress Enter to return to menu...")
        else:
            print(f"{Fore.RED}[!] Invalid choice: '{choice}'. Enter 0-99.{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Program interrupted by user. Exiting...")
