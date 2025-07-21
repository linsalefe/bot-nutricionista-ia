import openai
import base64
import imghdr

def analisar_imagem_gpt4o_bytes(img_bytes, openai_api_key):
    """
    Recebe bytes de uma imagem (jpeg/png/gif/webp), converte para base64
    e envia para o Vision.
    """
    fmt = imghdr.what(None, img_bytes)
    if fmt not in ["jpeg", "png", "gif", "webp"]:
        return "Formato de imagem não suportado."

    img_b64 = base64.b64encode(img_bytes).decode()

    prompt = (
    "Você é um nutricionista. Analise a imagem enviada, identifique os alimentos principais visíveis, "
    "estime a quantidade em gramas de cada item e faça uma análise nutricional para cada alimento. "
    "Responda neste formato conciso (em português):\n\n"
    "Arroz (100g): 130 kcal | 2.5g prot | 28g carb | 0.3g gord\n"
    "Feijão (100g): 95 kcal | 5g prot | 17g carb | 0.5g gord\n"
    "...\n"
    "Total: ... kcal | ...g prot | ...g carb | ...g gord\n\n"
    "Não explique nada além disso. Só liste os itens, os macros e o total."
)


    try:
        client = openai.OpenAI(api_key=openai_api_key)
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "O que tem nesse prato? Faça análise nutricional completa."},
                        {"type": "image_url", "image_url": {"url": f"data:image/{fmt};base64,{img_b64}"}}
                    ]
                }
            ],
            max_tokens=700,
            temperature=0.2
        )
        return resposta.choices[0].message.content
    except Exception as e:
        print(f"[image_analysis.py] Erro na análise de imagem com OpenAI: {e}")
        return "Não consegui analisar a imagem. Tente novamente com uma foto clara do prato!"

def analisar_imagem_gpt4o_base64(img_b64, openai_api_key):
    """Compat: Recebe base64, decodifica para bytes e repassa para a função principal."""
    img_bytes = base64.b64decode(img_b64)
    return analisar_imagem_gpt4o_bytes(img_bytes, openai_api_key)
