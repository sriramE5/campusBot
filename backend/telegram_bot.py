import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from pathlib import Path

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://localhost:8000"

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    welcome_message = (
        " Welcome to Campus Bot!\n\n"
        "I can help you with information about the campus, events, and more.\n\n"
        "Here are some commands you can use:\n"
        "/events - List upcoming campus events\n"
        "/help - Show this help message\n\n"
        "Or just type your question and I'll do my best to help!"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   
    help_text = (
        "*Campus Bot Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot and see welcome message\n"
        "/events - List upcoming campus events\n"
        "/help - Show this help message\n\n"
        "You can also ask me questions about the campus, and I'll try to help!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def list_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List upcoming campus events."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/events")
            response.raise_for_status()
            events = response.json()
            
            if not events:
                await update.message.reply_text("No upcoming events found.")
                return
                
            events_text = "📅 *Upcoming Events*\n\n"
            for event in events:
                events_text += (
                    f"*{event['name']}*\n"
                    f"📅 {event['date']}\n"
                    f"📍 {event['location']}\n"
                    f"ℹ️ {event['details']}\n\n"
                )
            
            await update.message.reply_text(events_text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        await update.message.reply_text("Sorry, I couldn't fetch the events right now. Please try again later.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and send them to the chatbot API."""
    user_message = update.message.text
    user = update.effective_user
    
    logger.info(f"Message from {user.first_name} ({user.id}): {user_message}")
    
    if not user_message:
        await update.message.reply_text("Please send a text message.")
        return
    
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/chat",
                json={"message": user_message},
                timeout=30.0
            )
            response.raise_for_status()
            bot_response = response.json().get("response", "I'm not sure how to respond to that.")
            
            if len(bot_response) > 4000:
                parts = bot_response.split('\n\n')
                current_part = ""
                
                for part in parts:
                    if len(current_part) + len(part) > 4000:
                        await update.message.reply_text(current_part)
                        current_part = part + "\n\n"
                    else:
                        current_part += part + "\n\n"
    
                if current_part.strip():
                    await update.message.reply_text(current_part.strip())
            else:
                await update.message.reply_text(bot_response)
                
    except httpx.TimeoutException:
        await update.message.reply_text("I'm taking too long to respond. Please try again in a moment.")
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("Sorry, I encountered an error processing your message. Please try again later.")


def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("events", list_events))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
 
    application.add_error_handler(error_handler)
    
    logger.info("Starting bot...")
    application.run_polling()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, 'message') and update.message:
        await update.message.reply_text(
            "An error occurred while processing your request. The developers have been notified."
        )


if __name__ == "__main__":
    main()
