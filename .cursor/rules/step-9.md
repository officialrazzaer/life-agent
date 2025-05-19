### Step 10: Query Interface Implementation

Create a query interface that allows you to ask natural language questions about your data:

```python
# src/interfaces/query_interface.py
from src.agent.core import PersonalAIAgent

class QueryInterface:
    def __init__(self):
        self.agent = PersonalAIAgent()

    def process_query(self, query_text: str) -> str:
        """Process a natural language query and return the response."""
        return self.agent.process_query(query_text)

    def suggest_insights(self) -> str:
        """Generate proactive insights based on recent data."""
        # This will be expanded in Phase 4
        return self.agent.process_query("What insights or patterns can you identify from my recent logs?")
```

## Phase 3: External Integration

### Step 11: Monzo API Integration

Implement the Monzo API integration to automatically fetch transaction data:

```python
# src/integrations/monzo.py
import os
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
MONZO_API_KEY = os.environ.get("MONZO_API_KEY")

class MonzoIntegration:
    def __init__(self):
        self.base_url = "https://api.monzo.com"
        self.headers = {
            "Authorization": f"Bearer {MONZO_API_KEY}"
        }

    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts associated with the authenticated user."""
        response = requests.get(f"{self.base_url}/accounts", headers=self.headers)
        response.raise_for_status()
        return response.json()["accounts"]

    def get_transactions(self, account_id: str, since: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get transactions for a specific account."""
        params = {"account_id": account_id, "limit": limit}

        if since:
            params["since"] = since.isoformat() + "Z"

        response = requests.get(f"{self.base_url}/transactions", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["transactions"]

    def process_transactions(self, account_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Process transactions from the last N days and format them for storage."""
        since_date = datetime.now() - timedelta(days=days)
        transactions = self.get_transactions(account_id, since=since_date)

        formatted_transactions = []
        for tx in transactions:
            formatted_tx = {
                "date": datetime.fromisoformat(tx["created"]).date(),
                "amount": abs(tx["amount"]) / 100,  # Convert from pence to pounds
                "currency": tx["currency"],
                "category": tx["category"],
                "description": tx["description"],
                "source": "Monzo",
                "transaction_type": "expense" if tx["amount"] < 0 else "income"
            }
            formatted_transactions.append(formatted_tx)

        return formatted_transactions
```

### Step 12: CoinGecko API Integration

Implement the CoinGecko API integration to fetch cryptocurrency prices:

```python
# src/integrations/coingecko.py
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

class CoinGeckoIntegration:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_coin_price(self, coin_id: str, vs_currency: str = "gbp") -> Optional[float]:
        """Get the current price of a cryptocurrency."""
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get(coin_id, {}).get(vs_currency)
        return None

    def get_coin_history(self, coin_id: str, date: datetime, vs_currency: str = "gbp") -> Optional[float]:
        """Get the price of a cryptocurrency on a specific date."""
        date_str = date.strftime("%d-%m-%Y")
        url = f"{self.base_url}/coins/{coin_id}/history"
        params = {
            "date": date_str,
            "localization": "false"
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("market_data", {}).get("current_price", {}).get(vs_currency)
        return None

    def search_coins(self, query: str) -> List[Dict[str, Any]]:
        """Search for coins by name or symbol."""
        url = f"{self.base_url}/search"
        params = {"query": query}

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("coins", [])
        return []
```

### Step 13: Travel API Integration (Skyscanner/Google Flights)

Implement a travel API integration to fetch flight prices and availability:

```python
# src/integrations/travel.py
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()
# You would need to sign up for a flight search API like Skyscanner, Kiwi, or use a service like RapidAPI
FLIGHT_API_KEY = os.environ.get("FLIGHT_API_KEY")

class FlightSearchIntegration:
    def __init__(self):
        self.base_url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices"
        self.headers = {
            "x-rapidapi-key": FLIGHT_API_KEY,
            "x-rapidapi-host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
        }

    def search_flights(self, origin: str, destination: str, departure_date: date, return_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Search for flights between two locations."""
        # Format dates as YYYY-MM-DD
        departure_str = departure_date.strftime("%Y-%m-%d")
        return_str = return_date.strftime("%Y-%m-%d") if return_date else ""

        # Construct the URL
        url = f"{self.base_url}/browseroutes/v1.0/UK/GBP/en-GB/{origin}/{destination}/{departure_str}"
        if return_date:
            url += f"/{return_str}"

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("Routes", [])
        return []

    def suggest_travel_dates(self, origin: str, destination: str, flexible_days: int = 3) -> List[Dict[str, Any]]:
        """Suggest optimal travel dates based on price and availability."""
        # This would be implemented to find the best travel dates within a flexible window
        pass
```

