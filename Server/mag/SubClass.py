



# http://localhost:5000/api/metrics

import os
import subprocess
import json
from flask import Flask, jsonify, request

project = os.path.dirname(os.path.abspath(__file__))
monitor_path = os.path.join(project, "..", "..", "Agent", "monitor_agent", "x64", "Debug", "monitor_agent.exe")

app = Flask(__name__)

def get_monitor_output():
    try:
        result = subprocess.run(
            [monitor_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=2
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                data = {"raw_output": result.stdout}
            return data
        else:
            return {"error": f"error: {result.stderr}"}
    except FileNotFoundError:
        return {"error": f"Файл {monitor_path} error pyti"}
    except subprocess.TimeoutExpired:
        return {"error": "Time out"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/api/metrics')
def metrics():
    output = get_monitor_output()
    return jsonify(output)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)


