from dotenv import load_dotenv
import os
import openai
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from modules import db

# Carregar variáveis de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print("Chave OpenAI carregada? ", bool(api_key))

# Função usando OpenAI puro
def perguntar_openai(prompt):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Função usando LangChain
def perguntar_langchain(pergunta):
    llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um nutricionista virtual."),
        ("user", "{pergunta}")
    ])
    chain = LLMChain(llm=llm, prompt=prompt)
    resposta = chain.invoke({"pergunta": pergunta})
    return resposta["text"]

def testar_ia_e_db():
    print("\n[OpenAI API puro]:")
    resposta1 = perguntar_openai("Me diga um alimento saudável para o café da manhã.")
    print(resposta1)

    print("\n[LangChain]:")
    resposta2 = perguntar_langchain("Quais os melhores alimentos para dar energia?")
    print(resposta2)

    print("\n[Teste TinyDB - salvar usuário]")
    db.salvar_usuario('123', {'nome': 'Álefe', 'meta': 'Emagrecer 5kg'})
    print("Usuário salvo!")

    print("\n[Teste TinyDB - adicionar refeições]")
    db.adicionar_refeicao('123', {'data': '2024-07-18', 'alimento': 'Ovo', 'calorias': 70})
    db.adicionar_refeicao('123', {'data': '2024-07-18', 'alimento': 'Banana', 'calorias': 90})

if __name__ == "__main__":
    # Para rodar os testes de IA e banco, descomente a linha abaixo:
    # testar_ia_e_db()

    # Para rodar o bot Telegram, descomente a linha abaixo:
    from modules.bot_telegram import start_bot
    start_bot()
