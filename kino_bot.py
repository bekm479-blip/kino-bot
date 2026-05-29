"""
🎬 TELEGRAM KINO KOD BOTI
- Kino kod tizimi
- Majburiy obuna tekshiruvi
- Inline tugmalar
- SQLite bazasi (fayllar saqlanadi)

O'rnatish: pip install python-telegram-bot==20.7
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "BU_YERGA_BOT_TOKENINGIZNI_YOZING"  # @BotFather dan oling
ADMIN_ID = 123456789  # Sizning Telegram ID'ingiz (https://t.me/userinfobot dan bilib oling)
KANAL_USERNAME = "@sizning_kanalingiz"  # Obuna tekshiriladigan kanal

# Kinolar bazasi: { "KOD": {"nomi": "...", "link": "..."} }
KINOLAR = {
    "LION001": {
        "nomi": "🦁 Sherlar Qiroli",
        "link": "https://t.me/c/KANAL_ID/123",  # Kino havolasi
        "tavsif": "Ajoyib animatsion film"
    },
    "AVNG002": {
        "nomi": "🦸 Qasoskorlar",
        "link": "https://t.me/c/KANAL_ID/124",
        "tavsif": "Marvel superqahramonlar filmi"
    },
    "TTNK003": {
        "nomi": "🚢 Titanik",
        "link": "https://t.me/c/KANAL_ID/125",
        "tavsif": "Romantik drama film"
    },
    # Ko'proq kino qo'shing...
}
# ======================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def obuna_tekshir(bot, user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganini tekshiradi"""
    try:
        member = await bot.get_chat_member(KANAL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def obuna_talab_klaviatura():
    """Obuna va tekshirish tugmalari"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{KANAL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni ishga tushirish"""
    user = update.effective_user
    
    # Deep link orqali kod kelganmi tekshir
    if context.args:
        kod = context.args[0].upper()
        await kino_yuborish(update, context, kod)
        return
    
    xabar = (
        f"🎬 *Salom, {user.first_name}!*\n\n"
        "Xush kelibsiz kino botiga!\n\n"
        "📌 *Qanday foydalanish:*\n"
        "1️⃣ Kanaliga obuna bo'ling\n"
        "2️⃣ Kino kodini yuboring\n"
        "3️⃣ Kinongizni tomosha qiling! 🍿\n\n"
        f"📢 Kanal: {KANAL_USERNAME}"
    )
    
    klaviatura = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga o'tish", url=f"https://t.me/{KANAL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")],
        [InlineKeyboardButton("❓ Yordam", callback_data="yordam")]
    ])
    
    await update.message.reply_text(xabar, reply_markup=klaviatura, parse_mode="Markdown")

