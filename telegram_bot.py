"""
Telegram Bot for Trading Signals
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import requests
import json

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingSignalsBot:
    """Telegram bot for trading signals"""

    def __init__(self, token: str, api_base: str):
        self.token = token
        self.api_base = api_base
        self.app = Application.builder().token(token).build()
        self._register_handlers()

    def _register_handlers(self):
        """Register command handlers"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("add", self.add_stock))
        self.app.add_handler(CommandHandler("remove", self.remove_stock))
        self.app.add_handler(CommandHandler("list", self.list_watchlist))
        self.app.add_handler(CommandHandler("analyze", self.analyze_stock))
        self.app.add_handler(CommandHandler("help", self.help_command))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name

        message = (
            f"🚀 Welcome to Trading Signals Bot, {user_name}!\n\n"
            "I analyze stocks using Benjamin Graham's value investing framework.\n\n"
            "📋 Available commands:\n"
            "• /add AAPL - Add stock to your watchlist\n"
            "• /remove AAPL - Remove stock\n"
            "• /list - Show your watchlist\n"
            "• /analyze AAPL - Get detailed analysis\n"
            "• /help - Show all commands\n\n"
            "Daily signals sent at 5 PM UTC 🔔"
        )

        await update.message.reply_text(message)

    async def add_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add SYMBOL command"""
        user_id = str(update.effective_user.id)

        if not context.args:
            await update.message.reply_text("❌ Usage: /add AAPL")
            return

        symbol = context.args[0].upper()

        try:
            response = requests.post(
                f"{self.api_base}/api/watchlist/add",
                params={"user_id": user_id, "symbol": symbol}
            )

            if response.status_code == 200:
                data = response.json()
                watchlist = data.get("watchlist", [])
                await update.message.reply_text(
                    f"✅ Added {symbol} to your watchlist\n\n"
                    f"Current watchlist: {', '.join(watchlist)}"
                )
            else:
                await update.message.reply_text(f"❌ Error adding {symbol}")

        except Exception as e:
            logger.error(f"Error adding stock: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def remove_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove SYMBOL command"""
        user_id = str(update.effective_user.id)

        if not context.args:
            await update.message.reply_text("❌ Usage: /remove AAPL")
            return

        symbol = context.args[0].upper()

        try:
            response = requests.delete(
                f"{self.api_base}/api/watchlist/remove",
                params={"user_id": user_id, "symbol": symbol}
            )

            await update.message.reply_text(f"✅ Removed {symbol} from watchlist")

        except Exception as e:
            logger.error(f"Error removing stock: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def list_watchlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        user_id = str(update.effective_user.id)

        try:
            response = requests.get(f"{self.api_base}/api/watchlist/{user_id}")

            if response.status_code == 200:
                watchlist = response.json()

                if not watchlist:
                    await update.message.reply_text(
                        "Your watchlist is empty.\nUse /add AAPL to add stocks."
                    )
                else:
                    message = "📊 Your Watchlist:\n\n"
                    for symbol in watchlist:
                        message += f"• {symbol}\n"
                    await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error listing watchlist: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def analyze_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze SYMBOL command (placeholder for now)"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /analyze AAPL")
            return

        symbol = context.args[0].upper()

        # In production, fetch actual data from yfinance and call /api/analyze
        await update.message.reply_text(
            f"📊 Analysis for {symbol}\n\n"
            f"(Detailed analysis coming in V1 - check dashboard for now)"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = (
            "🤖 Trading Signals Bot - Help\n\n"
            "Graham's 7-Stage Stock Analysis:\n"
            "1. Country Economic Analysis\n"
            "2. Industry Attractiveness\n"
            "3. Company Quality (Graham's 7 Criteria)\n"
            "4. Valuation Calculation\n"
            "5. Intrinsic Value vs Market Price\n"
            "6-7. Risk Assessment\n\n"
            "📌 Commands:\n"
            "/start - Welcome message\n"
            "/add SYMBOL - Add to watchlist\n"
            "/remove SYMBOL - Remove from watchlist\n"
            "/list - Show watchlist\n"
            "/analyze SYMBOL - Detailed analysis\n"
            "/help - This message\n\n"
            "⏰ Daily signals at 5 PM UTC\n"
            "🔔 Alerts: BUY (✅), SELL (⚠️), HOLD (⏸️), SKIP (❌)"
        )
        await update.message.reply_text(message)

    async def send_signal_alert(
        self,
        user_id: int,
        symbol: str,
        signal: str,
        price: float,
        iv: float,
        margin: float,
        graham_score: int,
        confidence: float
    ):
        """Send signal alert to user (called by scheduler)"""
        signal_emoji = {
            "BUY": "✅",
            "SELL": "⚠️",
            "HOLD": "⏸️",
            "SKIP": "❌",
        }

        emoji = signal_emoji.get(signal, "📊")

        message = (
            f"{emoji} SIGNAL: {signal} {symbol}\n"
            f"{'='*35}\n"
            f"💰 Current Price: ${price:.2f}\n"
            f"📈 Intrinsic Value: ${iv:.2f}\n"
            f"✨ Margin of Safety: {margin:+.1f}%\n\n"
            f"📋 Graham Criteria: {graham_score}/7 {'✅' if graham_score >= 5 else '⚠️'}\n"
            f"🎯 Confidence: {confidence:.0%}\n"
        )

        try:
            await self.app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"Signal alert sent to {user_id}: {symbol} {signal}")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")

    def run(self):
        """Start the bot"""
        logger.info("Starting Trading Signals Bot...")
        self.app.run_polling()


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set in .env")
        print("Get a token from @BotFather on Telegram")
        exit(1)

    bot = TradingSignalsBot(TELEGRAM_BOT_TOKEN, API_BASE_URL)
    bot.run()
