from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Team, User

teams_bp = Blueprint('teams', __name__, url_prefix='/api/teams')

@teams_bp.route('', methods=['GET'])
@jwt_required()
def get_teams():
    teams = Team.query.all()
    return jsonify([t.to_dict() for t in teams]), 200

@teams_bp.route('', methods=['POST'])
@jwt_required()
def create_team():
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({"error": "O nome da equipe é obrigatório."}), 400

    team = Team(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({"message": "Equipe criada com sucesso!", "team": team.to_dict()}), 201

@teams_bp.route('/<int:team_id>/members', methods=['POST'])
@jwt_required()
def add_member_to_team(team_id):
    team = Team.query.get_or_404(team_id)
    data = request.get_json() or {}
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "Informe o 'user_id' do membro."}), 400

    user = User.query.get_or_404(user_id)
    if user not in team.members:
        team.members.append(user)
        db.session.commit()

    return jsonify({"message": f"Usuário {user.name} adicionado à equipe {team.name} com sucesso!"}), 200
