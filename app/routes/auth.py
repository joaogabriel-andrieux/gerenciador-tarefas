from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.database import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"error": "Campos 'name', 'email' e 'password' são obrigatórios."}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "E-mail já cadastrado."}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'MEMBER')
    )
    
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso!", "user": user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Informe e-mail e senha."}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Credenciais inválidas."}), 401

    # Cria o token JWT contendo o ID e o e-mail do usuário como identidade
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login realizado com sucesso!",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200