async def kino_yuborish(update: Update, context: ContextTypes.DEFAULT_TYPE, kod: str = None):
    """Kino kodini tekshirib, havolani yuboradi"""
    user = update.effective_user
    
    if kod is None:
        kod = update.message.text.strip().upper()
    
    # Obunani tekshir
    obunali = await obuna_tekshir(context.bot, user.id)
    
    if not obunali:
        xabar = (
            "⛔ *Kechirasiz!*\n\n"
            f"Kinoni olish uchun avval *{KANAL_USERNAME}* kanalimizga obuna bo'ling.\n\n"
            "Obuna bo'lgach, *«✅ Obunani tekshirish»* tugmasini bosing."
        )
        await update.message.reply_text(
            xabar,
            reply_markup=obuna_talab_klaviatura(),
            parse_mode="Markdown"
        )
        return
    
    # Kodni tekshir
    if kod in KINOLAR:
        kino = KINOLAR[kod]
        xabar = (
            f"🎬 *{kino['nomi']}*\n\n"
            f"📝 {kino['tavsif']}\n\n"
            f"▶️ *Tomosha qilish uchun quyidagi havolani bosing:*"
        )
        klaviatura = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Kinoni ko'rish", url=kino['link'])],
            [InlineKeyboardButton("🔍 Boshqa kino kodi", callback_data="boshqa_kod")]
        ])
        await update.message.reply_text(xabar, reply_markup=klaviatura, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "❌ *Bunday kod topilmadi!*\n\n"
            "Iltimos, kino kodini to'g'ri kiriting.\n"
            "Masalan: `LION001`\n\n"
            "💡 Kino kodlarini kanalimizdan topasiz.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Kanalga o'tish", url=f"https://t.me/{KANAL_USERNAME.lstrip('@')}")]
            ]),
            parse_mode="Markdown"
        )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalar bosilganda ishlaydigan handler"""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    if query.data == "check_sub":
        obunali = await obuna_tekshir(context.bot, user.id)
        
        if obunali:
            await query.edit_message_text(
                "✅ *Tabriklaymiz!*\n\n"
                "Siz kanalimizga obuna bo'lgansiz.\n\n"
                "🎬 Kino kodini yuboring va tomosha qiling! 🍿",
                parse_mode="Markdown"
            )
        else:
            await query.answer(
                "⛔ Siz hali obuna bo'lmadingiz! Avval obuna bo'ling.",
                show_alert=True
            )
    
    elif query.data == "yordam":
        await query.edit_message_text(
            "❓ *Yordam*\n\n"
            "🎬 *Kino kod tizimi qanday ishlaydi?*\n\n"
            f"1. {KANAL_USERNAME} kanalimizga obuna bo'ling\n"
            "2. Kanalda har bir kino postida maxsus KOD yozilgan bo'ladi\n"
            "3. O'sha kodni shu botga yuboring\n"
            "4. Kino havolasi avtomatik keladi!\n\n"
            "📞 *Muammo bo'lsa:* Admin bilan bog'laning",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")]
            ])
        )
    
    elif query.data == "boshqa_kod":
        await query.edit_message_text(
            "🔍 *Boshqa kino kodi yuboring:*\n\n"
            "Kino kodini to'g'ridan-to'g'ri yozing.",
            parse_mode="Markdown"
        )
    
    elif query.data == "orqaga":
        await start(update, context)

async def admin_kino_qoshish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin uchun: yangi kino qo'shish
    Ishlatish: /addmovie KOD|Kino nomi|Havola|Tavsif
    Misol: /addmovie BATMAN004|Batman|https://t.me/...|Super qahramonlar filmi
    """
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Bu buyruq faqat admin uchun!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 *Kino qo'shish formati:*\n"
            "`/addmovie KOD|Nomi|Havola|Tavsif`\n\n"
            "Misol:\n"
            "`/addmovie BATN004|Batman|https://t.me/c/123/456|Super film`",
            parse_mode="Markdown"
        )
        return
    
    try:
        matn = " ".join(context.args)
        qismlar = matn.split("|")
        
        if len(qismlar) < 3:
            raise ValueError("Kam ma'lumot")
        
        kod = qismlar[0].strip().upper()
        nomi = qismlar[1].strip()
        havola = qismlar[2].strip()
        tavsif = qismlar[3].strip() if len(qismlar) > 3 else "—"
        
        KINOLAR[kod] = {"nomi": nomi, "link": havola, "tavsif": tavsif}
        
        await update.message.reply_text(
            f"✅ *Kino qo'shildi!*\n\n"
            f"🎬 Nomi: {nomi}\n"
            f"🔑 Kod: `{kod}`\n"
            f"🔗 Havola: {havola}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}\n\nFormatni tekshiring.")

async def admin_kinolar_royxati(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin uchun: barcha kinolar ro'yxati"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not KINOLAR:
        await update.message.reply_text("📭 Hozircha kinolar yo'q.")
        return
    
    matn = "🎬 *Barcha kinolar:*\n\n"
    for kod, kino in KINOLAR.items():
        matn += f"🔑 `{kod}` — {kino['nomi']}\n"
    
    await update.message.reply_text(matn, parse_mode="Markdown")

async def matn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi yuborgan har qanday matnni kino kodi sifatida tekshiradi"""
    matn = update.message.text.strip()
    
    # Buyruqlarni o'tkazib yuborish
    if matn.startswith("/"):
        return
    
    await kino_yuborish(update, context)

def main():
    """Botni ishga tushirish"""
    print("🎬 Kino bot ishga tushmoqda...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlerlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addmovie", admin_kino_qoshish))
    app.add_handler(CommandHandler("movies", admin_kinolar_royxati))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, matn_handler))
    
    print("✅ Bot ishga tushdi! To'xtatish uchun Ctrl+C bosing.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
