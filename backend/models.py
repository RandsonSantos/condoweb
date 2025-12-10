from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class Morador(db.Model):
    __tablename__ = "moradores"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    telefone = db.Column(db.String(30), nullable=True)
    bloco = db.Column(db.String(20), nullable=True)
    apartamento = db.Column(db.String(20), nullable=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    permissoes = db.Column(db.JSON, default={"abrir_veicular": True, "abrir_pedestre": True})

    veiculos = db.relationship("Veiculo", backref="morador", cascade="all, delete-orphan")
    acessos = db.relationship("AcessoLog", backref="morador", cascade="all, delete-orphan")

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

class Veiculo(db.Model):
    __tablename__ = "veiculos"
    id = db.Column(db.Integer, primary_key=True)
    morador_id = db.Column(db.Integer, db.ForeignKey("moradores.id"), nullable=False)
    modelo = db.Column(db.String(100), nullable=True)
    placa = db.Column(db.String(20), nullable=True)
    cor = db.Column(db.String(50), nullable=True)

class Camera(db.Model):
    __tablename__ = "cameras"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), default="rtsp")  # 'rtsp','mjpeg','hls'
    url = db.Column(db.String(500), nullable=False)
    public = db.Column(db.Boolean, default=False)
    porta_tipo = db.Column(db.String(20), default="veicular")  # veicular / pedestre / ambos

class AcessoLog(db.Model):
    __tablename__ = "acessos"
    id = db.Column(db.Integer, primary_key=True)
    morador_id = db.Column(db.Integer, db.ForeignKey("moradores.id"), nullable=True)
    tipo_portao = db.Column(db.String(20), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
