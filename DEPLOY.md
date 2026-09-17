# Deploy to Railway in 5 Minutes

**Goal: Get trading signals live on Telegram today.**

---

## Step 1: Get Telegram Bot Token (2 min)

1. Open Telegram → Search `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "Trading Signals Bot")
4. Copy the **bot token** (looks like: `123456789:ABCDefGhIjKlMnOpQrStUvWxYz`)
5. **Save this token** → you'll need it in Step 4

---

## Step 2: Create GitHub Repo (2 min)

1. Go to github.com → New Repository
2. Name: `trading-signals`
3. Add these files:
   ```
   graham.py
   main.py
   telegram_bot.py
   daily_screening.py
   test_analysis.py
   requirements.txt
   Dockerfile
   railway.toml
   README.md
   .env.example
   ```
4. Commit & Push

---

## Step 3: Deploy to Railway (1 min)

1. Go to **railway.app** → Sign up (free)
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Select your `trading-signals` repo
4. Click **Deploy**
5. Wait 2-3 min for build to finish ✅

---

## Step 4: Configure Environment Variables (1 min)

In Railway dashboard:

1. Click your project
2. Go to **"Variables"** tab
3. Add:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_from_step_1
   API_BASE_URL=https://your-railway-url.railway.app
   ```
4. Click **Deploy**

---

## Step 5: Test the Bot (1 min)

1. Open Telegram → Find your bot (name from Step 1)
2. Send `/start`
3. Bot responds: "Welcome! Send /add AAPL..."
4. Send `/add AAPL`
5. Bot responds: "✅ Added AAPL to your watchlist"
6. Send `/list`
7. Bot responds: "📊 Your Watchlist: • AAPL"

---

## ✅ You're Live!

**Daily signals will be sent at 5 PM UTC to your watchlist.**

Example alert (5:00 PM UTC tomorrow):
```
✅ SIGNAL: BUY AAPL
Current Price: $150.00
Intrinsic Value: $187.50
Margin of Safety: +25%
Graham Criteria: 6/7 ✅
Confidence: 78%
```

---

## Common Issues

### Bot not responding
- Check `TELEGRAM_BOT_TOKEN` is correct in Railway variables
- Redeploy: Railway dashboard → Deploy button
- Wait 2 min for new version to start

### No daily signals
- Check time is past 5 PM UTC (17:00 UTC)
- Job runs daily at that exact time
- Signals only generated if stock passes Graham's 7 criteria

### API errors
- Check logs: Railway dashboard → "Logs" tab
- Verify yfinance can reach Yahoo Finance (network issue?)
- Try `/add MSFT` (more liquid stock, less likely to fail)

---

## Next Steps (V1+)

After 1 week of live signals:
1. Add PostgreSQL database
2. Build React dashboard
3. Add technical indicators (momentum, trend)
4. Track signal accuracy

For now: **collect signals → validate accuracy → iterate.**

---

## Questions?

Check README.md for full API docs, command reference, and architecture.

**You're ready to launch! 🚀**
