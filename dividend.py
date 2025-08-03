import requests
from bs4 import BeautifulSoup

def get_top_dividend_stocks(limit=5):
    url = "https://www.screener.in/screens/3/highest-dividend-yield-shares/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(" Error fetching dividends:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", class_="data-table")
    if not table:
        print(" No table found.")
        return []

    rows = table.find("tbody").find_all("tr")
    top_stocks = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 7:
            continue

        # Column 1 is serial number, Column 2 has <a> with company name and link
        link = cols[1].find("a")
        if not link:
            continue

        name = link.text.strip()  # Company name
        url = link.get("href", "")
        symbol = url.strip("/").split("/")[-1].upper()  # Approximate symbol

        dividend_yield = cols[6].text.strip()

        top_stocks.append({
            "symbol": symbol,
            "description": name,
            "dividendYield": dividend_yield
        })

        if len(top_stocks) >= limit:
            break

    return top_stocks

def get_best_dividend_stock():
    stocks = get_top_dividend_stocks(limit=1)
    return stocks[0] if stocks else None

# For testing
if __name__ == "__main__":
    print(get_top_dividend_stocks(5))
    print(get_best_dividend_stock())
