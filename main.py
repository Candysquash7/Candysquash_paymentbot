import os, time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PreCheckoutQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7193430583") or 0)

# PACKAGE WITH MINUTES FOR TIMER
PACKAGES = {
    "3min":  {"label": "🍒 3 Mins", "kes": "50 KES", "usd": "$1", "stars": 25, "minutes": 3},
    "5min":  {"label": "🔥 5 Mins", "kes": "100 KES", "usd": "$2", "stars": 50, "minutes": 5},
    "10min": {"label": "💋 10 Mins", "kes": "200 KES", "usd": "$4", "stars": 100, "minutes": 10},
    "30min": {"label": "😍 30 Mins", "kes": "300 KES", "usd": "$6", "stars": 150, "minutes": 30},
}

# STORE ACTIVE CHATS IN MEMORY: user_id -> end_time
ACTIVE_CHATS = {}

WELCOME_TEXT = (
    "Hey I'm Candy 😜💦\n\n"
    "I get a little messy if you chat with me... 😈💋\n\n"
    "Come let's have fun baby 🥵 Don't keep me waiting daddy... I'm already waiting for you 🥺👉👈\n\n"
    "Choose package to chat with Candy down below baby 👇💦\n\n"
    "Real fun is waiting for you on my VIP 🍒✨"
)

def get_main_keyboard():
    kb = []
    for k,v in PACKAGES.items():
        kb.append([InlineKeyboardButton(f"{v['label']} - {v['kes']} / {v['usd']} / {v['stars']}⭐", callback_data=f"pkg_{k}")])
    kb.append([InlineKeyboardButton("📹 Video Call / Facetime - DM for prices 🥵", callback_data="video_info")])
    kb.append([InlineKeyboardButton("🎬 My VIP - Real Fun Here 🔥", callback_data="vip_only")])
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=get_main_keyboard())

