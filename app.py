from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados.db'
db = SQLAlchemy(app)

# Modelo para a tabela de dados
class Dados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    contrato = db.Column(db.String(20), nullable=True)
    assessor_descricao = db.Column(db.String(100), nullable=True)
    produto_descricao = db.Column(db.String(100), nullable=True)
    tabela_descricao = db.Column(db.String(100), nullable=True)
    status_descricao = db.Column(db.String(100), nullable=True)
    data_lancamento = db.Column(db.String(20), nullable=True)
    valor_emprestimo = db.Column(db.Float, nullable=True)
    valor_parcelas = db.Column(db.Float, nullable=True)
    numero_parcelas = db.Column(db.Integer, nullable=True)
    tipo_midia_descricao = db.Column(db.String(100), nullable=True)
    banco_descricao = db.Column(db.String(100), nullable=True)
    banco_ispb = db.Column(db.String(20), nullable=True)

# Função para atualizar os dados a partir do JSON
def atualizar_dados():
    url = "https://rncreditos.panoramaemprestimos.com.br/html.do?action=exportarLayout&saida=json&chaveExportacao=14182006000131&layout=51&dias=7&"
    response = requests.get(url)
    data = response.json()

    for item in data:
        cpf = item.get('Cliente.Cpf')
        dado_existente = Dados.query.filter_by(cpf=cpf).first()

        if not dado_existente:
            novo_dado = Dados(
                nome=item.get('Cliente.Nome'),
                cpf=cpf,
                contrato=item.get('Contrato'),
                assessor_descricao=item.get('assessor.estabelecimento.descricao'),
                produto_descricao=item.get('Produto.Descricao'),
                tabela_descricao=item.get('Tabela.Descricao'),
                status_descricao=item.get('tarefaExecucao.status.status.descricao'),
                data_lancamento=item.get('DataLancamento'),
                valor_emprestimo=float(item.get('Valoremprestimo', 0)),
                valor_parcelas=float(item.get('Valorparcelas', 0)),
                numero_parcelas=int(item.get('Numeroparcelas', 0)),
                tipo_midia_descricao=item.get('TipoMidia.Descricao'),
                banco_descricao=item.get('Banco.Descricao'),
                banco_ispb=item.get('Banco.Ispb')
            )
            db.session.add(novo_dado)
        db.session.commit()

# Rota para visualizar os dados em formato HTML
@app.route('/visualizar_dados')
def visualizar_dados():
    atualizar_dados()  # Atualiza os dados antes de exibir
    dados = Dados.query.all()
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visualizar Dados</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            th, td {
                padding: 10px;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <h1>Dados Cadastrados</h1>
        <table>
            <tr>
                <th>Nome</th>
                <th>CPF</th>
                <th>Contrato</th>
                <th>Assessor</th>
                <th>Produto</th>
                <th>Tabela</th>
                <th>Status</th>
                <th>Data de Lançamento</th>
                <th>Valor do Empréstimo</th>
                <th>Valor das Parcelas</th>
                <th>Número de Parcelas</th>
                <th>Tipo de Mídia</th>
                <th>Banco</th>
                <th>ISPB do Banco</th>
            </tr>
            {% for dado in dados %}
            <tr>
                <td>{{ dado.nome }}</td>
                <td>{{ dado.cpf }}</td>
                <td>{{ dado.contrato }}</td>
                <td>{{ dado.assessor_descricao }}</td>
                <td>{{ dado.produto_descricao }}</td>
                <td>{{ dado.tabela_descricao }}</td>
                <td>{{ dado.status_descricao }}</td>
                <td>{{ dado.data_lancamento }}</td>
                <td>{{ dado.valor_emprestimo }}</td>
                <td>{{ dado.valor_parcelas }}</td>
                <td>{{ dado.numero_parcelas }}</td>
                <td>{{ dado.tipo_midia_descricao }}</td>
                <td>{{ dado.banco_descricao }}</td>
                <td>{{ dado.banco_ispb }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''
    return render_template_string(html_template, dados=dados)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Recria o banco de dados com o esquema atualizado
    app.run(debug=True)
