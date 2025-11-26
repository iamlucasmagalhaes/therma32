from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json

# -------------------------------
# CONFIGURAÇÕES
# -------------------------------
BROKER = "localhost"
TOPICO = "lab/03/dht11"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# -------------------------------
# CALLBACKS DO MQTT
# -------------------------------
def ao_conectar(client, userdata, flags, rc):
    print(f"Conectado ao broker (código {rc})")
    client.subscribe(TOPICO)

def ao_receber_mensagem(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        dados = json.loads(payload)

        print(f"Temperatura: {dados['temperatura']}°C | Umidade: {dados['umidade']}%")

        # envia os dados para o frontend via websocket
        socketio.emit("atualizacao_dados", dados)

    except Exception as erro:
        print("Erro ao processar mensagem:", erro)
        print("Payload recebido:", msg.payload)

# -------------------------------
# CONFIGURAÇÃO DO CLIENTE MQTT
# -------------------------------
mqtt_client = mqtt.Client()
mqtt_client.on_connect = ao_conectar
mqtt_client.on_message = ao_receber_mensagem
mqtt_client.connect(BROKER, 1883, 60)
mqtt_client.loop_start()

# -------------------------------
# ROTAS FLASK
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------
# INICIALIZAÇÃO DO SERVIDOR
# -------------------------------
if __name__ == "__main__":
    print("Servidor Flask rodando em http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
