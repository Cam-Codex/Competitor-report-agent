# Competitor Report Agent

This project tracks daily announcements from analytics vendors (Microsoft, Salesforce/Tableau, Snowflake, Databricks, Sigma, etc.) and general industry news. A Python script gathers RSS articles and produces:

- **`public/index.html`** – a simple HTML report
- **`frontend/public/articles.json`** – structured data used by a React app
- **Optional email digest** summarising the links

The React app groups articles by vendor or industry and lets you search the summaries and heuristic "potential drawbacks" for each item. Styling aims to resemble a simple enterprise portal.

---

## 1. Prerequisites

1. Install [Python 3](https://www.python.org/downloads/). On Windows tick "Add Python to PATH".
2. Install [Node.js](https://nodejs.org/) (includes `npm`).

---

## 2. Get the project

Open a terminal and run:

```bash
git clone https://github.com/Cam-Codex/Competitor-report-agent.git
cd Competitor-report-agent
```

If you downloaded a ZIP instead, unzip it and open a terminal in the folder.

---

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

*(Optional but recommended)* create a virtual environment first:

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

---

## 4. Install React dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 5. Generate today's articles

Run the news agent to fetch feeds, build the HTML report and create the JSON file for the React app:

```bash
python news_agent.py --config feeds.yaml --output public/index.html --json frontend/public/articles.json
```

You can open `public/index.html` directly in a browser to see the full list of links. The JSON file powers the React frontend (`frontend/public/articles.json`).

---

## 6. Start the React app

```bash
cd frontend
npm run dev
```

`npm` prints a local URL (usually `http://localhost:5173`). Open that in your browser to browse articles grouped by vendor (e.g., Microsoft with Power BI news, Salesforce focusing on Tableau and Agentforce) or industry, search them, and view potential drawbacks.

---

## 7. (Optional) Send the TLDR email digest

Set these environment variables before running the script:

```
SMTP_HOST   – your mail server
SMTP_PORT   – server port (587 is common)
SMTP_USER   – username (often your email address)
SMTP_PASS   – password or app-specific password
EMAIL_FROM  – sender address
EMAIL_TO    – comma-separated recipient list
```

Example on macOS/Linux:

```bash
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="you@example.com"
export SMTP_PASS="your_password"
export EMAIL_FROM="you@example.com"
export EMAIL_TO="you@example.com"      # send to yourself
python news_agent.py --send-email
```

On Windows PowerShell use `$env:VARIABLE="value"` instead of `export`.

---

## 8. Automate daily runs

Schedule the command from step 5 (and optionally the email command) using a task scheduler:

- **macOS/Linux:** `crontab -e`
- **Windows:** Task Scheduler

Run it once a day to keep the report and React app data up to date. The TLDR email now includes brief summaries and potential drawbacks with clean plain text.

---

Feel free to customise `feeds.yaml` with additional competitors or industry sources.
