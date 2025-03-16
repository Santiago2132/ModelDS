from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import re
from text_cleaner import clean_text  # Importar la función de limpieza de texto

app = Flask(__name__, static_url_path='/static')
CORS(app)  # Habilitar CORS para toda la aplicación

def parse_response(text):
    # Expresión regular para capturar el contenido dentro de <think>...</think>
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else "Sin información de pensamiento"

    # Eliminar la etiqueta <think> y su contenido del texto original
    response_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    return {"think": think_content, "response": response_text or "Sin respuesta"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_model():
    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"error": "La consulta no puede estar vacía."}), 400

    # Limpiar la consulta para eliminar palabras en otros idiomas
    cleaned_query = clean_text(query)

    try:
        result = subprocess.run(['ollama', 'run', 'deepseek-1.5b', cleaned_query], capture_output=True, text=True, timeout=10)
        parsed_result = parse_response(result.stdout)
    except subprocess.TimeoutExpired:
        return jsonify({"error": "El modelo tardó demasiado en responder."}), 500
    except Exception as e:
        return jsonify({"error": f"Error en la ejecución: {str(e)}"}), 500

    return jsonify(parsed_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
