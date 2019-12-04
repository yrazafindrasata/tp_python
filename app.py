from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def home():
  return 'Bienvenue !'

@app.route('/devices', methods=['GET'])
def devices():
  devices = parse_from_json()
  return render_template("devices.html", devices=devices)

def parse_from_json():
  devices = []
  with open('./devices.json', 'r') as f:
    data = json.loads(f.read())
    for id in data:
      devices.append({"id": id,
                      "name": data[id]["name"],
                      "rssi": data[id]["rssi"] if "rssi" in data[id] else "?"})
    return devices

def dump_to_json(devices):
  pass
