import yfinance as yf
import openai
import os
import json
import re
import boto3
import csv
from io import StringIO

# Setup clients
ses = boto3.client('ses', region_name='us-east-1')
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def load_sp500_csv(event):
    if "sp500_data" in event:
        # Convert list of dicts to simple list format
        return event["sp500_data"]
    raise ValueError("Missing 'sp500_data' in event.")

def get_stock_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "Revenue Growth": info.get("revenueGrowth"),
            "EPS": info.get("trailingEps"),
            "Net Profit Margin": info.get("netMargins"),
            "Operating Margin": info.get("operatingMargins"),
            "Return on Equity": info.get("returnOnEquity"),
            "Earnings Growth Rate": info.get("earningsQuarterlyGrowth"),
            "Free Cash Flow": info.get("freeCashflow"),
            "Operating Cash Flow": info.get("operatingCashflow"),
            "Debt-to-Equity Ratio": info.get("debtToEquity"),
            "Current Ratio": info.get("currentRatio"),
            "P/E Ratio": info.get("trailingPE"),
            "PEG Ratio": info.get("pegRatio"),
            "P/B Ratio": info.get("priceToBook"),
            "Dividend Yield": info.get("dividendYield")
        }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def format_fundamentals(symbol, data):
    if not data:
        return f"{symbol}: No data available\n"
    formatted = f"{symbol}:\n"
    for key, value in data.items():
        formatted += f"  {key}: {value}\n"
    return formatted

def generate_analysis(fundamentals_block):
    prompt = f"""
You are a financial analyst assistant. Based on the following stock data, evaluate each stock using the 15 fundamental indicators provided. For each stock, assign a "BuyScore" from 1-10 (where 10 is the strongest buy) and provide 2-3 key "ReasonsToBuy" as an array.

Return your analysis as a JSON object with this exact structure:
{{
  "SYMBOL1": {{"BuyScore": X, "ReasonsToBuy": ["reason1", "reason2"]}},
  "SYMBOL2": {{"BuyScore": Y, "ReasonsToBuy": ["reason1", "reason2"]}}
}}

{fundamentals_block}

Return only the JSON object.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

def clean_and_load_json(response_text):
    try:
        match = re.search(r'\{[\s\S]+\}', response_text)
        if match:
            return json.loads(match.group(0))
        else:
            return {}
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        return {}

def send_email_with_csv(csv_content, subject, recipient):
    response = ses.send_raw_email(
        Source=recipient,
        Destinations=[recipient],
        RawMessage={
            'Data': f"""From: {recipient}
To: {recipient}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="NextPart"

--NextPart
Content-Type: text/plain

Attached are the top 25 stocks based on GPT-4 Buy Score (P/E > 0).

--NextPart
Content-Type: text/csv
Content-Disposition: attachment; filename="top_25_stocks.csv"

{csv_content}

--NextPart--
"""
        }
    )
    return response

def lambda_handler(event, context):
    try:
        sp500_data = load_sp500_csv(event)
        batch_size = 20
        total_stocks = len(sp500_data)
        all_results = []
        industry_map = {}

        for i in range(0, total_stocks, batch_size):
            batch = sp500_data[i:i+batch_size]
            fundamentals_text = ""
            symbols = {}
            fundamentals_data = {}

            for row in batch:
                symbol = row["Symbol"]
                industry = row.get("Sector", "Unknown")
                data = get_stock_fundamentals(symbol)

                # Skip if no data or P/E <= 0
                if not data or not data.get("P/E Ratio") or data["P/E Ratio"] <= 0:
                    continue

                industry_map[symbol] = industry
                fundamentals_text += format_fundamentals(symbol, data) + "\n"
                symbols[symbol] = industry
                fundamentals_data[symbol] = data

            if not symbols:
                continue  # Skip empty batches

            try:
                analysis_json = generate_analysis(fundamentals_text)
                batch_results = clean_and_load_json(analysis_json)
                for symbol in symbols:
                    if symbol in batch_results:
                        all_results.append({
                            "Symbol": symbol,
                            "Industry": industry_map[symbol],
                            "BuyScore": batch_results[symbol].get("BuyScore", 0),
                            "ReasonsToBuy": "; ".join(batch_results[symbol].get("ReasonsToBuy", []))
                        })
            except Exception as e:
                print(f"Error in batch {i//batch_size + 1}: {e}")

        # Sort and select top 25 using built-in sorting
        all_results.sort(key=lambda x: x["BuyScore"], reverse=True)
        top_25 = all_results[:25]

        # Convert to CSV string manually
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=["Symbol", "Industry", "BuyScore", "ReasonsToBuy"])
        writer.writeheader()
        writer.writerows(top_25)
        csv_str = csv_buffer.getvalue()

        # Email the results
        email_recipient = os.environ.get("EMAIL_RECIPIENT")
        if not email_recipient:
            raise ValueError("EMAIL_RECIPIENT environment variable is required")
        send_email_with_csv(csv_str, "Top 25 Stock Buy Picks (P/E > 0)", email_recipient)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Top 25 filtered by P/E > 0 emailed."})
        }

    except Exception as e:
        print(f"Lambda function failed: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }