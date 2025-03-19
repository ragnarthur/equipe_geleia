import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
import pdfkit

# Se o seu banco de dados está na pasta "instance", construa o caminho absoluto:
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'academia.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta'  # Necessária para mensagens flash e sessão

db = SQLAlchemy(app)

# =========================
# DECORATOR PARA LOGIN
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permite acesso se o endpoint for 'login' ou para arquivos estáticos
        if request.endpoint not in ['login', 'static'] and not session.get('logged_in'):
            flash("Por favor, faça login para acessar esta página.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# FILTRO DE COR DA FAIXA
# =========================
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

# =========================
# MODELO DE DADOS
# =========================
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # "infantil" ou "adulto"
    idade = db.Column(db.Integer, nullable=False)
    faixa_cor = db.Column(db.String(50), nullable=False)
    faixa_grau = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    data_entrada = db.Column(db.Date, nullable=False)   # Data de entrada na academia
    data_pagamento = db.Column(db.Date, nullable=False)   # Data do último pagamento
    data_nascimento = db.Column(db.Date, nullable=True)     # Novo campo: Data de Nascimento
    telefone = db.Column(db.String(20), nullable=True)      # Novo campo: Telefone
    mensagem_boasvindas = db.Column(db.Text, nullable=True) # Novo campo: Mensagem de Boas-Vindas
    ativo = db.Column(db.Boolean, default=True)             # Novo campo: Ativo/inativo
    preferencia_comunicacao = db.Column(db.String(20), nullable=True)  # Novo campo: Ex. "email", "whatsapp" ou "ambos"

    def __repr__(self):
        return f"<Aluno {self.nome}>"

    @property
    def proximo_pagamento(self):
        return self.data_pagamento + timedelta(days=30)

    @property
    def status_mensalidade(self):
        if datetime.today().date() <= self.data_pagamento + timedelta(days=30):
            return "Em dia"
        else:
            return "Atrasado"

# =========================
# ROTA DE LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Tela de login simples.
    Usuário e senha fixos para exemplo (admin/1234).
    Em produção, utilize um sistema de usuários com senhas criptografadas.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            flash("Login bem-sucedido!", "success")
            return redirect(url_for('home'))
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

# =========================
# ROTA DE LOGOUT
# =========================
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('login'))

# =========================
# ROTAS PROTEGIDAS (LOGIN NECESSÁRIO)
# =========================
@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/alunos')
@login_required
def listar_alunos():
    alunos_infantil = Aluno.query.filter_by(categoria="infantil").order_by(Aluno.nome).all()
    alunos_adulto = Aluno.query.filter_by(categoria="adulto").order_by(Aluno.nome).all()
    return render_template('alunos.html', 
                           alunos_infantil=alunos_infantil, 
                           alunos_adulto=alunos_adulto)

