import os
import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns
from rich import print

API_URL = os.getenv("API_URL", "http://localhost:5000/api")
console = Console()

def get_auth_token():
    console.print(Panel.fit("[bold cyan]GERENCIADOR DE TAREFAS - CLI[/bold cyan]\n[dim]Acesse para visualizar o Kanban e Métricas[/dim]", title="⚡ Trello Terminal"))
    email = input("E-mail [admin@teste.com]: ").strip() or "admin@teste.com"
    password = input("Senha [senha123]: ").strip() or "senha123"

    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        if res.status_code == 200:
            console.print("[bold green]✓ Login realizado com sucesso![/bold green]\n")
            return res.json()["access_token"]
        else:
            console.print(f"[bold red]Erro ao autenticar:[/bold red] {res.json().get('error')}")
            sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Não foi possível conectar à API:[/bold red] {e}")
        sys.exit(1)

def fetch_dashboard(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{API_URL}/dashboard", headers=headers)
    return res.json() if res.status_code == 200 else None

def fetch_tasks(token, project_id=1):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{API_URL}/projects/{project_id}/tasks", headers=headers)
    return res.json() if res.status_code == 200 else []

def render_kanban(tasks):
    pending_table = Table(title="📌 A FAZER (PENDING)", style="yellow", expand=True)
    pending_table.add_column("ID", style="dim", width=4)
    pending_table.add_column("Título", style="bold")
    pending_table.add_column("Prio", justify="center")

    progress_table = Table(title="🚀 EM ANDAMENTO (IN_PROGRESS)", style="cyan", expand=True)
    progress_table.add_column("ID", style="dim", width=4)
    progress_table.add_column("Título", style="bold")
    progress_table.add_column("Prio", justify="center")

    done_table = Table(title="✅ CONCLUÍDO (DONE)", style="green", expand=True)
    done_table.add_column("ID", style="dim", width=4)
    done_table.add_column("Título", style="bold")
    done_table.add_column("Prio", justify="center")

    prio_colors = {"HIGH": "[bold red]ALTA[/bold red]", "MEDIUM": "[yellow]MÉDIA[/yellow]", "LOW": "[blue]BAIXA[/blue]"}

    for t in tasks:
        prio = prio_colors.get(t["priority"], t["priority"])
        row = (str(t["id"]), t["title"], prio)
        
        if t["status"] == "PENDING":
            pending_table.add_row(*row)
        elif t["status"] == "IN_PROGRESS":
            progress_table.add_row(*row)
        elif t["status"] == "DONE":
            done_table.add_row(*row)

    console.print(Columns([pending_table, progress_table, done_table], equal=True, expand=True))

def main():
    token = get_auth_token()
    
    # Busca dados
    dash = fetch_dashboard(token)
    tasks = fetch_tasks(token, project_id=1)

    if dash:
        summary = dash["summary"]
        prio = dash["tasks_by_priority"]
        metrics_text = (
            f"[bold]Projetos:[/bold] {summary['total_projects']}  |  "
            f"[bold]Equipes:[/bold] {summary['total_teams']}  |  "
            f"[bold]Total de Tarefas:[/bold] {summary['total_tasks']}\n"
            f"[bold red]Alta Prio:[/bold red] {prio['HIGH']}  |  "
            f"[yellow]Média Prio:[/yellow] {prio['MEDIUM']}  |  "
            f"[blue]Baixa Prio:[/blue] {prio['LOW']}"
        )
        console.print(Panel(metrics_text, title="📊 Métricas Gerais do Sistema", border_style="bold magenta"))

    console.print("\n[bold white underline]QUADRO KANBAN - PROJETO #1[/bold white underline]\n")
    render_kanban(tasks)

if __name__ == "__main__":
    main()
