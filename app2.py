from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

# Plantilla HTML mejorada con CSS responsivo y loading indicator
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consulta Simple</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            width: 100%;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            font-size: 2.2rem;
        }
        textarea {
            width: 100%;
            min-height: 150px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            resize: vertical;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #4CAF50;
        }
        button {
            display: block;
            width: 200px;
            margin: 20px auto;
            padding: 12px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
        }
        button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        #response {
            margin-top: 20px;
            padding: 20px;
            border: 2px solid #eee;
            border-radius: 10px;
            background: #f9f9f9;
            white-space: pre-wrap;
            text-align: left;
            font-size: 1rem;
            line-height: 1.5;
        }
        .loader {
            display: none;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            h1 {
                font-size: 1.8rem;
            }
            textarea {
                min-height: 120px;
            }
            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Envía tu mensaje</h1>
        <form id="queryForm" method="POST">
            <textarea name="query" placeholder="Escribe tu consulta aquí..." required></textarea>
            <button type="submit" id="submitBtn">Enviar</button>
        </form>
        <div class="loader" id="loader"></div>
        <div id="response">{{ response|safe }}</div>
    </div>
    <script>
        document.getElementById('queryForm').addEventListener('submit', function() {
            const submitBtn = document.getElementById('submitBtn');
            const loader = document.getElementById('loader');
            submitBtn.disabled = true;
            loader.style.display = 'block';
            setTimeout(() => {
                submitBtn.disabled = false;
                loader.style.display = 'none';
            }, 10000); // Fallback para ocultar loader después de 10s
        });
    </script>
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
                    ['ollama', 'run', 'llama3.2:1b', f"Responde en español: {query}"],
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
            ['ollama', 'run', 'qwen2.5vl', f"Responde en español: {query}"],
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
    app.run(host='0.0.0.0', port=5000, debug=True)