### Step 14: Tool Integration in LangChain Agent

Extend the LangChain agent to incorporate the external API integrations:

```python
# src/agent/tools.py
from typing import Dict, Any
from src.integrations.monzo import MonzoIntegration
from src.integrations.coingecko import CoinGeckoIntegration
from src.integrations.travel import FlightSearchIntegration

class ExternalAPITools:
    def __init__(self):
        self.monzo = MonzoIntegration()
        self.coingecko = CoinGeckoIntegration()
        self.flight_search = FlightSearchIntegration()

    def get_recent_transactions(self, days: int = 7) -> str:
        """Get recent financial transactions from Monzo."""
        try:
            accounts = self.monzo.get_accounts()
            if not accounts:
                return "No Monzo accounts found."

            account_id = accounts[0]["id"]  # Use the first account
            transactions = self.monzo.process_transactions(account_id, days=days)

            # Format the transactions into a readable string
            result = f"Found {len(transactions)} transactions in the last {days} days:\n\n"
            for tx in transactions:
                result += f"Date: {tx['date']}, Amount: {tx['amount']} {tx['currency']}, Description: {tx['description']}, Category: {tx['category']}\n"

            return result
        except Exception as e:
            return f"Error fetching transactions: {str(e)}"

    def get_crypto_price(self, coin_id: str) -> str:
        """Get the current price of a cryptocurrency."""
        try:
            price = self.coingecko.get_coin_price(coin_id)
            if price:
                return f"The current price of {coin_id} is £{price:,.2f}"
            else:
                return f"Could not find price information for {coin_id}"
        except Exception as e:
            return f"Error fetching crypto price: {str(e)}"

    def search_flights(self, origin: str, destination: str, departure_date: str) -> str:
        """Search for flights between two locations."""
        try:
            from datetime import datetime
            departure_date_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()

            flights = self.flight_search.search_flights(origin, destination, departure_date_obj)
            if flights:
                result = f"Found {len(flights)} flight options from {origin} to {destination} on {departure_date}:\n\n"
                for i, flight in enumerate(flights[:5], 1):  # Show top 5 results
                    result += f"{i}. Price: £{flight.get('MinPrice', 'N/A')}, Carrier: {flight.get('Carrier', 'N/A')}\n"
                return result
            else:
                return f"No flights found from {origin} to {destination} on {departure_date}"
        except Exception as e:
            return f"Error searching flights: {str(e)}"
```

Update the agent's tool setup to include these new tools:

```python
# Update the _setup_tools method in src/agent/core.py
def _setup_tools(self):
    external_api_tools = ExternalAPITools()

    tools = [
        # Existing tools

        # External API tools
        Tool(
            name="GetRecentTransactions",
            func=external_api_tools.get_recent_transactions,
            description="Get recent financial transactions from Monzo"
        ),
        Tool(
            name="GetCryptoPrice",
            func=external_api_tools.get_crypto_price,
            description="Get the current price of a cryptocurrency"
        ),
        Tool(
            name="SearchFlights",
            func=external_api_tools.search_flights,
            description="Search for flights between two locations"
        )
    ]
    return tools
```

## Phase 4: Agent Autonomy

### Step 15: Database Schema Management

Implement functionality to allow the agent to create or modify database tables:

