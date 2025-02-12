import socket
import threading

# Configurações do cliente
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024  # Tamanho fixo do buffer

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nome_usuario = input("Digite seu nome: ")
client_socket.sendto(f"hi, meu nome eh {nome_usuario}".encode(), (SERVER_IP, SERVER_PORT))

def receive_messages():
    """Recebe mensagens do servidor e exibe no terminal."""
    mensagens_pendentes = {}  # Dicionário para armazenar fragmentos de mensagens
    
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            mensagem = data.decode()
            
            if mensagem == "FIM_MENSAGEM":
                # Reconstruir a mensagem completa
                if mensagens_pendentes:
                    fragmentos = list(mensagens_pendentes.values())
                    mensagem_completa = "".join(fragmentos)
                    print(mensagem_completa)  # Exibe a mensagem reconstruída
                    mensagens_pendentes.clear()  # Limpa os fragmentos após reconstruir a mensagem
                continue
            
            if "/" in mensagem and ":" in mensagem:
                try:
                    indice, conteudo = mensagem.split(":", 1)
                    posicao, total = indice.split("/")
                    posicao = int(posicao)
                    total = int(total)
                    
                    # Armazena o fragmento no dicionário
                    mensagens_pendentes[posicao] = conteudo
                    print(f"Fragmento recebido: {mensagem}")  # Log para depuração
                except (ValueError, IndexError) as e:
                    print(f"Erro ao processar fragmento: {e}")
        
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break

def fragmentar_mensagem(mensagem):
    """Fragmenta a mensagem em pedaços menores que BUFFER_SIZE, considerando o cabeçalho."""
    fragmentos = []
    tamanho_max_fragmento = BUFFER_SIZE - 20  # Reserva espaço para o cabeçalho (ex: "0/100:")
    total_fragmentos = (len(mensagem) // tamanho_max_fragmento) + 1  # Calcula o total de fragmentos
    
    for i in range(0, len(mensagem), tamanho_max_fragmento):
        fragmento = mensagem[i:i + tamanho_max_fragmento]
        fragmentos.append(fragmento)
        print(f"Fragmento {i}: {fragmento}")  # Log para depuração
    
    return fragmentos, total_fragmentos

# Inicia a thread para receber mensagens
threading.Thread(target=receive_messages, daemon=True).start()

while True:
    try:
        mensagem = input()
        if mensagem.lower() == "bye":
            client_socket.sendto("bye".encode(), (SERVER_IP, SERVER_PORT))
            print("👋 Saindo do chat...")
            break
        
        fragmentos, total_fragmentos = fragmentar_mensagem(mensagem)
        
        for i, fragmento in enumerate(fragmentos):
            pacote = f"{i}/{total_fragmentos}:{fragmento}"
            print(f"Enviando fragmento: {pacote}")  # Log para depuração
            client_socket.sendto(pacote.encode(), (SERVER_IP, SERVER_PORT))
        
        # Indicador de fim da mensagem
        client_socket.sendto("FIM_MENSAGEM".encode(), (SERVER_IP, SERVER_PORT))
    
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        break

client_socket.close()