async def end_chat_job(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data["user_id"]
    if user_id in ACTIVE_CHATS:
        del ACTIVE_CHATS[user_id]
        try:
            await context.bot.send_message(user_id, "⏰ Time's up baby! 🥺 Your chat time finished 💦\n\nChoose another package to continue 👇", reply_markup=get_main_keyboard())
            await context.bot.send_message(ADMIN_ID, f"⏰ CHAT ENDED for {user_id} - Time up!")
        except: pass

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "back_start":
        await q.edit_message_text(WELCOME_TEXT, reply_markup=get_main_keyboard())
        return
    if d == "video_info":
        await q.edit_message_text("📹 Video Call / Facetime Available 🥵💋\n\nDM me for prices baby", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]))
        return
    if d == "vip_only":
        await q.edit_message_text("🍒 My VIP 🍒\n\nTelegram: https://t.me/+eEsiq79bG6k2ODlk\nOnlyFans: https://onlyfans.com/candysquash", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]))
        return

    if d.startswith("pkg_"):
        k = d.replace("pkg_","")
        p = PACKAGES[k]
        context.user_data["pkg"] = k
        await q.edit_message_text(f"😍 {p['label']} - {p['usd']} / {p['stars']}⭐\n\nDon't keep me waiting baby... pay now and let's get messy 🥵💦\n\nChoose payment 👇", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"⭐ {p['stars']} Stars", callback_data=f"pay_stars_{k}")],[InlineKeyboardButton(f"💳 Skrill - {p['usd']}", callback_data=f"pay_skrill_{k}")],[InlineKeyboardButton(f"₿ Binance - {p['usd']}", callback_data=f"pay_binance_{k}")],[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]))
        return

    if d.startswith("pay_"):
        _, method, pkg_key = d.split("_")
        p = PACKAGES[pkg_key]
        if method == "stars":
            await context.bot.send_invoice(chat_id=q.from_user.id, title=p['label'], description="Chat with Candy", payload=pkg_key, provider_token="", currency="XTR", prices=[LabeledPrice(p['label'], p['stars'])])
        else:
            info = "Skrill: mbithey7@gmail.com" if method=="skrill" else "Binance ID: 1282131122"
            await q.edit_message_text(f"💰 Pay {p['usd']} via:\n{info}\n\nSend screenshot after baby 📸", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{pkg_key}")],[InlineKeyboardButton("⬅️ Back", callback_data=f"pkg_{pkg_key}")]]))
        return

    if d.startswith("paid_"):
        pkg_key = d.replace("paid_","")
        await q.edit_message_text("✅ Screenshot received baby! Waiting admin approval ⏰ Don't go anywhere 😘")
        if ADMIN_ID:
            try: await context.bot.send_message(ADMIN_ID, f"💰 CLIENT SAYS PAID!\n👤 @{q.from_user.username} ({q.from_user.id})\n📦 {pkg_key} - {PACKAGES[pkg_key]['minutes']} mins")
            except: pass
        return

    # ADMIN APPROVE / REJECT WITH TIMER
    if d.startswith("approve_"):
        if q.from_user.id != ADMIN_ID: return
        # data is approve_USERID_PACKAGE
        parts = d.split("_")
        user_id = int(parts[1])
        pkg_key = parts[2] if len(parts) > 2 else context.user_data.get("last_pkg", "3min")
        # find package - if not found use 3min
        p = PACKAGES.get(pkg_key, PACKAGES["3min"])
        minutes = p["minutes"]
        
        end_time = datetime.now() + timedelta(minutes=minutes)
        ACTIVE_CHATS[user_id] = {"end": end_time, "pkg": pkg_key}
        
        # Schedule auto stop
        context.job_queue.run_once(end_chat_job, when=minutes*60, data={"user_id": user_id}, name=f"end_{user_id}")

        await q.edit_message_text(f"✅ Approved {user_id} for {minutes} mins ({pkg_key})")
        try:
            await context.bot.send_message(user_id, f"✅ Approved baby! 😍 Your {minutes} mins chat starts NOW! ⏰\n\nSend Hi, don't keep me waiting... 🥺💦\n\nTimer is running!")
            await context.bot.send_message(ADMIN_ID, f"⏰ Timer started for {user_id} - {minutes} mins will auto stop!")
        except: pass
        return

    if d.startswith("reject_"):
        if q.from_user.id != ADMIN_ID: return
        user_id = int(d.split("_")[1])
        await q.edit_message_text(f"❌ Rejected {user_id}")
        try: await context.bot.send_message(user_id, "❌ Payment not confirmed baby, send clear screenshot 💋")
        except: pass
        return

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # store pkg from invoice payload
    pkg_key = update.pre_checkout_query.invoice_payload
    context.user_data["last_pkg"] = pkg_key
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pkg_key = update.message.successful_payment.invoice_payload
    p = PACKAGES.get(pkg_key, PACKAGES["3min"])
    minutes = p["minutes"]
    user_id = update.effective_user.id
    end_time = datetime.now() + timedelta(minutes=minutes)
    ACTIVE_CHATS[user_id] = {"end": end_time, "pkg": pkg_key}
    context.job_queue.run_once(end_chat_job, when=minutes*60, data={"user_id": user_id}, name=f"end_{user_id}")
    await update.message.reply_text(f"⭐ Stars payment received! Your {minutes} mins starts NOW baby! ⏰ Send Hi 💋")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pkg_key = context.user_data.get("pkg", "3min")
    context.user_data["last_pkg"] = pkg_key
    await update.message.reply_text("📸 Got it baby... waiting approval 🥺 Don't keep me waiting...")
    if ADMIN_ID:
        try:
            kb = [[InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{update.effective_user.id}_{pkg_key}"), InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{update.effective_user.id}")]]
            await context.bot.send_photo(ADMIN_ID, photo=update.message.photo[-1].file_id, caption=f"📸 PAYMENT!\n\n👤 @{update.effective_user.username} ({update.effective_user.id})\n📦 {pkg_key} = {PACKAGES[pkg_key]['minutes']} mins\n\nApprove to START TIMER ⏰", reply_markup=InlineKeyboardMarkup(kb))
        except: pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # If it's admin chatting, just pass
    if user_id == ADMIN_ID:
        # Admin can chat freely
        return

    # Check if user has active paid chat
    if user_id in ACTIVE_CHATS:
        end = ACTIVE_CHATS[user_id]["end"]
        if datetime.now() > end:
            # Time up
            del ACTIVE_CHATS[user_id]
            await update.message.reply_text("⏰ Time's up baby! 🥺 Your time finished 💦\n\nChoose package to continue 👇", reply_markup=get_main_keyboard())
            return
        else:
            # Time left - forward to admin and allow chat
            remaining = end - datetime.now()
            mins_left = int(remaining.total_seconds() // 60)
            try:
                await context.bot.send_message(ADMIN_ID, f"💬 CLIENT @{update.effective_user.username} ({user_id}) [{mins_left}min left]: {update.message.text}")
            except: pass
            await update.message.reply_text(f"😘 Got it baby... ({mins_left} mins left) 🥺💦")
            return
    else:
        # No active chat - not paid
        if ADMIN_ID:
            try: await context.bot.send_message(ADMIN_ID, f"💬 UNPAID MSG @{update.effective_user.username} ({user_id}): {update.message.text}")
            except: pass
        await update.message.reply_text("😏 Baby you need to choose package first to chat with me 💋\n\nDon't keep me waiting daddy...", reply_markup=get_main_keyboard())

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot running with TIMER...")
    app.run_polling()