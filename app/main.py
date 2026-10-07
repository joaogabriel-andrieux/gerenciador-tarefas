import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from app.database import db, init_db
from app.routes.auth import auth_bp
from app.routes.tasks import tasks_bp
from app.routes.teams import teams_bp
from app.models import User, Team, Project, Task

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'chave-padrao-dev')

jwt = JWTManager(app)
init_db(app)

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(teams_bp)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "message": "API do Gerenciador de Tarefas rodando com suporte completo a Auth, Tarefas e Equipes!"
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
