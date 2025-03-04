from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import re
from text_cleaner import clean_text  # Importar la función de limpieza de texto

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

def parse_response(text):
    # Expresión regular para capturar el contenido dentro de <think>...</think>
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else ""

    # Eliminar la etiqueta <think> y su contenido del texto original
    response_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    return {"think": think_content, "response": response_text}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_model():
    data = request.json
    query = data.get('query')

    # Limpiar la consulta para eliminar palabras en otros idiomas
    cleaned_query = clean_text(query)

    result = subprocess.run(['ollama', 'run', 'deepseek-1.5b', cleaned_query], capture_output=True, text=True)

    # Procesar la respuesta para separar "think" del "response"
    parsed_result = parse_response(result.stdout)

    return jsonify(parsed_result)

if __name__ == '__main__':
    # Especificar una IP específica para mayor seguridad
    app.run(host='192.168.1.100', port=4000)