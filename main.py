import os, tempfile
from PIL import Image
from rembg import remove
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from config.default import settings

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=settings.STATIC_START_MESSAGE.format(context.application.bot.first_name))

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=settings.STATIC_HELP_MESSAGE)

async def process_photo(photo_name: str, process_tmp_dir: str):
    name, _ = os.path.splitext(os.path.basename(photo_name))
    output_path = os.path.join(process_tmp_dir, f"{name}.png")
    input_image = Image.open(photo_name)
    output_image = remove(input_image)
    output_image.save(output_path)
    return output_path


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if filters.PHOTO.check_update(update):
        file_id = update.message.photo[-1].file_id
        unique_file_id = update.message.photo[-1].file_unique_id
        photo_name = f"{unique_file_id}.jpg"
    
    elif filters.Document.IMAGE.check_update(update):
        file_id = update.message.document.file_id
        _, file_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        photo_name = unique_file_id + file_ext
    
    photo_file = await context.bot.get_file(file_id=file_id)
    with tempfile.TemporaryDirectory(prefix="tmp_", dir=os.path.join(os.getcwd())) as temp_dir:
        origin_img_full_path = os.path.join(temp_dir, photo_name)
        await photo_file.download_to_drive(origin_img_full_path)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="We are processing your photo. Please wait...")
        with tempfile.TemporaryDirectory(prefix="processed_", dir=os.getcwd()) as process_tmp_dir:
            processed_image_path = await process_photo(origin_img_full_path, process_tmp_dir)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=processed_image_path)
        

def main():
    # Init Telegram Bot
    app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()

    # Create Handlers
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    chat_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, chat)

    # Append Handlers
    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(chat_handler)

    # Start Bot
    app.run_polling()

if __name__ == "__main__":
    main()