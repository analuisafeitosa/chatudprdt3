import socket
import threading
from datetime import datetime

# Configurações do servidor
SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345
BUFFER_SIZE = 1024  # Tamanho fixo do buffer

# Lista de clientes conectados
clientes = {}
mensagens_pendentes = {}

# Criando o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"✅ Servidor rodando em {SERVER_IP}:{SERVER_PORT}")

def fragmentar_mensagem(mensagem):
    """Fragmenta a mensagem em pedaços menores que BUFFER_SIZE, considerando o cabeçalho."""
    fragmentos = []
    tamanho_max_fragmento = BUFFER_SIZE - 20  # Reserva espaço para o cabeçalho (ex: "0/100:")
    total_fragmentos = (len(mensagem)) // tamanho_max_fragmento + 1  # Calcula o total de fragmentos
    
    for i in range(0, len(mensagem), tamanho_max_fragmento):
        fragmento = mensagem[i:i + tamanho_max_fragmento]
        fragmentos.append(fragmento)
        print(f"Fragmento {i}: {fragmento}")  # Log para depuração
    
    return fragmentos, total_fragmentos

def broadcast(mensagem, remetente):
    """Envia a mensagem fragmentada para todos os clientes conectados, exceto o remetente."""
    fragmentos, total_fragmentos = fragmentar_mensagem(mensagem)
    
    for cliente, nome in clientes.items():
        if cliente != remetente:
            try:
                for i, fragmento in enumerate(fragmentos):
                    pacote = f"{i}/{total_fragmentos}:{fragmento}"
                    server_socket.sendto(pacote.encode(), cliente)
                    print(f"Enviando fragmento para {nome}: {pacote}")  # Log para depuração
                
                # Indicador de fim da mensagem
                server_socket.sendto("FIM_MENSAGEM".encode(), cliente)
            except Exception as e:
                print(f"Erro ao enviar para {nome}: {e}")

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
            
            if mensagem == "FIM_MENSAGEM":
                if client_address in mensagens_pendentes:
                    fragmentos = mensagens_pendentes.pop(client_address, [])
                    mensagem_completa = "".join(fragmentos)
                    print(f"Mensagem reconstruída: {mensagem_completa}")  # Log para depuração
                    nome_usuario = clientes.get(client_address, "Desconhecido")
                    timestamp = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                    mensagem_formatada = f"{nome_usuario}: {mensagem_completa} ({timestamp})"
                    broadcast(mensagem_formatada, client_address)
                continue
            
            if "/" in mensagem and ":" in mensagem:
                try:
                    indice, conteudo = mensagem.split(":", 1)
                    posicao, total = indice.split("/")
                    posicao = int(posicao)
                    total = int(total)
                    
                    if client_address not in mensagens_pendentes:
                        mensagens_pendentes[client_address] = [""] * total
                    
                    mensagens_pendentes[client_address][posicao] = conteudo
                    print(f"Fragmento recebido de {client_address}: {mensagem}")  # Log para depuração
                except (ValueError, IndexError) as e:
                    print(f"Erro ao processar fragmento: {e}")
        
        except Exception as e:
            print(f"Erro: {e}")
            continue

# Inicia a thread do servidor
threading.Thread(target=handle_client, daemon=True).start()

while True:
    pass  # Mantém o servidor rodando