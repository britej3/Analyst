# Analyst

An AI-based cryptocurrency research bot that continuously collects market data, generates analysis and interacts via Telegram.

Set the `TELEGRAM_BOT_TOKEN` environment variable with your bot's token before running the container.

## Running with Docker

1. Build the image:

```bash
docker build -t analyst-bot .
```

2. Run the container supplying your Telegram bot token:

```bash
docker run -e TELEGRAM_BOT_TOKEN=<your token> analyst-bot
```

The container launches an Ollama service and the Telegram bot automatically.

