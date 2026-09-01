from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Your total monthly baseline income
    monthly_income = 12319

    # Budget categories configured with your specific targets
    budget_data = [
        {
            "id": "housing",
            "title": "Housing & Utilities",
            "color": "#1a73e8", 
            "items": [
                {"id": "mortgage", "label": "Mortgage", "value": 1267, "max": 2500},
                {"id": "utilities", "label": "Electric & Water", "value": 750, "max": 1500},
                {"id": "comms", "label": "Phone & Internet", "value": 408, "max": 800},
                {"id": "insurance", "label": "Home/Auto Insurance", "value": 347, "max": 800},
                {"id": "life_ins", "label": "Life Insurance (x2)", "value": 106, "max": 300},
            ]
        },
        {
            "id": "family",
            "title": "Family Obligations",
            "color": "#9c27b0",
            "items": [
                {"id": "college", "label": "Hannah's College Transfer", "value": 900, "max": 2000},
            ]
        },
        {
            "id": "debt",
            "title": "Debt Minimums",
            "color": "#d93025", 
            "items": [
                {"id": "auto", "label": "Auto Loans", "value": 1419, "max": 2500},
                {"id": "bnpl", "label": "Affirm, Microf & Upstart", "value": 1233, "max": 2500},
                {"id": "cc", "label": "Credit Cards", "value": 392, "max": 1000},
                {"id": "regional", "label": "Regional Finance", "value": 299, "max": 800},
                {"id": "spectrum", "label": "Spectrum Payoff", "value": 218, "max": 500},
            ]
        },
        {
            "id": "living",
            "title": "Daily Living (Strict Cap)",
            "color": "#34a853", 
            "items": [
                {"id": "groceries", "label": "Groceries", "value": 600, "max": 1500},
                {"id": "misc", "label": "Household & Misc Shopping", "value": 350, "max": 1000},
                {"id": "dining", "label": "Dining Out & Coffee", "value": 300, "max": 1000},
                {"id": "gas", "label": "Gas & Auto Fuel", "value": 250, "max": 800},
            ]
        },
        {
            "id": "subs",
            "title": "Subscriptions & Cloud",
            "color": "#f29900", 
            "items": [
                {"id": "hulu", "label": "Hulu", "value": 100, "max": 200},
                {"id": "streaming", "label": "Netflix, HBO, Peacock, MGM, Para", "value": 86, "max": 200},
                {"id": "other", "label": "Amazon, Dr. Squatch, Google Cloud", "value": 87, "max": 200},
            ]
        }
    ]

    return render_template('index.html', income=monthly_income, budget_data=budget_data)

if __name__ == '__main__':
    # Running on 0.0.0.0 allows you to access it across your local network
    app.run(host='0.0.0.0', port=5000, debug=True)