from app import app, db, Aluno
from datetime import datetime, timedelta
import random

def random_date(start, end):
    """Retorna uma data aleatória entre start e end."""
    delta = end - start
    random_days = random.randrange(delta.days + 1)
    return start + timedelta(days=random_days)

def populate_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Banco de dados recriado com sucesso.")

        juvenile_belts = ["Branca", "Cinza", "Amarela", "Laranja", "Verde"]
        adult_belts = ["Azul", "Roxa", "Marrom", "Preta"]

        first_names = ["João", "Maria", "Pedro", "Ana", "Lucas", "Carlos", "Fernanda", "Bruno",
                       "Gabriela", "Marcos", "Rafaela", "Ricardo", "Larissa", "Eduardo", "Priscila",
                       "Mateus", "Beatriz", "Diego", "Camila", "Juliana"]
        last_names = ["Silva", "Oliveira", "Santos", "Souza", "Lima", "Pereira", "Costa", "Gomes",
                      "Rodrigues", "Almeida"]

        alunos_imaginarios = []
        hoje = datetime.today().date()
        inicio_simulacao = datetime(2023, 1, 1).date()

        for i in range(50):
            # 40% infantil, 60% adulto
            if random.random() < 0.4:
                idade = random.randint(4, 15)
                categoria_exibicao = "infantil"
                belt_choice = random.choice(juvenile_belts)
                grau = "" if belt_choice == "Branca" else f"{random.randint(0, 4)}º Grau"
            else:
                idade = random.randint(16, 50)
                categoria_exibicao = "adulto"
                belt_choice = random.choice(adult_belts)
                grau = f"{random.randint(0, 4)}º Grau"

            nome = f"{random.choice(first_names)} {random.choice(last_names)}"
            email = f"{nome.split()[0].lower()}.{nome.split()[1].lower()}{random.randint(1,100)}@example.com"
            # Data de entrada: entre 01/01/2023 e hoje
            data_entrada = random_date(inicio_simulacao, hoje)
            # Data de pagamento: entre data de entrada e hoje
            data_pagamento = random_date(data_entrada, hoje)

            alunos_imaginarios.append({
                "nome": nome,
                "categoria": categoria_exibicao,
                "idade": idade,
                "faixa_cor": belt_choice,
                "faixa_grau": grau,
                "email": email,
                "data_entrada": data_entrada.strftime('%Y-%m-%d'),
                "data_pagamento": data_pagamento.strftime('%Y-%m-%d')
            })
        
        for aluno_data in alunos_imaginarios:
            try:
                data_en = datetime.strptime(aluno_data['data_entrada'], '%Y-%m-%d').date()
                data_pg = datetime.strptime(aluno_data['data_pagamento'], '%Y-%m-%d').date()
            except ValueError as e:
                print(f"Erro ao converter data para {aluno_data['nome']}: {e}")
                continue

            novo_aluno = Aluno(
                nome=aluno_data['nome'],
                categoria=aluno_data['categoria'],
                idade=aluno_data['idade'],
                faixa_cor=aluno_data['faixa_cor'],
                faixa_grau=aluno_data['faixa_grau'],
                email=aluno_data['email'],
                data_entrada=data_en,
                data_pagamento=data_pg
            )
            db.session.add(novo_aluno)
        
        try:
            db.session.commit()
            print("Banco de dados populado com sucesso!")
        except Exception as e:
            db.session.rollback()
            print("Erro ao popular o banco de dados:", e)

if __name__ == '__main__':
    populate_database()