```python
# src/db/schema_manager.py
import os
from supabase import create_client
from dotenv import load_dotenv
import openai
from typing import Dict, Any, List

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

class SchemaManager:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase = create_client(url, key)

    def generate_sql_for_new_table(self, table_description: str) -> str:
        """Generate SQL to create a new table based on a natural language description."""
        prompt = f"""
        Generate SQL code to create a new table in PostgreSQL based on this description:

        {table_description}

        The SQL should:
        1. Include appropriate column types
        2. Add a primary key (id) as UUID
        3. Add a user_id column as UUID with foreign key reference to users table
        4. Add a created_at timestamp column with default NOW()
        5. Include appropriate CHECK constraints for any rating fields (1-10 range)

        Return only the SQL code without any explanation.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a database expert that generates precise SQL code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip()

    def create_new_table(self, table_description: str) -> Dict[str, Any]:
        """Create a new table based on a natural language description."""
        sql = self.generate_sql_for_new_table(table_description)

        # Execute the SQL using Supabase's REST API
        # Note: This is a simplified version. In practice, you might need to use
        # a more direct PostgreSQL connection for schema modifications
        result = self.supabase.rpc(
            "execute_sql",
            {"sql_query": sql}
        ).execute()

        return {
            "success": True,
            "message": f"Table created successfully",
            "sql_used": sql
        }

    def modify_existing_table(self, table_name: str, modification_description: str) -> Dict[str, Any]:
        """Modify an existing table based on a natural language description."""
        # Similar implementation to create_new_table but for ALTER TABLE statements
        pass

    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        # This would query the PostgreSQL information_schema
        pass

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get the schema of a specific table."""
        # This would query the PostgreSQL information_schema
        pass
```

### Step 16: Proactive Insights Engine

Implement a proactive insights engine that can analyze your data and generate suggestions:

```python
# src/agent/insights.py
import openai
from typing import List, Dict, Any
from src.db.supabase_client import SupabaseManager
from src.nlp.embeddings import EmbeddingGenerator
from src.db.vector_store import ChromaDBManager  # or QdrantManager

class InsightsEngine:
    def __init__(self):
        self.supabase = SupabaseManager()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = ChromaDBManager()  # or QdrantManager()

    def generate_daily_insights(self, user_id: str) -> str:
        """Generate insights based on recent daily logs."""
        # Fetch recent daily logs
        recent_logs = self.supabase.select_data(
            table_name="daily_logs",
            filters={"user_id": user_id},
            # Add query parameters to limit to recent logs
        ).data

        if not recent_logs:
            return "Not enough data to generate insights."

        # Prepare the data for GPT-4
        logs_text = "\n\n".join([
            f"Date: {log['date']}\n"
            f"Mood: {log['mood_score']}/10\n"
            f"Energy: {log['energy_level']}/10\n"
            f"Stress: {log['stress_level']}/10\n"
            f"Sleep: {log['sleep_hours']} hours, Quality: {log['sleep_quality']}/10\n"
            f"Notes: {log['free_text']}"
            for log in recent_logs
        ])

        # Generate insights using GPT-4
        prompt = f"""
        Analyze these recent daily logs and provide insights about patterns, correlations, and suggestions:

        {logs_text}

        Focus on:
        1. Patterns in mood, energy, and stress levels
        2. Correlation between sleep and other metrics
        3. Any recurring themes in the free text notes
        4. Actionable suggestions based on the data

        Provide a thoughtful analysis that would be helpful for personal growth and well-being.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an insightful personal analytics assistant that identifies patterns and provides helpful suggestions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        return response.choices[0].message.content

    def generate_fitness_insights(self, user_id: str) -> str:
        """Generate insights based on gym and nutrition logs."""
        # Similar implementation to generate_daily_insights but for fitness data
        pass

    def generate_financial_insights(self, user_id: str) -> str:
        """Generate insights based on financial transactions and investments."""
        # Similar implementation to generate_daily_insights but for financial data
        pass

    def suggest_deload_week(self, user_id: str) -> Dict[str, Any]:
        """Analyze training data to suggest when a deload week might be beneficial."""
        # This would analyze gym and jiu-jitsu logs to identify signs of overtraining
        pass

    def suggest_budget_adjustments(self, user_id: str) -> Dict[str, Any]:
        """Analyze spending patterns to suggest budget adjustments."""
        # This would analyze financial transactions to identify spending patterns
        pass
```

### Step 17: Scheduled Tasks Setup

Set up scheduled tasks to regularly generate insights and send notifications:

