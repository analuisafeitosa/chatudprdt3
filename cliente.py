import socket

SERVER_IP = "127.0.0.1"  # IP do servidor
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Criando socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Nome do usuário
nome_usuario = input("Digite seu nome: ")
print(f"🟢 Conectado ao chat como {nome_usuario}")

while True:
    mensagem = input("> ")  # Usuário digita a mensagem
    if mensagem.lower() == "bye":
        print("👋 Saindo do chat...")
        break
    
    # Enviar mensagem para o servidor
    client_socket.sendto(f"{nome_usuario}: {mensagem}".encode(), (SERVER_IP, SERVER_PORT))

    # Receber resposta do servidor
    data, _ = client_socket.recvfrom(BUFFER_SIZE)
    print(f"📨 {data.decode()}")

client_socket.close()
