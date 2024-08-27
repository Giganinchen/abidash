import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

BASE_DIR = 'dateien'
OUTPUT_DIR = 'output'

# HTML-Vorlagen
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
            color: #000; /* Schwarzer Text */
            text-decoration: none; /* Kein Unterstrich */
        }}
        a:hover {{
            color: #000; /* Schwarzer Text beim Hover */
            text-decoration: none; /* Kein Unterstrich beim Hover */
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
        a {{
            color: #000; /* Schwarzer Text */
            text-decoration: none; /* Kein Unterstrich */
        }}
        a:hover {{
            color: #000; /* Schwarzer Text beim Hover */
            text-decoration: none; /* Kein Unterstrich beim Hover */
        }}
    </style>
</head>
<body>
    <h1>PDF Übersicht - {folder_name}</h1>
    <div class="pdf-container">
        {pdf_links}
    </div>
</body>
</html>'''

def generate_folder_page(folder_path, folder_name):
    """Generiert die HTML-Seite für einen bestimmten Ordner."""
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    pdf_links = '\n'.join(
        [f'<div class="pdf-box"><a href="/pdf/{folder_name}/{pdf}" target="_blank">{pdf}</a></div>' for pdf in pdf_files])

    folder_html = FOLDER_TEMPLATE.format(folder_name=folder_name, pdf_links=pdf_links)
    output_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(output_path, exist_ok=True)

    with open(os.path.join(output_path, 'index.html'), 'w') as f:
        f.write(folder_html)
    print(f"Generated page for folder: {folder_name}")

def generate_index_page(folders):
    """Generiert die Hauptindexseite."""
    folder_links = '\n'.join(
        [f'<a href="/folder/{folder}" class="folder-link">{folder}</a>' for folder in folders])

    index_html = INDEX_TEMPLATE.format(folders_links=folder_links)

    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as f:
        f.write(index_html)
    print("Generated main index page")

@app.route('/')
def index():
    """Startseite, die die Ordnerliste anzeigt."""
    folders = [name for name in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, name))]
    folder_links = '\n'.join(
        [f'<a href="/folder/{folder}" class="folder-link">{folder}</a>' for folder in folders])

    index_html = INDEX_TEMPLATE.format(folders_links=folder_links)
    return index_html

@app.route('/folder/<folder_name>')
def folder_page(folder_name):
    """Seite für einen spezifischen Ordner."""
    folder_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(folder_path):
        return "Ordner nicht gefunden", 404

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    pdf_links = '\n'.join(
        [f'<div class="pdf-box"><a href="/pdf/{folder_name}/{pdf}" target="_blank">{pdf}</a></div>' for pdf in pdf_files])

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