```python
# src/scheduler/tasks.py
import schedule
import time
import threading
from datetime import datetime
from src.agent.insights import InsightsEngine
from src.interfaces.telegram_bot import send_message_to_user

class ScheduledTasks:
    def __init__(self, user_id: str, telegram_chat_id: str):
        self.user_id = user_id
        self.telegram_chat_id = telegram_chat_id
        self.insights_engine = InsightsEngine()

    def send_daily_summary(self):
        """Send a daily summary of insights to the user."""
        insights = self.insights_engine.generate_daily_insights(self.user_id)
        send_message_to_user(self.telegram_chat_id, f"📊 Daily Insights\n\n{insights}")

    def send_weekly_review(self):
        """Send a weekly review of all data to the user."""
        # Generate comprehensive weekly insights
        daily_insights = self.insights_engine.generate_daily_insights(self.user_id)
        fitness_insights = self.insights_engine.generate_fitness_insights(self.user_id)
        financial_insights = self.insights_engine.generate_financial_insights(self.user_id)

        message = f"""
        🗓️ Weekly Review ({datetime.now().strftime('%Y-%m-%d')})

        🧠 Well-being Insights:
        {daily_insights}

        💪 Fitness Insights:
        {fitness_insights}

        💰 Financial Insights:
        {financial_insights}
        """

        send_message_to_user(self.telegram_chat_id, message)

    def check_for_proactive_suggestions(self):
        """Check if there are any proactive suggestions to send to the user."""
        # Check for various conditions that might trigger suggestions
        # For example, signs of overtraining, unusual spending, etc.
        pass

    def setup_schedules(self):
        """Set up the scheduled tasks."""
        # Daily summary at 9 PM
        schedule.every().day.at("21:00").do(self.send_daily_summary)

        # Weekly review on Sunday at 10 AM
        schedule.every().sunday.at("10:00").do(self.send_weekly_review)

        # Check for proactive suggestions every 6 hours
        schedule.every(6).hours.do(self.check_for_proactive_suggestions)

    def run_scheduler(self):
        """Run the scheduler in a separate thread."""
        self.setup_schedules()

        def run_continuously():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        scheduler_thread = threading.Thread(target=run_continuously)
        scheduler_thread.daemon = True
        scheduler_thread.start()
```

## Phase 5: UI/Reporting (Optional)

### Step 18: Weekly Report Generator

Implement a weekly report generator that creates a comprehensive summary of your data:

```python
# src/reporting/weekly_report.py
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import matplotlib.pyplot as plt
import pandas as pd
from src.db.supabase_client import SupabaseManager
from src.agent.insights import InsightsEngine

class WeeklyReportGenerator:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = SupabaseManager()
        self.insights_engine = InsightsEngine()
        self.report_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(self.report_dir, exist_ok=True)

    def generate_mood_chart(self, start_date, end_date):
        """Generate a chart showing mood, energy, and stress levels over time."""
        # Fetch data
        daily_logs = self.supabase.select_data(
            table_name="daily_logs",
            filters={"user_id": self.user_id},
            # Add query parameters for date range
        ).data

        # Convert to DataFrame
        df = pd.DataFrame(daily_logs)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Create the chart
        plt.figure(figsize=(10, 6))
        plt.plot(df['date'], df['mood_score'], label='Mood', marker='o')
        plt.plot(df['date'], df['energy_level'], label='Energy', marker='s')
        plt.plot(df['date'], df['stress_level'], label='Stress', marker='^')
        plt.title('Mood, Energy, and Stress Levels')
        plt.xlabel('Date')
        plt.ylabel('Score (1-10)')
        plt.legend()
        plt.grid(True)

        # Save the chart
        chart_path = os.path.join(self.report_dir, f"mood_chart_{start_date}_{end_date}.png")
        plt.savefig(chart_path)
        plt.close()

        return chart_path

    def generate_workout_summary(self, start_date, end_date):
        """Generate a summary of workouts during the specified period."""
        # Fetch gym logs
        gym_logs = self.supabase.select_data(
            table_name="gym_logs",
            filters={"user_id": self.user_id},
            # Add query parameters for date range
        ).data

        # Process the data to create a summary
        # This would depend on the specific structure of your gym logs
        pass

    def generate_financial_summary(self, start_date, end_date):
        """Generate a summary of financial transactions during the specified period."""
        # Fetch financial transactions
        transactions = self.supabase.select_data(
            table_name="financial_transactions",
            filters={"user_id": self.user_id},
            # Add query parameters for date range
        ).data

        # Process the data to create a summary
        # This would include categorizing expenses, calculating totals, etc.
        pass

    def generate_weekly_report(self):
        """Generate a comprehensive weekly report."""
        # Define the date range for the report
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        # Generate insights
        daily_insights = self.insights_engine.generate_daily_insights(self.user_id)
        fitness_insights = self.insights_engine.generate_fitness_insights(self.user_id)
        financial_insights = self.insights_engine.generate_financial_insights(self.user_id)

        # Generate charts
        mood_chart_path = self.generate_mood_chart(start_date, end_date)

        # Generate summaries
        workout_summary = self.generate_workout_summary(start_date, end_date)
        financial_summary = self.generate_financial_summary(start_date, end_date)

        # Compile the report
        report = f"""
        # Weekly Report: {start_date} to {end_date}

        ## Well-being Insights
        {daily_insights}

        ## Fitness Insights
        {fitness_insights}
        {workout_summary}

        ## Financial Insights
        {financial_insights}
        {financial_summary}

        ## Charts and Visualizations
        ![Mood, Energy, and Stress Levels]({mood_chart_path})
        """

        # Save the report
        report_path = os.path.join(self.report_dir, f"weekly_report_{start_date}_{end_date}.md")
        with open(report_path, 'w') as f:
            f.write(report)

        return report_path
```

