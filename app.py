from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  
import subprocess
import re

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

    result = subprocess.run(['ollama', 'run', 'deepseek-r1:7b', query], capture_output=True, text=True)

    # Procesar la respuesta para separar "think" del "response"
    parsed_result = parse_response(result.stdout)

    return jsonify(parsed_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)