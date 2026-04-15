



# http://localhost:5000/api/metrics

# http://localhost:5000

# http://localhost:5000/api/kill/<pid>


import os # для работы с путями и файловой системой
import subprocess # Запуск внешних программ
import json
import signal
import sys
from flask import Flask, jsonify, request, send_from_directory # Создание веб сервака 


try:
    import ctypes # вызывает системные функции для защиты от закрытия
    kr = ctypes.windll.kernel32 # Предоставляет доступ к стандартным Windows DLL 
except (ImportError, AttributeError):
    kr = None

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# 26-27 нахождение пути к скрипту (в данном случаи нахождение monitor_agent.exe)
monitor_path = get_resource_path("monitor_agent.exe")
html_path = get_resource_path("")


app = Flask(__name__) # Создание и обработка входящих запросо HTML

def get_monitor_output(): #Функция запускающию cpp файл и читает ее вывод (кодировка cp1251)
    try:
        result = subprocess.run(
            [monitor_path], # В переменной, путь к файлу
            capture_output=True, # перехват
            text=True, # Возращает вывод в виде текст
            encoding='cp1251',
            timeout=2
        )
        if result.returncode == 0: # Успешное или нет
            try:
                return json.loads(result.stdout) # пытается превратить вывод программы в JSON
            except json.JSONDecodeError:
                return {"raw_output": result.stdout}
        else:
            return {"error": result.stderr}
    except FileNotFoundError:
        return {"error": f"monitor.exe не найден по пути {monitor_path}"} # Есть, нет - файла?
    except subprocess.TimeoutExpired:
        return {"error": "Timeout"} # Если программа не уложилась в 2 секунды возвращает timeout
    except Exception as e:
        return {"error": str(e)} # Лоивт другие любые ошибки 

def get_processes(): # Получение всех работающих процессов
    try:
        result = subprocess.run( # Запуск программы и ожидание ее завершения
            ["tasklist", "/fo", "csv", "/nh"], #Вывода списка процессов в формате CSV
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        procs = [] # тут будет список о процессах
        for line in result.stdout.strip().split('\n'): # Убирает лишние пробелы и разбиваем строки по символам
            if not line:
                continue
            parts = line.strip('"').split('","') # удаляет кавычки в начале и конце строки
            if len(parts) >= 2:
                procs.append({"name": parts[0], "pid": int(parts[1])}) #Добавляет в список словарь с именем процесса
        return procs
    except Exception as e:
        return [{"name": f"Ошибка"}]

@app.route('/') # Сигнал который вызывается если человек переходит по ссылке
def index():
    return send_from_directory(html_path, 'interface.html') #Ищем интерфейс и загружаем на сайт

@app.route('/api/metrics') #декоратор связывающий эту функцию с URL-адресом
def metrics():
    mon = get_monitor_output()
    print("DEBUG from C++:", mon) # Выводит полученный от C++ словарь в консоль сервера
    procs = mon.get("processes", get_processes())
    response = {
        "cpu": mon.get("cpu", "0%"),
        "ram": mon.get("ram", "0%"),
        "disk": mon.get("disk", "0%"),
        "procs": procs[:200] # Сколько процессов вывести (и 
                             # изменить в interface.html ~80 строку тоже на число которое нужно для вывода)
    }
    return jsonify(response) # превращает словарь в JSON и отправляет клиенту

@app.route('/api/kill/<int:pid>', methods=['POST', 'DELETE'])
def kill_process(pid): #Функция убивающая процесс

    try:
        result = subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        if result.returncode == 0: # Если да нет
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
            }), 400 # HTTP-статус-код ответа
    except Exception as e:# ловит любые ошибки при попытке убить процесс
                          # и возвращает клиенту ошибку сервера 500
        print(f"[KILL] Исключение: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "pid": pid
        }), 500 # HTTP-статус-код ответа

# Часть запускает Flask-приложение в режиме без отладки на локальном компьютере
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)