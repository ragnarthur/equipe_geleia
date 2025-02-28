﻿import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///academia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta'  # Necessária para mensagens flash

db = SQLAlchemy(app)

# Filtro para mapear faixa_cor para um código de cor CSS (hex)
def get_color_code(faixa_cor):
    mapping = {
        "Branca": "#ffffff",
        "Cinza": "#a0a0a0",
        "Amarela": "#ffff00",
        "Laranja": "#ffa500",
        "Verde": "#008000",
        "Azul": "#0000ff",
        "Roxa": "#800080",
        "Marrom": "#a52a2a",
        "Preta": "#000000",
        "Vermelha e Preta (Coral)": "#8b0000",
        "Vermelha e Branca": "#ff0000"
    }
    return mapping.get(faixa_cor, "#cccccc")

app.jinja_env.filters['faixa_color'] = get_color_code

# Modelo de dados atualizado
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # "infantil" ou "adulto"
    idade = db.Column(db.Integer, nullable=False)
    faixa_cor = db.Column(db.String(50), nullable=False)
    faixa_grau = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    data_entrada = db.Column(db.Date, nullable=False)    # Data de entrada na academia
    data_pagamento = db.Column(db.Date, nullable=False)    # Data do último pagamento

    def __repr__(self):
        return f"<Aluno {self.nome}>"

    @property
    def proximo_pagamento(self):
        """Calcula o próximo pagamento (30 dias após o último pagamento)."""
        return self.data_pagamento + timedelta(days=30)

    @property
    def status_mensalidade(self):
        """Retorna 'Em dia' se o último pagamento foi feito há menos de 30 dias, senão 'Atrasado'."""
        if datetime.today().date() <= self.data_pagamento + timedelta(days=30):
            return "Em dia"
        else:
            return "Atrasado"

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/alunos')
def listar_alunos():
    alunos_infantil = Aluno.query.filter_by(categoria="infantil").order_by(Aluno.nome).all()
    alunos_adulto = Aluno.query.filter_by(categoria="adulto").order_by(Aluno.nome).all()
    return render_template('alunos.html', 
                           alunos_infantil=alunos_infantil, 
                           alunos_adulto=alunos_adulto)

@app.route('/alunos/new', methods=['GET', 'POST'])
def criar_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome')
        categoria = request.form.get('categoria')
        idade = request.form.get('idade')
        faixa_cor = request.form.get('faixa_cor')
        faixa_grau = request.form.get('faixa_grau')
        email = request.form.get('email')
        data_entrada_str = request.form.get('data_entrada')
        data_pagamento_str = request.form.get('data_pagamento')
        try:
            idade = int(idade)
        except ValueError:
            flash("Idade inválida. Informe um número inteiro.")
            return redirect(url_for('criar_aluno'))
        try:
            data_entrada = datetime.strptime(data_entrada_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de entrada inválida. Use o formato dd/mm/aaaa.")
            return redirect(url_for('criar_aluno'))
        try:
            data_pagamento = datetime.strptime(data_pagamento_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de pagamento inválida. Use o formato dd/mm/aaaa.")
            return redirect(url_for('criar_aluno'))

        novo_aluno = Aluno(
            nome=nome,
            categoria=categoria,
            idade=idade,
            faixa_cor=faixa_cor,
            faixa_grau=faixa_grau,
            email=email,
            data_entrada=data_entrada,
            data_pagamento=data_pagamento
        )
        db.session.add(novo_aluno)
        db.session.commit()
        flash("Aluno criado com sucesso!")
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', aluno=None)

@app.route('/alunos/<int:aluno_id>/edit', methods=['GET', 'POST'])
def editar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    if request.method == 'POST':
        aluno.nome = request.form.get('nome')
        aluno.categoria = request.form.get('categoria')
        try:
            aluno.idade = int(request.form.get('idade'))
        except ValueError:
            flash("Idade inválida. Informe um número inteiro.")
            return redirect(url_for('editar_aluno', aluno_id=aluno_id))
        aluno.faixa_cor = request.form.get('faixa_cor')
        aluno.faixa_grau = request.form.get('faixa_grau')
        aluno.email = request.form.get('email')
        data_entrada_str = request.form.get('data_entrada')
        data_pagamento_str = request.form.get('data_pagamento')
        try:
            aluno.data_entrada = datetime.strptime(data_entrada_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de entrada inválida. Use o formato dd/mm/aaaa.")
            return redirect(url_for('editar_aluno', aluno_id=aluno_id))
        try:
            aluno.data_pagamento = datetime.strptime(data_pagamento_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de pagamento inválida. Use o formato dd/mm/aaaa.")
            return redirect(url_for('editar_aluno', aluno_id=aluno_id))
        db.session.commit()
        flash("Aluno atualizado com sucesso!")
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', aluno=aluno)

@app.route('/alunos/<int:aluno_id>/delete', methods=['POST'])
def deletar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    flash("Aluno deletado com sucesso!")
    return redirect(url_for('listar_alunos'))

# Função para simular a cobrança mensal (atualiza data_pagamento se necessário)
def cobrar_mensalidade():
    hoje = datetime.today().date()
    alunos = Aluno.query.all()
    for aluno in alunos:
        if hoje > aluno.data_pagamento + timedelta(days=30):
            print(f"Cobrando mensalidade de {aluno.nome} (Atrasado)")
            aluno.data_pagamento = hoje
    db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=cobrar_mensalidade, trigger="interval", days=30)
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
