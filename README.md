# Created by Bryan Sailer
# Created on 2026-09-04

# Zero-Based Budget Dashboard

## The Philosophy
Zero-based budgeting is the practice of assigning every single dollar of your income a specific job before the month begins. The goal is to subtract your expenses, debt payments, and investments from your total income until your surplus equals exactly zero. 

This application replaces messy spreadsheets with a visual, interactive command center that enforces this discipline. It bridges the gap between *planning* your budget and actually *executing* it on a daily basis.

## How It Works
The application is split into three core workflows:

1. **The Planner (Dashboard):** Use interactive sliders to model your month. As you adjust your expected income, savings goals, and spending limits, the dashboard calculates your available surplus in real-time. If you over-allocate, your surplus turns red, warning you to pull back.
2. **The Tracker:** A daily logging tool where you enter your actual transactions. The tracker pulls your planned limits directly from the dashboard and displays them next to your actual spending. If you budget $600 for groceries and spend $615, the tracker instantly snaps to red.
3. **The Configuration Engine:** A backend settings menu that allows you to add, edit, or remove income sources and expense categories on the fly. You can easily adapt the tool as debts are paid off or income changes, without ever touching the underlying code.

## Key Features
* **Smart Income Calculation:** Automatically deducts your monthly investments from your top-line income to show your *true* available cash. Supports automatic bi-weekly paycheck math (multiplying by 26/12) for accurate monthly forecasting.
* **Live Guardrails:** Transaction totals are color-coded against your custom targets, providing instant psychological feedback on your spending velocity.
* **Month-End Archival:** A single-click "Close Month" function sums up your monthly performance, saves a permanent snapshot to a historical database table, and wipes the active tracker clean for the new month.
* **Fully Dynamic Interface:** Driven by a lightweight SQLite backend. Adding a new debt minimum or subscription creates a new slider and adjusts your math instantly.
* **Self-Hosted & Private:** Your financial data never leaves your network. 

## Quick Start (Docker)
The easiest and recommended way to deploy the application is using Docker. The included `docker-compose.yml` file maps a persistent volume so your database safely survives container updates.

1. Clone this repository to your local machine or server.
2. Navigate to the project directory and run:
   bash
   docker compose up -d



3. Open your web browser and navigate to `http://localhost:5001`. The application will automatically generate a clean SQLite database in the `/data` folder on first boot.

## Manual Installation

If you prefer to run the application directly on your machine without Docker:

1. Clone the repository and navigate to the project folder.
2. Create a virtual environment and install the required dependencies:
bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt




3. Launch the Flask server:
bash
python app.py


4. Navigate to `http://localhost:5001`.

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

You are free to use, modify, and distribute this software. However, any derivative works or modifications must also be open-source and distributed under the same GPL-3.0 license. See the `LICENSE` file in this repository for full text and details.