### Step 19: Simple Dashboard (Optional)

If you want a simple dashboard, you can create one using Flask:

```python
# src/interfaces/dashboard.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from src.db.supabase_client import SupabaseManager
from src.agent.core import PersonalAIAgent
from src.agent.insights import InsightsEngine
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
supabase = SupabaseManager()
agent = PersonalAIAgent()
insights_engine = InsightsEngine()

@app.route('/')
def index():
    """Render the dashboard homepage."""
    return render_template('index.html')

@app.route('/daily-logs')
def daily_logs():
    """Render the daily logs page."""
    # Fetch daily logs from Supabase
    logs = supabase.select_data("daily_logs").data
    return render_template('daily_logs.html', logs=logs)

@app.route('/gym-logs')
def gym_logs():
    """Render the gym logs page."""
    # Fetch gym logs from Supabase
    logs = supabase.select_data("gym_logs").data
    return render_template('gym_logs.html', logs=logs)

@app.route('/jiujitsu-logs')
def jiujitsu_logs():
    """Render the jiu-jitsu logs page."""
    # Fetch jiu-jitsu logs from Supabase
    logs = supabase.select_data("jiujitsu_logs").data
    return render_template('jiujitsu_logs.html', logs=logs)

@app.route('/nutrition-logs')
def nutrition_logs():
    """Render the nutrition logs page."""
    # Fetch nutrition logs from Supabase
    logs = supabase.select_data("nutrition_logs").data
    return render_template('nutrition_logs.html', logs=logs)

@app.route('/financial')
def financial():
    """Render the financial page."""
    # Fetch financial transactions from Supabase
    transactions = supabase.select_data("financial_transactions").data
    return render_template('financial.html', transactions=transactions)

@app.route('/investments')
def investments():
    """Render the investments page."""
    # Fetch investment logs from Supabase
    investments = supabase.select_data("investment_logs").data
    return render_template('investments.html', investments=investments)

@app.route('/insights')
def insights():
    """Render the insights page."""
    # Generate insights
    daily_insights = insights_engine.generate_daily_insights("your_user_id")
    fitness_insights = insights_engine.generate_fitness_insights("your_user_id")
    financial_insights = insights_engine.generate_financial_insights("your_user_id")

    return render_template('insights.html',
                          daily_insights=daily_insights,
                          fitness_insights=fitness_insights,
                          financial_insights=financial_insights)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    """Render the ask page where users can query the AI agent."""
    if request.method == 'POST':
        query = request.form.get('query')
        response = agent.process_query(query)
        return render_template('ask.html', query=query, response=response)
    return render_template('ask.html')

def run_dashboard():
    """Run the Flask dashboard."""
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    run_dashboard()
```

Create the necessary HTML templates for the dashboard in a `templates` directory.

## Deployment and Maintenance

### Step 20: Deployment Setup

