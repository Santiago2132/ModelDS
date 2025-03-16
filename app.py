from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app, resources={r"/query": {"origins": "*"}})

def extract_response(text):
    """Elimina la etiqueta <think> y devuelve solo la respuesta."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_model():
    """Procesa la consulta y ejecuta el modelo."""
    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"error": "La consulta está vacía"}), 400
    
    formatted_query = f"Pregunta del usuario, responde todo en español y con coherencia: {query}"

    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:1b', formatted_query],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            return jsonify({"error": "Error al ejecutar el modelo", "details": result.stderr}), 500

        response_text = extract_response(result.stdout)
        return jsonify({"response": response_text})

    except FileNotFoundError:
        return jsonify({"error": "Ollama no está instalado o no está en el PATH"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "El modelo tardó demasiado en responder"}), 504
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
