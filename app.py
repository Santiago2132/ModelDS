from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_model():
    data = request.json
    query = data.get('query')
    result = subprocess.run(['ollama','run','deepseek-r1:1.5b', query], capture_output=True, text=True)
    return jsonify({'response': result.stdout})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)