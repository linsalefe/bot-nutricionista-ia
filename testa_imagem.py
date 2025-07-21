import imghdr

with open("imagem_baixada_teste.jpg", "rb") as f:
    img_bytes = f.read()
print(imghdr.what(None, img_bytes))  # Deve mostrar 'jpeg', 'png', etc ou None
