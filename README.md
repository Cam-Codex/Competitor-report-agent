# Competitor Report Agent

This project provides a simple daily agent that scans competitor blogs and
industry news for updates related to agentic data & analytics. It generates
an HTML report and can send a TLDR email digest.

## Configuration

Feeds are defined in `feeds.yaml`. Each entry contains a `name`, `url`, and
optional `max_items`.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the agent to build the HTML report and JSON data used by the React app:

```bash
python news_agent.py --config feeds.yaml \
  --output public/index.html \
  --json frontend/public/articles.json
```

Set the following environment variables to enable email digest sending:

- `SMTP_HOST`, `SMTP_PORT` (default `587`)
- `SMTP_USER`, `SMTP_PASS`
- `EMAIL_FROM`, `EMAIL_TO` (comma-separated recipients)

Then run:

```bash
python news_agent.py --send-email
```

Schedule the script via `cron` or any task scheduler to run daily.

## React app

A simple React frontend lives under `frontend/`. It groups articles by vendor
or industry and includes a search bar.

Install dependencies and start the dev server:

```bash
cd frontend
npm install
npm run dev
```

The React app expects `articles.json` in its `public` directory. Generate it via
the `--json` option shown above.
