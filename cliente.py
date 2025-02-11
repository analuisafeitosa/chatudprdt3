import socket
import threading
import os
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nome_usuario = input("Digite seu nome: ")
client_socket.sendto(f"hi, meu nome eh {nome_usuario}".encode(), (SERVER_IP, SERVER_PORT))

def receive_messages():
    """Recebe mensagens do servidor e exibe no terminal."""
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            print(data.decode())
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

while True:
    mensagem = input()
    if mensagem.lower() == "bye":
        client_socket.sendto("bye".encode(), (SERVER_IP, SERVER_PORT))
        print("👋 Saindo do chat...")
        break
    
    # Criar arquivo temporário para envio
    with open("mensagem.txt", "w", encoding="utf-8") as file:
        file.write(mensagem)
    
    # Ler e enviar fragmentado
    with open("mensagem.txt", "r", encoding="utf-8") as file:
        while True:
            chunk = file.read(BUFFER_SIZE)
            if not chunk:
                break
            client_socket.sendto(chunk.encode(), (SERVER_IP, SERVER_PORT))
    
    os.remove("mensagem.txt")

client_socket.close()