# ⚡ Terminal Task Manager API & CLI

Sistema de gerenciamento de tarefas e projetos baseado em **arquitetura RESTful desacoplada**, desenvolvido em **Python**, **Flask** e **SQLAlchemy**, empacotado em **Docker Compose** e acompanhado por uma **Interface TUI (Terminal User Interface)** rica e responsiva.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.11+, Flask, Flask-SQLAlchemy, Flask-JWT-Extended
* **Banco de Dados:** SQLite (ORM SQLAlchemy)
* **Containerização:** Docker & Docker Compose
* **Interface TUI/CLI:** Rich & Requests

---

## 🚀 Como Executar o Projeto

### Pró-requisitos
* Docker e Docker Compose instalados.

### 1. Clonar o repositório e subir os containers
```bash
git clone [https://github.com/seu-usuario/gerenciador-tarefas.git](https://github.com/seu-usuario/gerenciador-tarefas.git)
cd gerenciador-tarefas
docker compose up -d
