from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
import os
import time
import threading

BROKER = os.getenv("BROKER", "mqtt")  
TOPICO = "lab/03/dht11"

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

def ao_conectar(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT (código {rc})")
    client.subscribe(TOPICO)

def ao_receber_mensagem(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        dados = json.loads(payload)
        print(f"Temperatura: {dados['temperatura']}°C | Umidade: {dados['umidade']}%")
        socketio.emit("atualizacao_dados", dados)
    except Exception as erro:
        print("Erro ao processar mensagem:", erro)
        print("Payload recebido:", msg.payload)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = ao_conectar
mqtt_client.on_message = ao_receber_mensagem

#Inicia o loop MQTT em uma thread separada
def mqtt_loop():
    """Loop para conectar ao MQTT em background."""
    while True:
        try:
            print(f"Tentando conectar ao broker MQTT em {BROKER}:1883 ...")
            mqtt_client.connect(BROKER, 1883, 60)
            print("Conectado ao broker MQTT!")
            break
        except Exception as e:
            print("Falha ao conectar ao MQTT. Tentando novamente em 2s...")
            print("Erro:", e)
            time.sleep(2)
    mqtt_client.loop_forever()

threading.Thread(target=mqtt_loop, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    print("Servidor Flask rodando em http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
