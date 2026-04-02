



# http://localhost:5000/api/metrics

# http://localhost:5000/api/kill/<pid>


import os
import subprocess
import json
import signal
from flask import Flask, jsonify, request, send_from_directory

try:
    import ctypes
    kr = ctypes.windll.kernel32
except (ImportError, AttributeError):
    kr = None

project = os.path.dirname(os.path.abspath(__file__))

monitor_path = os.path.join(project, "monitor_agent.exe")


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
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw_output": result.stdout}
        else:
            return {"error": result.stderr}
    except FileNotFoundError:
        return {"error": f"monitor.exe не найден по пути {monitor_path}"}
    except subprocess.TimeoutExpired:
        return {"error": "Timeout"}
    except Exception as e:
        return {"error": str(e)}

def get_processes():
    try:
        result = subprocess.run(
            ["tasklist", "/fo", "csv", "/nh"],
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        procs = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                procs.append({"name": parts[0], "pid": int(parts[1])})
        return procs
    except Exception as e:
        return [{"name": f"Ошибка: {e}", "pid": 0}]

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(__file__), 'interface.html')

@app.route('/api/metrics')
def metrics():
    mon = get_monitor_output()
    procs = get_processes()
    response = {
        "cpu": mon.get("cpu", "0%"),
        "ram": mon.get("ram", "0%"),
        "disk": mon.get("disk", "0%"),
        "procs": procs[:30]
    }
    return jsonify(response)

@app.route('/api/kill/<int:pid>', methods=['POST', 'DELETE'])
def kill_process(pid):

    try:
        result = subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        if result.returncode == 0:
            print(f"[KILL] Процесс PID={pid} успешно завершён")
            return jsonify({
                "status": "ok",
                "message": f"Процесс с PID {pid} завершён",
                "pid": pid
            })
        else:

            error_msg = result.stderr.strip()
            print(f"[KILL] Ошибка при завершении PID={pid}: {error_msg}")
            return jsonify({
                "status": "error",
                "message": f"Не удалось завершить процесс: {error_msg}",
                "pid": pid
            }), 400
    except Exception as e:
        print(f"[KILL] Исключение: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "pid": pid
        }), 500


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)