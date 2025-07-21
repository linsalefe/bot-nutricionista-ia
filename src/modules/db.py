from tinydb import TinyDB, Query
import os

# Define o caminho do banco (pasta raiz, mas pode colocar em /data se preferir)
DB_PATH = os.path.join(os.path.dirname(__file__), '../../db.json')
db = TinyDB(DB_PATH)
User = Query()

# Função para criar ou atualizar usuário
def salvar_usuario(user_id, dados):
    # Atualiza se já existe, senão insere
    if db.search(User.user_id == user_id):
        db.update(dados, User.user_id == user_id)
    else:
        dados['user_id'] = user_id
        db.insert(dados)

# Função para buscar usuário
def buscar_usuario(user_id):
    result = db.search(User.user_id == user_id)
    return result[0] if result else None

# Função para adicionar refeição ao usuário
def adicionar_refeicao(user_id, refeicao):
    usuario = buscar_usuario(user_id)
    if usuario:
        if 'refeicoes' not in usuario:
            usuario['refeicoes'] = []
        usuario['refeicoes'].append(refeicao)
        db.update({'refeicoes': usuario['refeicoes']}, User.user_id == user_id)
    else:
        salvar_usuario(user_id, {'refeicoes': [refeicao]})

# Função para buscar histórico de refeições
def buscar_refeicoes(user_id):
    usuario = buscar_usuario(user_id)
    return usuario.get('refeicoes', []) if usuario else []
