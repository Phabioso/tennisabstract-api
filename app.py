from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def search_tennisabstract(player_name):
    query = f"site:tennisabstract.com {player_name} tennis"
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        if "tennisabstract.com/cgi-bin/" in href:
            return href
    return None

def extract_surface_stats(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    tables = soup.find_all("table")
    surface_stats = {}
    for table in tables:
        if "Surface" in table.text and "Clay" in table.text:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    surface = cells[0].get_text(strip=True)
                    winrate = cells[1].get_text(strip=True)
                    if re.match(r'\d+%$', winrate):
                        surface_stats[surface] = winrate
            break
    return surface_stats

@app.route("/playerstats")
def player_stats():
    player_name = request.args.get("name")
    if not player_name:
        return jsonify({"error": "Missing player name"}), 400
    url = search_tennisabstract(player_name)
    if not url:
        return jsonify({"error": "Player not found on TennisAbstract"}), 404
    stats = extract_surface_stats(url)
    return jsonify({
        "player": player_name,
        "url": url,
        "surface_stats": stats
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
