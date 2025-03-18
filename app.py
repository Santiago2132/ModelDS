from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def extract_response(text):
    """Elimina la etiqueta <think> y devuelve solo la respuesta."""
    response = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return response if response else "Error en emisión de datos"

def run_ollama(prompt):
    """Ejecuta el modelo Ollama con el prompt dado."""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:1b', prompt],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            return {"error": "Error al ejecutar el modelo", "details": result.stderr}, 500

        return {"response": extract_response(result.stdout)}

    except FileNotFoundError:
        return {"error": "Ollama no está instalado o no está en el PATH"}, 500
    except subprocess.TimeoutExpired:
        return {"error": "El modelo tardó demasiado en responder"}, 504
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}, 500

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

    prompt = f"Pregunta del usuario, responde todo en español y con coherencia: {query}"
    response = run_ollama(prompt)

    return jsonify(response)

@app.route('/enhance_response', methods=['POST'])
def enhance_response():
    """Mejora la respuesta de la IA basada en la emoción detectada."""
    data = request.json
    mensaje_usuario = data.get('mensaje_usuario', '').strip()
    mensaje_ia = data.get('mensaje_ia', '').strip()
    emotion_detectada = data.get('emotion_detectada', '').strip()

    if not mensaje_usuario or not mensaje_ia or not emotion_detectada:
        return jsonify({"error": "Faltan parámetros"}), 400

    prompt = (
        f"Mejora la respuesta de la IA considerando la emoción detectada. "
        f"Usuario: {mensaje_usuario} "
        f"Respuesta IA: {mensaje_ia} "
        f"Emoción detectada: {emotion_detectada}. "
        f"Responde solo con un párrafo corto."
    )

    response = run_ollama(prompt)
    return jsonify(response)

@app.route('/short_response', methods=['POST'])
def short_response():
    """Genera una respuesta mejorada solo con el mensaje del usuario y la IA."""
    data = request.json
    mensaje_usuario = data.get('mensaje_usuario', '').strip()
    mensaje_ia = data.get('mensaje_ia', '').strip()

    if not mensaje_usuario or not mensaje_ia:
        return jsonify({"error": "Faltan parámetros"}), 400

    prompt = (
        f"Mejora la respuesta de la IA basada en la consulta del usuario. "
        f"Usuario: {mensaje_usuario} "
        f"Respuesta IA: {mensaje_ia}. "
        f"Responde solo con un párrafo corto."
    )

    response = run_ollama(prompt)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
