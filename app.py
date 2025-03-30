from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
from duckduckgo_search import DDGS

app = Flask(__name__)
CORS(app, resources={r"/query": {"origins": "*"}})

def parse_response(text):
    """Extrae la respuesta y el contenido <think> del texto."""
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else ""
    response_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return {"think": think_content, "response": response_text}

def perform_web_search(query, max_results=5):
    """Realiza una búsqueda web y devuelve resultados formateados."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        search_results = "\n".join(
            f"{r['title']} - {r['body']} (URL: {r['href']})" for r in results
        )
        return search_results if search_results else "No se encontraron resultados en la búsqueda web."
    except Exception as e:
        return f"Error en la búsqueda web: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_model():
    """Procesa la consulta y ejecuta el modelo con búsqueda web."""
    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"error": "Consulta vacía"}), 400

    # Realiza una búsqueda web para enriquecer el contexto
    search_results = perform_web_search(query)

    # Construye el prompt con la consulta y los resultados de búsqueda
    prompt = (
        f"Pregunta del usuario, responde todo en español, sé coherente: {query}\n\n"
        f"Resultados de búsqueda web:\n{search_results}\n\n"
        "Por favor, utiliza esta información para responder la consulta del usuario. "
        "Asegúrate de citar cualquier fuente que uses de los resultados de búsqueda en tu respuesta."
    )

    try:
        # Solicitud a la API de Ollama (sin timeout estricto, espera prolongada)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60  # Tiempo de espera largo pero razonable
        )

        # Verifica si la solicitud fue exitosa
        if response.status_code != 200:
            return jsonify({"error": "Error al ejecutar el modelo", "details": response.text}), 500

        # Extrae la respuesta del modelo
        result = response.json().get("response", "No se recibió respuesta del modelo.")
        parsed_result = parse_response(result)
        return jsonify(parsed_result)

    except requests.ConnectionError:
        return jsonify({"error": "No se pudo conectar con el servidor de Ollama"}), 503
    except requests.Timeout:
        return jsonify({"error": "El modelo tardó demasiado en responder"}), 504
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)