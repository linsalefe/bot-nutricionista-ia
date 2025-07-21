from langchain.tools import BaseTool

class FoodImageAnalyzerTool(BaseTool):
    name: str = "food_image_analyzer"
    description: str = '''utilize essa ferramenta para analizar imagens de comida que o usuário enviar. Descreva os alimentos presentae e crie uma tabela nutricional da refeição
    o agente deve usar esta ferramenta sempre que um caminho de imagem for forncecido, mas somente quando o input for um caminho de imagem.
    '''
    
