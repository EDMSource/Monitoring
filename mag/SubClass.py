





import os
import subprocess
import json
from flask import Flask, jsonify


project = r"Clear"

monitor_path = os.path.join(project, "monitor.exe")

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

