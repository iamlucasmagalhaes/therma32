from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
import os
import time
import threading
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

# =========================
# Configurações MQTT
# =========================
BROKER = os.getenv("BROKER", "mqtt")
TOPICO = "lab/03/dht11"

# =========================
# Configurações Banco
# =========================
DB_HOST = os.getenv("DB_HOST", "database")
DB_NAME = os.getenv("DB_NAME", "app")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

# =========================
# Modelo da Tabela
# =========================
class DHT11Leitura(Base):
    __tablename__ = "leituras_dht11"

    id = Column(Integer, primary_key=True)
    temperatura = Column(Float, nullable=False)
    umidade = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# =========================
# Flask / Socket.IO
# =========================
app = Flask(__name__, template_folder="templates")
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

# =========================
# MQTT Callbacks
# =========================
def ao_conectar(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT (código {rc})")
    client.subscribe(TOPICO)

def ao_receber_mensagem(client, userdata, msg):
    db = SessionLocal()
    try:
        payload = msg.payload.decode()
        dados = json.loads(payload)

        temperatura = float(dados["temperatura"])
        umidade = float(dados["umidade"])

        # Salva no banco
        leitura = DHT11Leitura(
            temperatura=temperatura,
            umidade=umidade
        )
        db.add(leitura)
        db.commit()

        log_texto = f"Temperatura: {temperatura}°C | Umidade: {umidade}%"
        print(log_texto)

        # Envia para frontend
        socketio.emit("atualizacao_dados", {
            "temperatura": temperatura,
            "umidade": umidade
        })
        socketio.emit("log_mensagem", {
            "mensagem": log_texto
        })

    except Exception as erro:
        db.rollback()
        erro_msg = f"Erro ao processar mensagem: {erro}"
        print(erro_msg)
        socketio.emit("log_mensagem", {"mensagem": erro_msg})

    finally:
        db.close()

# =========================
# MQTT Setup
# =========================
mqtt_client = mqtt.Client()
mqtt_client.on_connect = ao_conectar
mqtt_client.on_message = ao_receber_mensagem

def mqtt_loop():
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

# =========================
# Rotas Flask
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# Run
# =========================
if __name__ == "__main__":
    print("Servidor Flask rodando em http://0.0.0.0:5000")
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
        allow_unsafe_werkzeug=True
    )
