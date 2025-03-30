from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import re
import os
import atexit
from threading import Lock
import time

app = Flask(__name__)
CORS(app)  # Habilitamos CORS para todas las rutas

# Variables globales para el estado del modelo
model_ready = False
model_lock = Lock()
model_loading = False

def load_model():
    """Carga el modelo al iniciar la aplicación"""
    global model_ready, model_loading
    
    with model_lock:
        if model_ready or model_loading:
            return
            
        model_loading = True
        print("⏳ Cargando modelo llama3.2:1b...")
        
        try:
            # Comando para precargar el modelo
            startup_check = subprocess.run(
                ['ollama', 'run', 'llama3.2:1b', 'Hola'],
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if startup_check.returncode == 0:
                model_ready = True
                print("✅ Modelo cargado correctamente")
            else:
                print(f"❌ Error al cargar modelo: {startup_check.stderr}")
                
        except Exception as e:
            print(f"⚠️ Excepción al cargar modelo: {str(e)}")
        finally:
            model_loading = False

def ensure_model_ready():
    """Espera hasta que el modelo esté listo"""
    global model_ready
    
    if model_ready:
        return True
        
    with model_lock:
        if not model_ready and not model_loading:
            load_model()
    
    # Espera activa con timeout
    timeout = 30  # segundos
    start_time = time.time()
    
    while not model_ready and (time.time() - start_time) < timeout:
        time.sleep(0.5)
    
    return model_ready

def parse_response(text):
    """Versión optimizada del parser de respuesta"""
    think_content = ""
    response_text = text
    
    # Extrae contenido <think> si existe
    think_start = text.find("<think>")
    think_end = text.find("</think>")
    
    if think_start != -1 and think_end != -1:
        think_content = text[think_start+7:think_end].strip()
        response_text = (text[:think_start] + text[think_end+8:]).strip()
    
    return {
        "think": think_content,
        "response": response_text or "No se recibió respuesta",
        "timestamp": time.time()
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    """Endpoint para verificar el estado del modelo"""
    return jsonify({
        "model_ready": model_ready,
        "status": "ready" if model_ready else "loading"
    })

@app.route('/query', methods=['POST'])
def query_model():
    """Endpoint optimizado para consultas"""
    if not ensure_model_ready():
        return jsonify({"error": "Modelo no disponible", "details": "El modelo no pudo cargarse"}), 503
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos no válidos"}), 400
        
    query = data.get('query', '').strip()
    if not query:
        return jsonify({"error": "Consulta vacía"}), 400
    
    # Prefijo para asegurar respuestas en español
    processed_query = f"Responde en español de manera clara y concisa: {query}"
    
    try:
        # Ejecución optimizada con timeout
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:1b', processed_query],
            capture_output=True,
            text=True,
            timeout=15  # Timeout aumentado para respuestas largas
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or "Error desconocido al ejecutar el modelo"
            return jsonify({"error": "Error en el modelo", "details": error_msg}), 500
        
        response_data = parse_response(result.stdout)
        return jsonify(response_data)
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout", "details": "El modelo tardó demasiado en responder"}), 504
    except Exception as e:
        return jsonify({"error": "Error interno", "details": str(e)}), 500

# Precargar el modelo al iniciar
@app.before_first_request
def initialize():
    load_model()

# Manejo de limpieza al salir
def cleanup():
    print("🔴 Apagando servidor...")

atexit.register(cleanup)

if __name__ == '__main__':
    # Precargar el modelo antes de aceptar conexiones
    load_model()
    app.run(host='0.0.0.0', port=4000, debug=False, threaded=True)