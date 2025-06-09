# Analyst

An AI-based cryptocurrency research bot that continuously collects market data, generates analysis and interacts via Telegram. It caches market data with Redis, stores research in Postgres and can issue price alerts via Telegram.

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

### Docker Compose

You can spin up the full stack using `docker-compose` which includes Redis and Postgres:

```bash
docker compose up -d
```

Ensure `TELEGRAM_BOT_TOKEN` is exported in your environment before running the command.

## Running natively on Ubuntu

You can also run the bot directly on an Ubuntu machine without Docker:

```bash
sudo apt-get update && sudo apt-get install -y \
    python3 python3-venv python3-pip git curl build-essential
curl -fsSL https://ollama.ai/install.sh | bash
python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt
export TELEGRAM_BOT_TOKEN=<your token>
bash start.sh
```

This setup mirrors the Docker container which is based on Ubuntu 22.04.

## Kubernetes Deployment

Kubernetes manifests are provided in the `k8s/` directory:

```bash
kubectl apply -f k8s/
```

Secrets for the Telegram token should be created separately.

