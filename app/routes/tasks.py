from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.database import db
from app.models.task import Project, Task, Team
from app.models.user import User

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')

# --- ROTAS DE PROJETOS ---

@tasks_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects]), 200

@tasks_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({"error": "O título do projeto é obrigatório."}), 400

    project = Project(
        title=data['title'],
        description=data.get('description', ''),
        team_id=data.get('team_id')
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({"message": "Projeto criado com sucesso!", "project": project.to_dict()}), 201


# --- ROTAS DE TAREFAS ---

@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks_by_project(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project.id).all()
    return jsonify([t.to_dict() for t in tasks]), 200

@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    Project.query.get_or_404(project_id)
    data = request.get_json() or {}

    if not data.get('title'):
        return jsonify({"error": "O título da tarefa é obrigatório."}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'MEDIUM'),
        status=data.get('status', 'PENDING'),
        project_id=project_id,
        assigned_to_id=data.get('assigned_to_id')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Tarefa criada com sucesso!", "task": task.to_dict()}), 201

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json() or {}

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    task.assigned_to_id = data.get('assigned_to_id', task.assigned_to_id)

    db.session.commit()
    return jsonify({"message": "Tarefa atualizada com sucesso!", "task": task.to_dict()}), 200


# --- ROUTE DO DASHBOARD / METRICAS ---

@tasks_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    total_tasks = Task.query.count()
    total_projects = Project.query.count()
    total_teams = Team.query.count()

    # Agrupamento por status
    status_counts = db.session.query(
        Task.status, func.count(Task.id)
    ).group_by(Task.status).all()
    tasks_by_status = {status: count for status, count in status_counts}

    # Agrupamento por prioridade
    priority_counts = db.session.query(
        Task.priority, func.count(Task.id)
    ).group_by(Task.priority).all()
    tasks_by_priority = {priority: count for priority, count in priority_counts}

    # Tarefas por usuário
    users = User.query.all()
    tasks_by_user = []
    for u in users:
        assigned_count = Task.query.filter_by(assigned_to_id=u.id).count()
        completed_count = Task.query.filter_by(assigned_to_id=u.id, status='DONE').count()
        tasks_by_user.append({
            "user_id": u.id,
            "user_name": u.name,
            "total_assigned": assigned_count,
            "completed": completed_count,
            "pending": assigned_count - completed_count
        })

    return jsonify({
        "summary": {
            "total_teams": total_teams,
            "total_projects": total_projects,
            "total_tasks": total_tasks
        },
        "tasks_by_status": {
            "PENDING": tasks_by_status.get('PENDING', 0),
            "IN_PROGRESS": tasks_by_status.get('IN_PROGRESS', 0),
            "DONE": tasks_by_status.get('DONE', 0)
        },
        "tasks_by_priority": {
            "LOW": tasks_by_priority.get('LOW', 0),
            "MEDIUM": tasks_by_priority.get('MEDIUM', 0),
            "HIGH": tasks_by_priority.get('HIGH', 0)
        },
        "workload_by_user": tasks_by_user
    }), 200
