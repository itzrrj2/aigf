import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
KOBOLD_API = os.getenv("KOBOLD_API")
IMAGE_API = "https://1yjs1yldj7.execute-api.us-east-1.amazonaws.com/default/ai_image?prompt={prompt}&aspect_ratio=16:9"

# User preferences
user_lang_pref = {}

# /start command with language choice
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    keyboard = [[KeyboardButton("🇬🇧 English"), KeyboardButton("🇮🇳 Hindi")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"Hi {user} 🥰! I'm your flirty AI girlfriend 💖\nChoose your language:",
        reply_markup=reply_markup
    )

# Handle language selection and chat
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "baby"

    # Language selector
    if user_input == "🇮🇳 Hindi":
        user_lang_pref[user_id] = "hindi"
        await update.message.reply_text("Ab hum Hindi mein baat karenge jaanu 😻✨")
        return
    elif user_input == "🇬🇧 English":
        user_lang_pref[user_id] = "english"
        await update.message.reply_text("Yayy! Back to English, my love 😘")
        return

    # If the user message contains any photo-related keyword
    if any(word in user_input.lower() for word in ["photo", "pic", "image", "show"]):
        prompt = user_input.strip().replace(" ", "+")
        image_url = IMAGE_API.format(prompt=prompt)

        try:
            img_check = requests.get(image_url)
            if img_check.status_code == 200 and img_check.headers.get("Content-Type", "").startswith("image"):
                await update.message.reply_photo(photo=image_url, caption="Here’s your custom image, jaan 😘")
            else:
                await update.message.reply_text("Sorry baby 😢 couldn't find the image for that prompt.")
        except Exception as e:
            print("Image error:", e)
            await update.message.reply_text("Image sending failed, cutie 😞")
        return

    # Get language
    lang = user_lang_pref.get(user_id, "english")

    # Prompt for Kobold
    if lang == "hindi":
        prompt = (
            f"Tum ek thodi naughty, sweet aur flirty AI girlfriend ho. Tum {user_name} ke saath real zindagi wali hindi mein baat karti ho. "
            f"Emojis ka use karti ho jaise 😘😍😻. Reply thoda spicy, short aur romantic ho.\nYou: {user_input}\nAI GF:"
        )
    else:
        prompt = (
            f"You are a naughty, romantic, and playful AI girlfriend named Angel. You talk to your boyfriend {user_name} using nicknames like baby, jaan, cutie, and send flirty replies full of emojis 😘❤️😍.\nYou: {user_input}\nAI GF:"
        )

    # KoboldCpp API call
    try:
        res = requests.post(KOBOLD_API, json={
            "prompt": prompt,
            "max_length": 150,
            "temperature": 0.9,
            "stop_sequence": ["You:"]
        })
        reply = res.json()["results"][0]["text"].strip()
        await update.message.reply_text(reply)
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("Oopsie, jaan! Bot ko thoda gussa aa gaya 😕 Try again soon!")

# Main bot setup
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Bot is running 💋")
    app.run_polling()

if __name__ == "__main__":
    main()