@app.route('/alunos/new', methods=['GET', 'POST'])
@login_required
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
        data_nascimento_str = request.form.get('data_nascimento')
        telefone = request.form.get('telefone')
        mensagem_boasvindas = request.form.get('mensagem_boasvindas')
        
        try:
            idade = int(idade)
        except ValueError:
            flash("Idade inválida. Informe um número inteiro.", "danger")
            return redirect(url_for('criar_aluno'))
        try:
            data_entrada = datetime.strptime(data_entrada_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de entrada inválida. Use o formato dd/mm/aaaa.", "danger")
            return redirect(url_for('criar_aluno'))
        try:
            data_pagamento = datetime.strptime(data_pagamento_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de pagamento inválida. Use o formato dd/mm/aaaa.", "danger")
            return redirect(url_for('criar_aluno'))
        try:
            data_nascimento = datetime.strptime(data_nascimento_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de nascimento inválida. Use o formato dd/mm/aaaa.", "danger")
            return redirect(url_for('criar_aluno'))
        
        novo_aluno = Aluno(
            nome=nome,
            categoria=categoria,
            idade=idade,
            faixa_cor=faixa_cor,
            faixa_grau=faixa_grau,
            email=email,
            data_entrada=data_entrada,
            data_pagamento=data_pagamento,
            data_nascimento=data_nascimento,
            telefone=telefone,
            mensagem_boasvindas=mensagem_boasvindas,
            ativo=True,
            preferencia_comunicacao="ambos"
        )
        db.session.add(novo_aluno)
        db.session.commit()
        flash("Aluno criado com sucesso!", "success")
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', aluno=None)

@app.route('/alunos/<int:aluno_id>/edit', methods=['GET', 'POST'])
@login_required
def editar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    if request.method == 'POST':
        aluno.nome = request.form.get('nome')
        aluno.categoria = request.form.get('categoria')
        try:
            aluno.idade = int(request.form.get('idade'))
        except ValueError:
            flash("Idade inválida. Informe um número inteiro.", "danger")
            return redirect(url_for('editar_aluno', aluno_id=aluno_id))
        aluno.faixa_cor = request.form.get('faixa_cor')
        aluno.faixa_grau = request.form.get('faixa_grau')
        aluno.email = request.form.get('email')
        data_entrada_str = request.form.get('data_entrada')
        data_pagamento_str = request.form.get('data_pagamento')
        data_nascimento_str = request.form.get('data_nascimento')
        try:
            aluno.data_entrada = datetime.strptime(data_entrada_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de entrada inválida. Use o formato dd/mm/aaaa.", "danger")
            return redirect(url_for('editar_aluno', aluno_id=aluno_id))
        try:
            aluno.data_pagamento = datetime.strptime(data_pagamento_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de pagamento inválida. Use o formato dd/mm/aaaa.", "danger")
            return redirect(url_for('editar_aluno', aluno_id=aluno_id))
        try:
            aluno.data_nascimento = datetime.strptime(data_nascimento_str, '%d/%m/%Y').date()
        except ValueError:
            flash("Data de nascimento inválida. Use o formato dd/mm/aaaa.", "danger")
            return redirect(url_for('editar_aluno', aluno_id=aluno_id))
        aluno.telefone = request.form.get('telefone')
        aluno.mensagem_boasvindas = request.form.get('mensagem_boasvindas')
        db.session.commit()
        flash("Aluno atualizado com sucesso!", "success")
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', aluno=aluno)

@app.route('/alunos/<int:aluno_id>/delete', methods=['POST'])
@login_required
def deletar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    flash("Aluno deletado com sucesso!", "success")
    return redirect(url_for('listar_alunos'))

@app.route('/alunos/<int:aluno_id>/pagar', methods=['POST'])
@login_required
def pagar_mensalidade(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    aluno.data_pagamento = datetime.today().date()
    db.session.commit()
    
    # Define o valor da mensalidade com base na categoria
    valor = 120 if aluno.categoria == 'adulto' else 100
    recibo = {
        'nome': aluno.nome,
        'data_pagamento': aluno.data_pagamento.strftime('%d/%m/%Y'),
        'valor': valor,
        'mensagem': "Pagamento realizado com sucesso! Seu recibo foi gerado para envio por email/WhatsApp.",
        'proximo_pagamento': aluno.proximo_pagamento.strftime('%d/%m/%Y')
    }
    flash(f"Mensalidade paga com sucesso para <strong>{aluno.nome}</strong>!", "success")
    # Exibe o recibo com pdf_mode=False (botões visíveis)
    return render_template("recibo.html", recibo=recibo, pdf_mode=False)

# =========================
# ROTA PARA GERAR PDF DO RECIBO
# =========================
@app.route('/recibo/pdf')
@login_required
def recibo_pdf():
    # Recupera os dados do recibo via query string
    nome = request.args.get('nome')
    data_pagamento = request.args.get('data_pagamento')
    valor = request.args.get('valor')
    mensagem = request.args.get('mensagem')
    proximo_pagamento = request.args.get('proximo_pagamento')

    # Reconstrói o dicionário do recibo com a nova informação
    recibo = {
        'nome': nome,
        'data_pagamento': data_pagamento,
        'valor': valor,
        'mensagem': mensagem,
        'proximo_pagamento': proximo_pagamento
    }
    
    # Renderiza o template de recibo com pdf_mode=True (botões ocultos)
    rendered = render_template('recibo.html', recibo=recibo, pdf_mode=True)
    
    # Define as opções para permitir acesso a arquivos locais, se necessário
    options = {
        'enable-local-file-access': None
    }
    
    # Converte o HTML renderizado em PDF
    pdf = pdfkit.from_string(rendered, False, options=options)
    
    # Gera o nome do arquivo com o nome do aluno e data do pagamento
    safe_nome = nome.replace(" ", "_") if nome else "recibo"
    safe_data = data_pagamento.replace("/", "-") if data_pagamento else "data"
    filename = f"recibo_{safe_nome}_{safe_data}.pdf"
    
    # Prepara a resposta para download
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# =========================
# ROTA MENSALIDADES (PROTEGIDA)
# =========================
@app.route('/mensalidades')
@login_required
def mensalidades():
    """Exibe um resumo financeiro das mensalidades, usando dados reais do banco."""
    total_adultos = Aluno.query.filter_by(categoria="adulto").count()
    total_infantil = Aluno.query.filter_by(categoria="infantil").count()

    valor_adulto = 120
    valor_infantil = 100

    receita_total = (total_adultos * valor_adulto) + (total_infantil * valor_infantil)
    dist_categoria = [total_adultos, total_infantil]

    # Calcula a receita mensal real com base na data de pagamento
    monthly_revenue = {m: 0 for m in range(1, 13)}
    # Calcula o status mensal (pagamentos "Em dia" e "Atrasado" por mês)
    monthly_status = {m: {"Em dia": 0, "Atrasado": 0} for m in range(1, 13)}
    for aluno in Aluno.query.all():
        mes_pg = aluno.data_pagamento.month
        if aluno.categoria == "adulto":
            monthly_revenue[mes_pg] += valor_adulto
        else:
            monthly_revenue[mes_pg] += valor_infantil
        monthly_status[mes_pg][aluno.status_mensalidade] += 1

    # Status geral dos pagamentos
    status_counts = {"Em dia": 0, "Atrasado": 0}
    for aluno in Aluno.query.all():
        status_counts[aluno.status_mensalidade] += 1

    meses_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                    "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    data_values = [monthly_revenue[m] for m in range(1, 13)]

    return render_template("mensalidades.html",
                           total_adultos=total_adultos,
                           total_infantil=total_infantil,
                           receita_total=receita_total,
                           dist_categoria=dist_categoria,
                           meses_labels=meses_labels,
                           data_values=data_values,
                           valor_adulto=valor_adulto,
                           valor_infantil=valor_infantil,
                           status_counts=status_counts,
                           monthly_status=monthly_status)

# =========================
# FUNÇÃO PARA COBRANÇA
# =========================
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
