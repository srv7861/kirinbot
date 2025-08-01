
import os
import logging
from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, ContextTypes, filters
)

BOT_TOKEN = '7997418992:AAG5S1JVazuQS1xKQeWf2oASF-jwnhKLRas'
FORWARD_CHAT_ID = 1164872254  # Replace with your personal chat ID

USDT_AMOUNT, FUND_TYPE, CONFIRM_EXCHANGE, BANK_DETAILS, SCREENSHOT_UPLOAD, LANG_SELECTION = range(6)

RATES = {
    "1": 93.5,
    "2": 95.7,
    "3": 107.0
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEXTS = {
    'welcome_caption': {
        'en': "🦄 *Welcome to Kirin Payments!*",
        'hi': "🦄 *Kirin Payments में आपका स्वागत है!*"
    },
    'language_prompt': {
        'en': "Please choose your preferred language:",
        'hi': "कृपया अपनी भाषा चुनें:"
    },
    'start_usdt': {
        'en': "🌟 How many USDT would you like to sell today?",
        'hi': "🌟 आप कितने USDT बेचना चाहते हैं?"
    },
    'invalid_usdt': {
        'en': "❗ Please enter a valid USDT amount (numeric & greater than zero).",
        'hi': "❗ कृपया मान्य USDT राशि दर्ज करें (संख्या और शून्य से बड़ी)।"
    },
    'select_fund_type': {
        'en': (
            "📉 *Step 2:* Choose the fund type to proceed:\n\n"
            "🧾 *Today's Rates:*\n"
            "➤ Clean Fund: ₹93.5\n"
            "➤ Gaming Fund: ₹95.7\n"
            "➤ Stock Fund: ₹107.0\n\n"
            "_Tap on the desired fund option below_ 👇"
        ),
        'hi': (
            "📉 *चरण 2:* कृपया फंड प्रकार चुनें:\n\n"
            "🧾 *आज के दर:*\n"
            "➤ क्लीन फंड: ₹93.5\n"
            "➤ गेमिंग फंड: ₹95.7\n"
            "➤ स्टॉक फंड: ₹107.0\n\n"
            "_नीचे अपनी पसंद का विकल्प चुनें_ 👇"
        )
    },
    'confirm_exchange': {
        'en': "💸 You will receive: ₹{amount:,.2f}\n\n📌 Do you want to continue with this transaction?",
        'hi': "💸 आपको मिलेगा: ₹{amount:,.2f}\n\n📌 क्या आप इस लेन-देन को जारी रखना चाहते हैं?"
    },
    'cancelled': {
        'en': "🚫 Transaction cancelled.\n💬 Contact @kirinpaymentsmax for help.",
        'hi': "🚫 लेन-देन रद्द किया गया।\n💬 सहायता के लिए @kirinpaymentsmax से संपर्क करें।"
    },
    'ask_bank_details': {
        'en': "🏦 Step 3: Please enter your Indian bank details or UPI ID.\n_Format: Account Number + IFSC or UPI ID (e.g., name@upi)_",
        'hi': "🏦 चरण 3: कृपया अपने भारतीय बैंक विवरण या UPI ID दर्ज करें।\n_फ़ॉर्मेट: खाता संख्या + IFSC या UPI ID (जैसे name@upi)_"
    },
    'ask_send_usdt': {
        'en': (
            "📤 Step 4: Send the USDT to this wallet address:\n\n"
            "`TMJ42PnF7HsBc746sYy97PyiG74GyeYd8X`\n\n"
            "📝 Once sent, upload a screenshot with TXID or paste TXID below."
        ),
        'hi': (
            "📤 चरण 4: कृपया USDT इस वॉलेट पते पर भेजें:\n\n"
            "`TMJ42PnF7HsBc746sYy97PyiG74GyeYd8X`\n\n"
            "📝 भेजने के बाद, कृपया TXID के साथ स्क्रीनशॉट अपलोड करें या TXID नीचे पेस्ट करें।"
        )
    },
    'thank_you': {
        'en': (
            "🎉 Thank you for your submission!\n\n"
            "💵 Payout will be completed in 15–30 minutes.\n"
            "💬 Contact @kirinpaymentsmax for queries."
        ),
        'hi': (
            "🎉 आपके लेन-देन के लिए धन्यवाद!\n\n"
            "💵 भुगतान 15–30 मिनट में पूरा किया जाएगा।\n"
            "💬 किसी भी प्रश्न के लिए @kirinpaymentsmax से संपर्क करें।"
        )
    },
    'upload_prompt': {
        'en': "❗ Please upload a screenshot or paste the TXID.",
        'hi': "❗ कृपया स्क्रीनशॉट अपलोड करें या TXID पेस्ट करें।"
    },
    'cancel_msg': {
        'en': "🚫 Transaction cancelled. Type /start to begin again.",
        'hi': "🚫 लेन-देन रद्द किया गया। फिर शुरू करने के लिए /start टाइप करें।"
    },
    'select_language_invalid': {
        'en': "Please select a valid option.",
        'hi': "कृपया सही विकल्प चुनें।"
    },
    'select_language_prompt': {
        'en': "Select language / भाषा चुनें:",
        'hi': "Select language / भाषा चुनें:"
    }
}

def get_text(lang, key, **kwargs):
    text = TEXTS.get(key, {}).get(lang, "")
    if kwargs:
        return text.format(**kwargs)
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logo_path = 'kirin_unicorn_logo.png'  # Your logo image path here
    lang = 'en'  # default until user selects

    try:
        with open(logo_path, 'rb') as logo:
            await update.message.reply_photo(
                photo=InputFile(logo),
                caption=f"{get_text(lang, 'welcome_caption')}\n\n{get_text(lang, 'language_prompt')}",
                parse_mode='Markdown'
            )
    except Exception:
        await update.message.reply_text(
            f"{get_text(lang, 'welcome_caption')}\n\n{get_text(lang, 'language_prompt')}",
            parse_mode='Markdown'
        )

    keyboard = [['🇮🇳 हिंदी', '🇬🇧 English']]
    await update.message.reply_text(
        get_text(lang, 'select_language_prompt'),
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LANG_SELECTION

async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip()
    if choice == '🇮🇳 हिंदी':
        context.user_data['lang'] = 'hi'
        await update.message.reply_text(
            get_text('hi', 'start_usdt'),
            reply_markup=ReplyKeyboardMarkup([['Cancel']], resize_keyboard=True)
        )
    elif choice == '🇬🇧 English':
        context.user_data['lang'] = 'en'
        await update.message.reply_text(
            get_text('en', 'start_usdt'),
            reply_markup=ReplyKeyboardMarkup([['Cancel']], resize_keyboard=True)
        )
    else:
        await update.message.reply_text(get_text('en', 'select_language_invalid'))
        return LANG_SELECTION

    return USDT_AMOUNT

async def usdt_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get('lang', 'en')
    text = update.message.text.strip()
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
        context.user_data['usdt'] = amount

        try:
            await context.bot.forward_message(
                chat_id=FORWARD_CHAT_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
        except Exception as e:
            logger.warning(f"❌ Forwarding failed: {e}")

        keyboard = [
            [InlineKeyboardButton("1️⃣ Clean Fund (₹93.5)", callback_data="1")],
            [InlineKeyboardButton("2️⃣ Gaming Fund (₹95.7)", callback_data="2")],
            [InlineKeyboardButton("3️⃣ Stock Fund (₹107)", callback_data="3")]
        ]
        await update.message.reply_text(
            get_text(lang, 'select_fund_type'),
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return FUND_TYPE

    except Exception:
        await update.message.reply_text(get_text(lang, 'invalid_usdt'))
        return USDT_AMOUNT

async def fund_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get('lang', 'en')
    query = update.callback_query
    await query.answer()
    fund_type = query.data
    context.user_data['fund_type'] = fund_type

    rate = RATES[fund_type]
    usdt = context.user_data['usdt']
    amount_inr = usdt * rate
    context.user_data['received_amount'] = amount_inr

    try:
        await context.bot.forward_message(
            chat_id=FORWARD_CHAT_ID,
            from_chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
    except Exception as e:
        logger.warning(f"❌ Forwarding failed: {e}")

    confirm_msg = get_text(lang, 'confirm_exchange', amount=amount_inr)
    confirm_buttons = [
        [InlineKeyboardButton("✅ Yes", callback_data="yes")],
        [InlineKeyboardButton("❌ No", callback_data="no")]
    ]
    await query.edit_message_text(
        confirm_msg,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(confirm_buttons)
    )
    return CONFIRM_EXCHANGE

async def confirm_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get('lang', 'en')
    query = update.callback_query
    await query.answer()
    if query.data == "no":
        await query.edit_message_text(get_text(lang, 'cancelled'), parse_mode='Markdown')
        return ConversationHandler.END

    await query.edit_message_text(get_text(lang, 'ask_bank_details'), parse_mode='Markdown')
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="✍️ " + ("Type your bank details below or press Cancel." if lang == 'en' else "नीचे अपना बैंक विवरण टाइप करें या Cancel दबाएं।"),
        reply_markup=ReplyKeyboardMarkup([['Cancel']], resize_keyboard=True)
    )
    return BANK_DETAILS

async def bank_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get('lang', 'en')
    text = update.message.text.strip()
    context.user_data['bank'] = text

    try:
        await context.bot.forward_message(
            chat_id=FORWARD_CHAT_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logger.warning(f"❌ Forwarding failed: {e}")

    await update.message.reply_text(
        get_text(lang, 'ask_send_usdt'),
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([['Cancel']], resize_keyboard=True)
    )
    return SCREENSHOT_UPLOAD

async def screenshot_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get('lang', 'en')
    if update.message.text or update.message.photo or update.message.document:
        try:
            await context.bot.forward_message(
                chat_id=FORWARD_CHAT_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
        except Exception as e:
            logger.warning(f"❌ Forwarding failed: {e}")

        await update.message.reply_text(
            get_text(lang, 'thank_you'),
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    await update.message.reply_text(get_text(lang, 'upload_prompt'), parse_mode='Markdown')
    return SCREENSHOT_UPLOAD

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(
        get_text(lang, 'cancel_msg'),
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 Your chat ID is:\n`{update.message.chat_id}`",
        parse_mode='Markdown'
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANG_SELECTION: [MessageHandler(filters.Regex('^(🇮🇳 हिंदी|🇬🇧 English)$'), language_selection)],
            USDT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, usdt_amount)],
            FUND_TYPE: [CallbackQueryHandler(fund_type)],
            CONFIRM_EXCHANGE: [CallbackQueryHandler(confirm_exchange)],
            BANK_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bank_details)],
            SCREENSHOT_UPLOAD: [MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, screenshot_upload)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('id', get_id))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == '__main__':
    main()
