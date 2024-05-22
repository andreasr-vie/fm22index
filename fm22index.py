from flask import Flask, jsonify
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

def compute_fm_index():
    # URL der Seite
    url = "https://www.wienenergie.at/indexwerte"

    # HTML-Inhalt der Seite herunterladen
    response = requests.get(url)
    html_content = response.text

    # Use regular expressions to find the line containing 'var data ='
    table_regex = re.compile(r'<table>[\s\S]*?<\\/table>', re.DOTALL)

    # Suche nach dem Inhalt innerhalb der <table> Tags
    tables = table_regex.findall(html_content)

    tables_str = ' '.join(tables)

    tables_str = tables_str.replace('\\/', '/')
    tables_str = tables_str.replace('=\\', '=')
    tables_str = tables_str.replace('\\"', '"')
    tables_str = tables_str.replace('\\u00e4', 'ä')
    tables_str = tables_str.replace('\\u00f6', 'ö')
    tables_str = tables_str.replace('\\u00fc', 'ü')
    tables_str = tables_str.replace('\\u00c4', 'Ä')
    tables_str = tables_str.replace('\\u00d6', 'Ö')
    tables_str = tables_str.replace('\\u00dc', 'Ü')
    tables_str = tables_str.replace('\\u00df', 'ß')

    soup = BeautifulSoup(tables_str, 'html.parser')

    # Alle Monate und FM 22 Index Werte extrahieren
    rows = soup.find_all('tr')[1:]  # Erste Zeile überspringen (Header)

    # Überprüfen, ob Zeilen gefunden wurden
    if not rows:
        raise ValueError("Keine Zeilen im HTML-Output gefunden")

    for row in rows:
        columns = row.find_all('td')
        if len(columns) < 4:
            raise ValueError(f"Unerwartetes Format in Zeile: {row}")
        fm_index = columns[3].text.strip().replace('<strong>', '').replace('</strong>', '')
        fm_index = fm_index.replace(',', '.')  # Komma durch Punkt ersetzen
        return fm_index
        break

@app.route('/fm_index', methods=['GET'])
def get_fm_index():
    try:
        fm_index = compute_fm_index()
        return jsonify({'fm_index': fm_index})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5001)
