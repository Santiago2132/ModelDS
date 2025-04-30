from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

# Plantilla HTML corregida y completa
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
            try:
                # Ejecuta el modelo con ollama
                result = subprocess.run(
                    ['ollama', 'run', 'llama3.2:1b', f"te llamas Freud1.1: {query}"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    response = result.stdout
                else:
                    response = f"Error al procesar: {result.stderr}"
            except FileNotFoundError:
                response = "Error: Ollama no está instalado o no está en el PATH."
            except Exception as e:
                response = f"Error inesperado: {str(e)}"
    
    return render_template_string(HTML_TEMPLATE, response=response)
@app.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.json
    query = data.get("query", "").strip()
    
    if not query:
        return {"error": "Consulta vacía"}, 400
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:1b', f"Responde en español y aconsjea emocionalmente: {query}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return {"response": result.stdout}
        else:
            return {"error": f"Error al procesar: {result.stderr}"}, 500
    except FileNotFoundError:
        return {"error": "Ollama no está instalado o no está en el PATH."}, 500
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
