import socket

# Configurações do servidor
SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Criando o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"✅ Servidor rodando em {SERVER_IP}:{SERVER_PORT}")

while True:
    # Recebe mensagem do cliente
    data, client_address = server_socket.recvfrom(BUFFER_SIZE)
    print(f"📩 Mensagem recebida de {client_address}: {data.decode()}")

    # Envia resposta ao cliente
    resposta = f"Mensagem recebida: {data.decode()}"
    server_socket.sendto(resposta.encode(), client_address)
