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

def fragmentar_mensagem(mensagem):
    """Fragmenta a mensagem em pedaços de tamanho BUFFER_SIZE."""
    fragmentos = []
    for i in range(0, len(mensagem), BUFFER_SIZE - 10):  # Reservando espaço para cabeçalho
        fragmento = mensagem[i:i + BUFFER_SIZE - 10]
        fragmentos.append(fragmento)
    return fragmentos

threading.Thread(target=receive_messages, daemon=True).start()

while True:
    mensagem = input()
    if mensagem.lower() == "bye":
        client_socket.sendto("bye".encode(), (SERVER_IP, SERVER_PORT))
        print("👋 Saindo do chat...")
        break
    
    fragmentos = fragmentar_mensagem(mensagem)
    
    for i, fragmento in enumerate(fragmentos):
        pacote = f"{i}/{len(fragmentos)}:{fragmento}"
        client_socket.sendto(pacote.encode(), (SERVER_IP, SERVER_PORT))
    
    # Indicador de fim da mensagem
    client_socket.sendto("FIM_MENSAGEM".encode(), (SERVER_IP, SERVER_PORT))

client_socket.close()
