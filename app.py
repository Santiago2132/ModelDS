from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import re
import os

app = Flask(__name__)
CORS(app, resources={r"/query": {"origins": "*"}})

def parse_response(text):
    """Extrae la respuesta y el contenido <think> del texto."""
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else ""
    response_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return {"think": think_content, "response": response_text}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_model():
    """Procesa la consulta y ejecuta el modelo."""
    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"error": "Consulta vacía"}), 400
    query = f"Pregunta del usuario, responde todo en español, se coherente: {query}"

    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:1b', query],
            capture_output=True, text=True, timeout=10000000000000000000000000000
        )

        if result.returncode != 0:
            return jsonify({"error": "Error al ejecutar el modelo", "details": result.stderr}), 500

        parsed_result = parse_response(result.stdout)
        return jsonify(parsed_result)
    except FileNotFoundError:
        return jsonify({"error": "Ollama no está instalado o no está en el PATH"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "El modelo tardó demasiado en responder"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)
