import socket
import threading
import os
from datetime import datetime

# Configurações do servidor
SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Lista de clientes conectados
clientes = {}

# Criando o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"✅ Servidor rodando em {SERVER_IP}:{SERVER_PORT}")

def broadcast(mensagem, remetente):
    """Envia a mensagem para todos os clientes conectados, exceto o remetente."""
    for cliente, nome in clientes.items():
        if cliente != remetente:
            server_socket.sendto(mensagem.encode(), cliente)

def handle_client():
    """Gerencia a recepção de mensagens dos clientes."""
    while True:
        try:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            mensagem = data.decode()
            
            if mensagem.startswith("hi, meu nome eh"):
                nome_usuario = mensagem.split(" ")[-1]
                clientes[client_address] = nome_usuario
                print(f"👤 {nome_usuario} ({client_address}) entrou na sala")
                broadcast(f"{nome_usuario} entrou na sala", client_address)
                continue
            
            if mensagem.lower() == "bye":
                nome_usuario = clientes.pop(client_address, "Usuário desconhecido")
                print(f"🚪 {nome_usuario} ({client_address}) saiu da sala")
                broadcast(f"{nome_usuario} saiu da sala", client_address)
                continue
            
            nome_usuario = clientes.get(client_address, "Desconhecido")
            timestamp = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            mensagem_formatada = f"{client_address[0]}:{client_address[1]}/~{nome_usuario}: {mensagem} {timestamp}"
            print(mensagem_formatada)
            broadcast(mensagem_formatada, client_address)
        
        except Exception as e:
            print(f"Erro: {e}")
            continue

# Inicia a thread do servidor
threading.Thread(target=handle_client, daemon=True).start()

while True:
    pass  # Mantém o servidor rodando