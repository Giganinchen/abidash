import os
import re
from datetime import datetime
from flask import Flask, send_from_directory

app = Flask(__name__)

BASE_DIR = 'dateien'
OUTPUT_DIR = 'output'

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fächerübersicht</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
        }}
        .folder-link {{
            display: block;
            margin: 10px 0;
            padding: 10px;
            background-color: #ddd;
            border-radius: 5px;
            text-decoration: none;
            color: #333;
            font-size: 18px;
        }}
        .folder-link:hover {{
            background-color: #bbb;
        }}
        a {{
            color: #000;
            text-decoration: none;
        }}
        a:hover {{
            color: #000;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <h1>Fächerübersicht</h1>
    <div id="folders-container">
        {folders_links}
    </div>
</body>
</html>'''

FOLDER_TEMPLATE = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Übersicht - {folder_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
        }}
        .pdf-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }}
        .pdf-box {{
            padding: 10px;
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
            text-align: center;
            cursor: pointer;
        }}
        .pdf-box:hover {{
            background-color: #eee;
        }}
        a {{
            color: #000;
            text-decoration: none;
        }}
        a:hover {{
            color: #000;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <h1>Übersicht - {folder_name}</h1>
    <div class="pdf-container">
        {pdf_links}
    </div>
</body>
</html>'''

def extract_date_from_filename(filename):
    """Extrahiert das Datum aus einem Dateinamen im Format (DD.MM.YYYY).pdf."""
    match = re.search(r'\((\d{2}\.\d{2}\.\d{4})\)\.pdf$', filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%d.%m.%Y')
    return None

def strip_date_from_filename(filename):
    """Entfernt das Datum und die Dateiendung aus dem Dateinamen."""
    return re.sub(r' \(\d{2}\.\d{2}\.\d{4}\)\.pdf$', '', filename)

def generate_folder_page(folder_path, folder_name):
    """Generiert die HTML-Seite für einen bestimmten Ordner, sortiert nach Datum."""
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    pdf_files_with_dates = [(pdf, extract_date_from_filename(pdf)) for pdf in pdf_files]
    pdf_files_with_dates = sorted(
        [pdf for pdf in pdf_files_with_dates if pdf[1] is not None],
        key=lambda x: x[1],
        reverse=True
    )
    
    pdf_links = '\n'.join(
        [f'<a href="/pdf/{folder_name}/{pdf[0]}" class="pdf-box" target="_blank">{strip_date_from_filename(pdf[0])}</a>' for pdf in pdf_files_with_dates]
    )

    folder_html = FOLDER_TEMPLATE.format(folder_name=folder_name, pdf_links=pdf_links)
    output_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(output_path, exist_ok=True)

    with open(os.path.join(output_path, 'index.html'), 'w') as f:
        f.write(folder_html)
    print(f"Generated page for folder: {folder_name}")

def generate_index_page(folders):
    """Generiert die Hauptindexseite."""
    folder_links = '\n'.join(
        [f'<a href="/folder/{folder}" class="folder-link">{folder}</a>' for folder in folders]
    )

    index_html = INDEX_TEMPLATE.format(folders_links=folder_links)

    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as f:
        f.write(index_html)
    print("Generated main index page")

@app.route('/')
def index():
    """Startseite, die die Ordnerliste anzeigt."""
    folders = [name for name in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, name))]
    folder_links = '\n'.join(
        [f'<a href="/folder/{folder}" class="folder-link">{folder}</a>' for folder in folders]
    )

    index_html = INDEX_TEMPLATE.format(folders_links=folder_links)
    return index_html

@app.route('/folder/<folder_name>')
def folder_page(folder_name):
    """Seite für einen spezifischen Ordner."""
    folder_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(folder_path):
        return "Ordner nicht gefunden", 404

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    pdf_files_with_dates = [(pdf, extract_date_from_filename(pdf)) for pdf in pdf_files]
    pdf_files_with_dates = sorted(
        [pdf for pdf in pdf_files_with_dates if pdf[1] is not None],
        key=lambda x: x[1],
        reverse=True
    )
    
    pdf_links = '\n'.join(
        [f'<a href="/pdf/{folder_name}/{pdf[0]}" class="pdf-box" target="_blank">{strip_date_from_filename(pdf[0])}</a>' for pdf in pdf_files_with_dates]
    )

    folder_html = FOLDER_TEMPLATE.format(folder_name=folder_name, pdf_links=pdf_links)
    return folder_html

@app.route('/pdf/<folder_name>/<pdf_name>')
def pdf_view(folder_name, pdf_name):
    """Stellt eine spezifische PDF-Datei bereit."""
    pdf_path = os.path.join(BASE_DIR, folder_name, pdf_name)
    if not os.path.exists(pdf_path):
        return "PDF nicht gefunden", 404

    return send_from_directory(os.path.join(BASE_DIR, folder_name), pdf_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
