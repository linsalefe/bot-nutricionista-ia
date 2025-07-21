import re

def limpar_texto(texto):
    # Remove espaços extras, pontuação irrelevante, etc.
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto
def identificar_intencao(texto):
    texto = limpar_texto(texto)
    if any(palavra in texto for palavra in ['refeição', 'comi', 'almocei', 'jantei']):
        return 'registrar_refeicao'
    elif any(palavra in texto for palavra in ['meta', 'objetivo']):
        return 'definir_meta'
    elif any(palavra in texto for palavra in ['sugestão', 'o que comer', 'recomendação']):
        return 'sugestao_refeicao'
    elif any(palavra in texto for palavra in ['caloria', 'quanto comi']):
        return 'consultar_calorias'
    else:
        return 'outro'
    
def extrair_alimento(texto):
    texto = limpar_texto(texto)
    # Muito simples, para evoluir depois
    for alimento in ['banana', 'ovo', 'maçã', 'pão', 'arroz', 'frango']:
        if alimento in texto:
            return alimento
    return None

def extrair_meta(texto):
    texto = limpar_texto(texto)
    # Exemplo: "minha meta é emagrecer 5kg"
    match = re.search(r'(emagrecer|ganhar)\s*(\d+)\s*kg', texto)
    if match:
        return {'tipo': match.group(1), 'quantidade': int(match.group(2))}
    return None

if __name__ == "__main__":
    exemplos = [
        "Acabei de almoçar arroz e frango.",
        "Qual a melhor sugestão de refeição para hoje?",
        "Minha meta é emagrecer 5kg.",
        "Quero saber quantas calorias já comi.",
        "Oi, tudo bem?"
    ]

    for frase in exemplos:
        print(f"Input: {frase}")
        print("  Intenção:", identificar_intencao(frase))
        print("  Alimento:", extrair_alimento(frase))
        print("  Meta:", extrair_meta(frase))
        print()


