import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging

# Importa seu analisador de imagem com OpenAI GPT-4o
from src.modules import image_analysis


# (Opcional) IA conversacional, com contexto, usando LangChain + OpenAI GPT-3.5/4
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
WPP_TOKEN = os.getenv("WPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ianutri2024")

required_vars = {
    'WPP_TOKEN': WPP_TOKEN,
    'PHONE_NUMBER_ID': PHONE_NUMBER_ID,
    'OPENAI_API_KEY': OPENAI_API_KEY
}
missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    logger.error(f"❌ Variáveis de ambiente obrigatórias não encontradas: {missing_vars}")
    exit(1)

app = Flask(__name__)

# --- Inteligência Artificial Conversacional (LangChain + OpenAI) ---
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.3)
memorias = {}  # Memória por usuário (para conversas contextualizadas)

def resposta_ia(usuario_id, mensagem):
    if usuario_id not in memorias:
        memorias[usuario_id] = ConversationBufferMemory()
    chain = ConversationChain(llm=llm, memory=memorias[usuario_id])
    return chain.predict(input=mensagem)

# --- Função para baixar imagem enviada pelo WhatsApp (oficial Meta API) ---
def baixar_imagem_meta(media_id, access_token):
    # Passo 1: Obter a URL da mídia
    url_info = f"https://graph.facebook.com/v19.0/{media_id}"
    params = {'access_token': access_token}
    resp = requests.get(url_info, params=params, timeout=30)
    resp.raise_for_status()
    image_url = resp.json()['url']
    # Passo 2: Baixar imagem
    headers = {'Authorization': f'Bearer {access_token}'}
    img_resp = requests.get(image_url, headers=headers, timeout=30)
    img_resp.raise_for_status()
    return img_resp.content

# --- Função para enviar mensagem de texto para o usuário pelo WhatsApp ---
def send_whatsapp_message_meta(phone_number_id, to, message, access_token):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    resp = requests.post(url, json=data, headers=headers, timeout=15)
    resp.raise_for_status()
    logger.info(f"Mensagem enviada para {to}: {message}")
    return resp.json()

# --- WEBHOOK ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Validação do Webhook
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == VERIFY_TOKEN:
            return challenge, 200
        return 'Token inválido', 403

    if request.method == 'POST':
        data = request.get_json()
        logger.info(f"Webhook recebido: {data}")
        try:
            entry = data['entry'][0]
            changes = entry['changes'][0]['value']
            messages = changes.get('messages')
            if not messages:
                return 'ok', 200

            message = messages[0]
            msg_type = message['type']
            from_number = message['from']

            # --- TEXTO ---
            if msg_type == "text":
                texto = message['text']['body']
                resposta = resposta_ia(from_number, texto)
                send_whatsapp_message_meta(PHONE_NUMBER_ID, from_number, resposta, WPP_TOKEN)

            # --- IMAGEM ---
            elif msg_type == "image":
                try:
                    media_id = message['image']['id']
                    img_bytes = baixar_imagem_meta(media_id, WPP_TOKEN)
                    resposta = image_analysis.analisar_imagem_gpt4o_bytes(img_bytes, OPENAI_API_KEY)
                except Exception as ex:
                    resposta = "Não consegui analisar sua imagem. Tente novamente ou envie uma foto mais clara do prato!"
                    logger.error(f"Erro na análise de imagem: {ex}")
                send_whatsapp_message_meta(PHONE_NUMBER_ID, from_number, resposta, WPP_TOKEN)

            # Você pode adicionar outros tipos de mensagem (áudio, documentos etc) se quiser

        except Exception as e:
            logger.error(f"Erro no webhook: {e}")
        return 'ok', 200

# --- Healthcheck ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=5000, debug=True)
