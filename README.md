# ✈️ Airnoise Flight Data Extraction Agent

## 📌 Project Overview
This project is an automated, CLI-driven data extraction pipeline built in Python. It connects to the Gmail API to fetch daily noise complaint digests from **Airnoise.io**, parses the raw text of the emails (which contain malformed HTML), and outputs thousands of individual flight events (including altitude, aircraft type, callsign, and distance) into a clean `.csv` file.

This tool was built to empower residents living near **JFK International Airport** to gather hard, undeniable data regarding aircraft operations over their properties. The generated data is used as empirical evidence for formal complaints filed with the FAA, the Port Authority of NY & NJ (PANYNJ), and local elected officials.

## 🛠️ Tech Stack & Skills Demonstrated
*   **Language:** Python 3
*   **APIs & Authentication:** Google Cloud Console, Gmail API, OAuth 2.0 (`google-auth-oauthlib`)
*   **Data Parsing:** Advanced Regular Expressions (`re`), String Manipulation
*   **Automation:** Mac `cron` scheduler for daily automated execution
*   **Data Storage:** CSV generation (`csv` module)
*   **Version Control & Environment:** Git, GitHub CLI, `venv` (Virtual Environments)

## 🚀 The Engineering Challenge (The "Aha!" Moment)
The most significant technical hurdle was that the Airnoise email payloads contained malformed HTML tags embedded as literal plain text. Standard parsers like `BeautifulSoup` and `pandas.read_html` completely failed to find the flight tables because the HTML lacked proper closing tags (e.g., `<th>` instead of `<th>...</th>`).

**The Solution:** I bypassed standard HTML parsers and wrote a custom **Regular Expression parser** that scans the raw email body for `<tr>` and `<td>` tags. It strips away the raw HTML formatting, identifies rows with 8+ columns, and extracts the data into a structured format. 

## ⚙️ How It Works
1. **Authentication:** The script uses OAuth 2.0 to authenticate with the user's Gmail account.
2. **Fetching:** It queries the Gmail API for the last 7 days of emails from `no-reply@airnoise.io`.
3. **Parsing:** It extracts the `text/plain` payload and uses Regex to pull out the flight table data.
4. **Output:** It cleans the data and appends it to `airnoise_flights.csv`.
5. **Automation:** A `cron` job runs the script automatically at 6:00 AM every day.

## 📂 Project Structure
```text
airnoise-agent/
├── .gitignore          # Excludes sensitive credentials and virtual environment
├── README.md           # Project documentation
├── airnoise_agent.py   # Main Python execution script
├── credentials.json    # (Hidden) Google Cloud OAuth 2.0 client secrets
├── token.json          # (Hidden) Auto-generated access/refresh tokens
└── airnoise_flights.csv# Generated data file containing flight events