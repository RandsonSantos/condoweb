from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context, send_from_directory
from extensions import db
from models import Morador, Veiculo, Camera, AcessoLog
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import requests, os

bp = Blueprint("api", __name__, url_prefix="/api")

# AUTH
@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    required = ['nome','cpf','password']
    for r in required:
        if r not in data:
            return jsonify({'msg':f'campo {r} é obrigatório'}),400
    if Morador.query.filter_by(cpf=data['cpf']).first():
        return jsonify({'msg':'CPF já cadastrado'}),400
    m = Morador(nome=data['nome'], cpf=data['cpf'], email=data.get('email'), telefone=data.get('telefone'), bloco=data.get('bloco'), apartamento=data.get('apartamento'))
    m.set_password(data['password'])
    db.session.add(m); db.session.commit()
    return jsonify({'msg':'morador cadastrado','id':m.id}),201

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    cpf = data.get('cpf'); password = data.get('password')
    if not cpf or not password:
        return jsonify({'msg':'cpf e password obrigatórios'}),400
    m = Morador.query.filter_by(cpf=cpf).first()
    if not m or not m.check_password(password):
        return jsonify({'msg':'credenciais inválidas'}),401
    access_token = create_access_token(identity=m.id)
    return jsonify({'access_token':access_token,'morador_id':m.id,'nome':m.nome})

# CRUD Moradores (admin use) - simple
@bp.route('/moradores', methods=['GET'])
@jwt_required()
def list_moradores():
    ms = Morador.query.all()
    out = []
    for m in ms:
        out.append({'id':m.id,'nome':m.nome,'cpf':m.cpf,'email':m.email,'telefone':m.telefone,'bloco':m.bloco,'apartamento':m.apartamento,'permissoes':m.permissoes})
    return jsonify(out)

@bp.route('/morador/<int:morador_id>', methods=['PUT','DELETE','GET'])
@jwt_required()
def manage_morador(morador_id):
    m = Morador.query.get_or_404(morador_id)
    if request.method == 'GET':
        return jsonify({'id':m.id,'nome':m.nome,'cpf':m.cpf,'email':m.email,'telefone':m.telefone,'bloco':m.bloco,'apartamento':m.apartamento,'permissoes':m.permissoes})
    if request.method == 'DELETE':
        db.session.delete(m); db.session.commit(); return jsonify({'msg':'removido'})
    data = request.get_json() or {}
    for f in ('nome','email','telefone','bloco','apartamento'):
        if f in data: setattr(m,f,data[f])
    if 'password' in data: m.set_password(data['password'])
    db.session.commit()
    return jsonify({'msg':'atualizado'})

@bp.route('/morador', methods=['POST'])
@jwt_required()
def create_morador():
    data = request.get_json() or {}
    required = ['nome','cpf','password']
    for r in required:
        if r not in data:
            return jsonify({'msg':f'campo {r} é obrigatório'}),400
    if Morador.query.filter_by(cpf=data['cpf']).first():
        return jsonify({'msg':'cpf já cadastrado'}),400
    m = Morador(nome=data['nome'], cpf=data['cpf'], email=data.get('email'), telefone=data.get('telefone'), bloco=data.get('bloco'), apartamento=data.get('apartamento'))
    m.set_password(data['password'])
    db.session.add(m); db.session.commit()
    return jsonify({'msg':'criado','id':m.id}),201

# Cameras CRUD
@bp.route('/cameras', methods=['GET','POST'])
@jwt_required()
def cameras():
    if request.method == 'GET':
        cams = Camera.query.all()
        out = []
        for c in cams:
            out.append({'id':c.id,'nome':c.nome,'tipo':c.tipo,'stream_endpoint':f'/api/camera/{c.id}/stream','porta_tipo':c.porta_tipo,'public':c.public})
        return jsonify(out)
    data = request.get_json() or {}
    required = ['nome','tipo','url']
    for r in required:
        if r not in data: return jsonify({'msg':f'{r} obrigatório'}),400
    c = Camera(nome=data['nome'], tipo=data['tipo'], url=data['url'], public=data.get('public', False), porta_tipo=data.get('porta_tipo','veicular'))
    db.session.add(c); db.session.commit()
    return jsonify({'msg':'criada','id':c.id}),201

