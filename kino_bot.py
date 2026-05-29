"""
🎬 TELEGRAM KINO KOD BOTI
- Kino kod tizimi
- Majburiy obuna tekshiruvi
- Inline tugmalar
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
KANAL_USERNAME = os.environ.get("KANAL_USERNAME", "@sizning_kanalingiz")

# Kinolar bazasi
KINOLAR = {
    "LION001": {
        "nomi": "🦁 Sherlar Qiroli",
        "link": "https://t.me/dunyofilmlari/1",
        "tavsif": "Ajoyib animatsion film"
    },
    "AVNG002": {
        "nomi": "🦸 Qasoskorlar",
        "link": "https://t.me/dunyofilmlari/2",
        "tavsif": "Marvel superqahramonlar filmi"
    },
}
# ======================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def obuna_tekshir(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(KANAL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def obuna_talab_klaviatura():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{KANAL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if context.args:
        kod = context.args[0].upper()
        await kino_yuborish(update, context, kod)
        return

    xabar = (
        f"🎬 *Salom, {user.first_name}!*\n\n"
        "Xush kelibsiz kino botiga!\n\n"
        "📌 *Qanday foydalanish:*\n"
        "1️⃣ Kanalga obuna bo'ling\n"
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
    user = update.effective_user

    if kod is None:
        kod = update.message.text.strip().upper()

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
        user = query.from_user
        xabar = (
            f"🎬 *Salom, {user.first_name}!*\n\n"
            "Kino kodini yuboring! 🍿"
        )
        klaviatura = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Kanalga o'tish", url=f"https://t.me/{KANAL_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")],
        ])
        await query.edit_message_text(xabar, reply_markup=klaviatura, parse_mode="Markdown")

async def admin_kino_qoshish(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(f"❌ Xato: {e}")

async def admin_kinolar_royxati(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    matn = "🎬 *Barcha kinolar:*\n\n"
    for kod, kino in KINOLAR.items():
        matn += f"🔑 `{kod}` — {kino['nomi']}\n"
    await update.message.reply_text(matn, parse_mode="Markdown")

async def matn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("/"):
        return
    await kino_yuborish(update, context)

def main():
    print("🎬 Kino bot ishga tushmoqda...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addmovie", admin_kino_qoshish))
    app.add_handler(CommandHandler("movies", admin_kinolar_royxati))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, matn_handler))
    print("✅ Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
