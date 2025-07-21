import os
from pyrogram import Client, filters
from modules import nlp, db

def start_bot():
    app = Client(
        "nutricionista_bot",
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        api_id=int(os.getenv("TELEGRAM_API_ID")),
        api_hash=os.getenv("TELEGRAM_API_HASH")
    )

    @app.on_message(filters.command("start"))
    def start(client, message):
        message.reply("Olá! Eu sou seu nutricionista virtual. Me conte sua meta ou registre uma refeição!")

    @app.on_message(filters.text & ~filters.command("start"))
    def responder(client, message):
        texto = message.text
        user_id = str(message.from_user.id)
        intencao = nlp.identificar_intencao(texto)

        if intencao == 'registrar_refeicao':
            alimento = nlp.extrair_alimento(texto)
            if alimento:
                db.adicionar_refeicao(user_id, {'alimento': alimento, 'data': 'hoje'})
                message.reply(f"Refeição registrada: {alimento}!")
            else:
                message.reply("Qual foi o alimento? Não consegui identificar. Exemplo: 'Comi banana'.")
        elif intencao == 'definir_meta':
            meta = nlp.extrair_meta(texto)
            if meta:
                db.salvar_usuario(user_id, {'meta': meta})
                message.reply(f"Meta registrada: {meta['tipo']} {meta['quantidade']}kg!")
            else:
                message.reply("Por favor, informe sua meta de forma clara. Ex: 'Minha meta é emagrecer 5kg'.")
        elif intencao == 'sugestao_refeicao':
            message.reply("Sugestão: consuma ovos mexidos com aveia no café da manhã!")
        elif intencao == 'consultar_calorias':
            refeicoes = db.buscar_refeicoes(user_id)
            if refeicoes:
                total = sum([r.get('calorias', 0) for r in refeicoes])
                message.reply(f"Você consumiu {total} calorias registradas até agora.")
            else:
                message.reply("Nenhuma refeição registrada ainda!")
        else:
            message.reply("Desculpe, não entendi. Pode reformular?")

    print("Bot rodando! Envie /start no Telegram.")
    app.run()
