from flask import Flask, request, render_template_string, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consulta Simple</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; text-align: center; }
        textarea { width: 80%; height: 100px; margin: 10px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
        #response { margin-top: 20px; padding: 10px; border: 1px solid #ccc; white-space: pre-wrap; text-align: left; max-width: 80%; margin: auto; }
    </style>
</head>
<body>
    <h1>Envía tu mensaje</h1>
    <form method="POST">
        <textarea name="query" placeholder="Escribe tu consulta aquí..." required></textarea><br>
        <button type="submit">Enviar</button>
    </form>
    <div id="response">{{ response|safe }}</div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    response = ""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            response = run_ollama_prompt(query)
    return render_template_string(HTML_TEMPLATE, response=response)

@app.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()
    print(f"Consulta recibida por API: {query}")  # Log para depuración

    if not query:
        return jsonify({"error": "Consulta vacía"}), 400

    response = run_ollama_prompt(query)
    if response.startswith("Error"):
        return jsonify({"error": response}), 500
    return jsonify({"response": response})

def run_ollama_prompt(query: str) -> str:
    try:
        prompt = f"""
Responde en español como un terapeuta emocional profesional y empático.
Ofrece orientación emocional basada en el mensaje siguiente:

\"{query}\"
"""
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:1b'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=90  # Más tiempo de ejecución
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error al procesar: {result.stderr.strip()}"
    except FileNotFoundError:
        return "Error: Ollama no está instalado o no está en el PATH."
    except subprocess.TimeoutExpired:
        return "Error: Tiempo de ejecución excedido al intentar obtener respuesta del modelo."
    except Exception as e:
        return f"Error inesperado: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