@bp.route('/camera/<int:camera_id>', methods=['GET','PUT','DELETE'])
@jwt_required()
def camera_manage(camera_id):
    c = Camera.query.get_or_404(camera_id)
    if request.method == 'GET':
        return jsonify({'id':c.id,'nome':c.nome,'tipo':c.tipo,'url':c.url,'public':c.public,'porta_tipo':c.porta_tipo})
    if request.method == 'DELETE':
        db.session.delete(c); db.session.commit(); return jsonify({'msg':'removida'})
    data = request.get_json() or {}
    for f in ('nome','tipo','url','public','porta_tipo'):
        if f in data: setattr(c,f,data[f])
    db.session.commit()
    return jsonify({'msg':'atualizada'})

# Stream proxy / hint for HLS
@bp.route('/camera/<int:camera_id>/stream')
@jwt_required()
def camera_stream(camera_id):
    c = Camera.query.get_or_404(camera_id)
    if c.tipo == 'mjpeg':
        try:
            r = requests.get(c.url, stream=True, timeout=5)
            return Response(stream_with_context(r.iter_content(chunk_size=1024)), headers={'Content-Type': r.headers.get('Content-Type','multipart/x-mixed-replace;boundary=--myboundary')})
        except Exception as e:
            return jsonify({'msg':'erro ao acessar camera','error':str(e)}),500
    if c.tipo == 'rtsp' or c.tipo == 'hls':
        hls_path = current_app.config.get('HLS_OUTPUT_DIR','/var/www/html/streams')
        hls_rel = f'/streams/{camera_id}.m3u8'
        return jsonify({'hls_url': hls_rel, 'note':'use HLS player (hls.js) to play this stream'})
    return jsonify({'msg':'tipo não suportado'}),400

# Open gate (calls ESP32)
@bp.route('/portao/abrir', methods=['POST'])
@jwt_required()
def abrir_portao():
    morador_id = get_jwt_identity()
    data = request.get_json() or {}
    tipo = data.get('tipo','veicular')
    camera_id = data.get('camera_id')
    morador = Morador.query.get(morador_id)
    campo = 'abrir_veicular' if tipo == 'veicular' else 'abrir_pedestre'
    if not morador.permissoes.get(campo, False):
        log = AcessoLog(morador_id=morador.id, tipo_portao=tipo, status='negado', descricao='sem permissao')
        db.session.add(log); db.session.commit()
        return jsonify({'msg':'sem permissao'}),403
    esp_url = current_app.config.get('ESP32_BASE_URL').rstrip('/') + '/open'
    headers = {}
    token = current_app.config.get('ESP32_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        resp = requests.post(esp_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            log = AcessoLog(morador_id=morador.id, tipo_portao=tipo, status='ok', descricao=f'aberto camera:{camera_id}')
            db.session.add(log); db.session.commit()
            return jsonify({'msg':'portao aberto'}),200
        else:
            log = AcessoLog(morador_id=morador.id, tipo_portao=tipo, status='erro', descricao=f'esp status {resp.status_code}')
            db.session.add(log); db.session.commit()
            return jsonify({'msg':'erro ao abrir portao'}),500
    except Exception as e:
        log = AcessoLog(morador_id=morador.id, tipo_portao=tipo, status='erro', descricao=str(e))
        db.session.add(log); db.session.commit()
        return jsonify({'msg':'erro de comunicacao','error':str(e)}),500

# logs
@bp.route('/logs')
@jwt_required()
def get_logs():
    logs = AcessoLog.query.order_by(AcessoLog.data_hora.desc()).limit(300).all()
    out = [{'id':l.id,'morador_id':l.morador_id,'tipo_portao':l.tipo_portao,'data_hora':l.data_hora.isoformat(),'status':l.status,'descricao':l.descricao} for l in logs]
    return jsonify(out)