Set up a deployment environment for your personal AI system:

1. **Server Setup**:

   - Use a VPS provider like DigitalOcean, Linode, or AWS EC2
   - Set up a Ubuntu 20.04 server with at least 2GB RAM
   - Install Docker and Docker Compose for containerization

2. **Docker Compose Configuration**:
   Create a `docker-compose.yml` file:

```yaml
version: "3"

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=your_username
      - N8N_BASIC_AUTH_PASSWORD=your_password
    volumes:
      - n8n_data:/home/node/.n8n

  vector-db:
    image: qdrant/qdrant
    restart: always
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  python-agent:
    build: ./agent
    restart: always
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./agent:/app

volumes:
  n8n_data:
  qdrant_data:
```

3. **Environment Variables**:
   Create a `.env` file with all your API keys and credentials.

4. **Deployment Script**:
   Create a deployment script:

```bash
#!/bin/bash

# Pull latest changes
git pull

# Build and start containers
docker-compose up -d --build

# Run database migrations if needed
# ...

echo "Deployment completed successfully!"
```

### Step 21: Backup and Maintenance

Set up regular backups and maintenance procedures:

1. **Database Backups**:
   Create a script to backup your Supabase database:

```bash
#!/bin/bash

# Set variables
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/path/to/backups"
SUPABASE_PROJECT_ID="your_project_id"
SUPABASE_API_KEY="your_api_key"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup Supabase database
curl -X POST "https://api.supabase.io/v1/projects/$SUPABASE_PROJECT_ID/database/backup" \
  -H "Authorization: Bearer $SUPABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -o "$BACKUP_DIR/supabase_backup_$DATE.sql"

# Backup vector database
# This would depend on which vector database you're using

echo "Backup completed successfully!"
```

2. **Monitoring**:
   Set up monitoring to ensure your system is running smoothly:

```bash
#!/bin/bash

# Check if n8n is running
n8n_status=$(docker ps | grep n8n | wc -l)
if [ $n8n_status -eq 0 ]; then
  echo "n8n is not running! Restarting..."
  docker-compose restart n8n
fi

# Check if vector database is running
vector_db_status=$(docker ps | grep vector-db | wc -l)
if [ $vector_db_status -eq 0 ]; then
  echo "Vector database is not running! Restarting..."
  docker-compose restart vector-db
fi

# Check if Python agent is running
python_agent_status=$(docker ps | grep python-agent | wc -l)
if [ $python_agent_status -eq 0 ]; then
  echo "Python agent is not running! Restarting..."
  docker-compose restart python-agent
fi

echo "Monitoring check completed successfully!"
```

3. **Log Rotation**:
   Set up log rotation to prevent logs from consuming too much disk space:

```bash
#!/bin/bash

# Set variables
LOG_DIR="/path/to/logs"
MAX_LOG_SIZE="100M"
MAX_LOG_FILES=10

# Configure logrotate
cat > /etc/logrotate.d/personal-ai-system << EOF
$LOG_DIR/*.log {
  size $MAX_LOG_SIZE
  rotate $MAX_LOG_FILES
  compress
  delaycompress
  missingok
  notifempty
  create 0640 root root
}
EOF

echo "Log rotation configured successfully!"
```

## Conclusion

This comprehensive step-by-step plan outlines the development of your personal AI system across five progressive phases. By following this plan, you'll build a robust system that can:

1. Ingest and process data from various aspects of your life
2. Store structured data in Supabase and semantic data in a vector database
3. Use GPT-4 to extract structured data from natural language inputs
4. Provide insights and correlations across different data domains
5. Access external APIs for financial, cryptocurrency, and travel data
6. Autonomously manage database schema and generate proactive suggestions
7. Create reports and visualizations to help you understand your data

The system is designed to be modular and scalable, allowing you to start with the core functionality and gradually add more features as needed. The use of modern tools like LangChain, Supabase, and n8n ensures that the system is built on solid foundations and can be extended in the future.

Remember to prioritize data security and privacy throughout the development process, especially when dealing with sensitive personal information. Regularly backup your data and monitor the system to ensure it's running smoothly.

With this personal AI system, you'll have a powerful tool to help you track, analyze, and optimize various aspects of your life, leading to better decision-making and personal growth.
