import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PreCheckoutQueryHandler, ContextTypes
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

app = Flask(__name__)
@app.route('/')
def home():
    return "Candy Bot Live"

VIP_TELEGRAM = "https://t.me/+eEsiq79bG6k2ODlk"
ONLYFANS_LINK = "https://onlyfans.com/candysquash"

PACKAGES = {
    "3min": {"label": "🍒 3 Mins", "price_kes": "50 KES", "price_usd": "$1", "stars": 25, "title": "Chat 3 Mins"},
    "5min": {"label": "🔥 5 Mins", "price_kes": "100 KES", "price_usd": "$2", "stars": 50, "title": "Chat 5 Mins"},
    "10min": {"label": "💋 10 Mins", "price_kes": "200 KES", "price_usd": "$4", "stars": 100, "title": "Chat 10 Mins"},
    "30min": {"label": "😍 30 Mins", "price_kes": "300 KES", "price_usd": "$6", "stars": 150, "title": "Chat 30 Mins"},
}

PAYMENTS = {
    "skrill": "💳 Skrill: mbithey7@gmail.com",
    "binance": "₿ Binance ID: 1282131122",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    text = "🔥 Welcome to Candy's Squash 💋\n\n😏 Baby I'm horny... waiting for you... 🛏️\n\n💬 Chatting ONLY - No video call ❌\n🎬 For videos join my VIP!\n\n💬 Choose package baby 👇"
    keyboard = []
    for k, v in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(f"{v['label']} - {v['price_kes']} / {v['price_usd']} / {v['stars']}⭐", callback_data=f"pkg_{k}")])
    keyboard.append([InlineKeyboardButton("🎬 My Videos - VIP Links 🔥", callback_data="vip_only")])
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_start":
        await start(update, context)
        return

    if data == "vip_only":
        text = "🎬 Candy's Private Videos 🔥\n\n👇 Join VIP:"
        keyboard = [
            [InlineKeyboardButton("🔥 JOIN VIP TELEGRAM 💦", url=VIP_TELEGRAM)],
            [InlineKeyboardButton("💦 ONLYFANS 🥵", url=ONLYFANS_LINK)],
            [InlineKeyboardButton("⬅️ Back 💬", callback_data="back_start")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("pkg_"):
        key = data.replace("pkg_", "")
        pkg = PACKAGES.get(key)
        context.user_data["pkg"] = key
        context.user_data["pkg_obj"] = pkg
        text = f"😍 {pkg['title']} 😍\n\n💰 {pkg['price_kes']} | {pkg['price_usd']} (Skrill/Binance) | {pkg['stars']} Stars ⭐\n\n⚠️ Chatting ONLY 💬\n❌ No video call\n\n👇 Choose pay method:"
        keyboard = [
            [InlineKeyboardButton(f"⭐ Pay {pkg['stars']} Stars Instant", callback_data=f"pay_stars_{key}")],
            [InlineKeyboardButton(f"💳 Skrill - {pkg['price_usd']}", callback_data=f"pay_skrill_{key}")],
            [InlineKeyboardButton(f"₿ Binance - {pkg['price_usd']}", callback_data=f"pay_binance_{key}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_start")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("pay_"):
        parts = data.split("_")
        pay_key = parts[1]
        pkg_key = parts[2]
        pkg = PACKAGES.get(pkg_key)
        context.user_data["pkg"] = pkg_key
        context.user_data["pkg_obj"] = pkg
        context.user_data["pay"] = pay_key

        if pay_key == "stars":
            try:
                await context.bot.send_invoice(
                    chat_id=query.from_user.id,
                    title=pkg['title'],
                    description=f"{pkg['label']} - Chatting ONLY",
                    payload=f"candy_{pkg_key}_{query.from_user.id}",
                    provider_token="",
                    currency="XTR",
                    prices=[LabeledPrice(label=pkg['label'], amount=pkg['stars'])]
                )
            except Exception as e:
                await query.edit_message_text(f"❌ Stars error baby, use Skrill/Binance: {e}")
        else:
            pay_info = PAYMENTS.get(pay_key, "")
            text = f"💰 Payment Details\n\n📦 {pkg['label']}\n💵 Amount: {pkg['price_usd']}\n\n{pay_info}\n\n📸 Send screenshot after paying {pkg['price_usd']} baby 😍"
            keyboard = [
                [InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{pay_key}")],
                [InlineKeyboardButton("⬅️ Back", callback_data=f"pkg_{pkg_key}")]
            ]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("paid_"):
        pkg = context.user_data.get("pkg_obj", {"label": "Package"})
        text = f"✅ Screenshot received baby! 💰\n📦 {pkg['label']} - CHAT ONLY\n\nWaiting approval ⏰💋"
        await query.edit_message_text(text)
        if ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰 PAID: @{query.from_user.username} ({query.from_user.id}) - {pkg['label']} - {data}")
            except:
                pass

    if data.startswith("approve_") or data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            return
        tid = int(data.split("_")[1])
        if "approve_" in data:
            await query.edit_message_text(f"✅ Approved {tid}")
            try:
                await context.bot.send_message(chat_id=tid, text=f"✅ Approved baby! Send Hi to start chat 😍\n\nVideos:\n{VIP_TELEGRAM}\n{ONLYFANS_LINK}")
            except:
                pass
        else:
            await query.edit_message_text(f"❌ Rejected {tid}")
            try:
                await context.bot.send_message(chat_id=tid, text="❌ Not confirmed baby, send clear screenshot 💋")
            except:
                pass

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pkg_key = context.user_data.get("pkg", "unknown")
    pkg = PACKAGES.get(pkg_key, {"label": pkg_key})
    await update.message.reply_text(f"✅ Stars Paid ⭐ {pkg['label']} - CHAT ONLY 💬\n\nSend Hi to start baby 💋🔥\n\nVideos: {VIP_TELEGRAM}")
    if ADMIN_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"⭐ STARS PAID: @{update.effective_user.username} - {pkg['label']} - {update.message.successful_payment.total_amount} Stars")
        except:
            pass

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Screenshot received baby 💦 Waiting approval ⏰")
    if ADMIN_ID:
        pkg = context.user_data.get("pkg_obj", {"label": "unknown"})
        keyboard = [
            [InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{update.effective_user.id}"),
             InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{update.effective_user.id}")]
        ]
        caption = f"📸 From @{update.effective_user.username} ({update.effective_user.id}) - {pkg['label']}"
        try:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set!")
    else:
        threading.Thread(target=run_flask, daemon=True).start()
        print("Bot running...")
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler(["start", "prices", "pay"], start))
        application.add_handler(CallbackQueryHandler(buttons))
        application.add_handler(PreCheckoutQueryHandler(precheckout))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.run_polling()