# 📈 MSTR Trading Bot

Automated trading signal bot that analyzes **MicroStrategy (MSTR)** stock data, calculates the 200-day moving average, and sends a **daily trading signal** (with chart) to a **Telegram channel**.

## 🚀 Features

- ✅ Download and analyze **10 years** of MSTR historical data  
- ✅ Calculate **200-day moving average (MA200)**  
- ✅ Detect and signal trading conditions  
- ✅ Generate and send charts with analysis  
- ✅ **Telegram integration** to send signals automatically  
- ✅ **Dockerized** and scheduled to run **daily at 6 AM (Mexico City time)**

---

## ⚙️ How it works

1. **Fetch MSTR data** from Yahoo Finance  
2. **Calculate MA200** to analyze long-term trend  
3. **Check conditions:**  
   - Current price > MA200 → Possible **bullish signal**  
   - Current price < MA200 → Possible **bearish signal**  
4. **Generate chart** with current price and MA200  
5. **Send Telegram message** + chart to configured channel

---

## 🐳 Dockerized Execution

The bot runs inside a Docker container and is scheduled via **cron** to run automatically every day.

### Build and run

```bash
docker-compose up --build -d
