import socket
import os
import queue
import math
import threading
import struct
import time

# Configuração do Servidor
clients = []
messages = queue.Queue()
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 7777))

# Armazenamento de fragmentos recebidos
lista_fragmentos = []
contador_fragmentos = 0

# Variável relacionada ao RDT 3.0
timeout = 2  # Timeout de 2 segundos

# Função que faz o cálculo do Checksum
def calcula_checksum(data):
    # Converte os dados de bytes para uma sequência binária de bits
    bits = bin(int.from_bytes(data, byteorder='big'))[2:]

    # Garante que o número de bits seja múltiplo de 8, preenchendo à esquerda com zeros
    if len(bits) % 8 != 0:
        bits = '0' * (8 - len(bits) % 8) + bits

    slice_length = 8
    # Divide a mensagem em blocos de 8 bits
    blocos = [bits[i:i+slice_length] for i in range(0, len(bits), slice_length)]
    
    # Soma todos os blocos convertidos para inteiro
    total = sum(int(b, 2) for b in blocos)
    total_bin = bin(total)[2:]

    # Tratamento de overflow (soma os bits excedentes)
    if len(total_bin) > slice_length:
        overflow = len(total_bin) - slice_length
        total = int(total_bin[:overflow], 2) + int(total_bin[overflow:], 2)
        total_bin = bin(total)[2:]

    # Preenche com zeros à esquerda se necessário
    total_bin = total_bin.zfill(slice_length)

    # Calcula o complemento de 1 (inversão dos bits)
    checksum = ''.join('0' if bit == '1' else '1' for bit in total_bin)

    # Converte o checksum binário para inteiro
    return int(checksum, 2)

# Função que cria fragmentos
def gerar_fragmento(dados, tamanho_fragmento, indice_fragmento, total_fragmentos):
    data = dados[:tamanho_fragmento]
    checksum = calcula_checksum(data)
    header = struct.pack('!IIII', tamanho_fragmento, indice_fragmento, total_fragmentos, checksum)
    print(f"[ENVIO] Checksum gerado: {checksum} (Fragmento {indice_fragmento + 1}/{total_fragmentos})")

    return header + data

# Função para enviar ACK
def envia_ack(addr):
    ack_packet = struct.pack('!I', 1)
    server.sendto(ack_packet, addr)
    print(f'ACK enviado com sucesso para {addr}')

# Verificação da integridade dos dados recebidos por meio de desempacotamento e reagrupação
def reconstruir_mensagem(data, addr):
    global contador_fragmentos, lista_fragmentos

    header = data[:16]
    message_in_bytes = data[16:]
    tamanho_fragmento, indice_fragmento, total_fragmentos, checksum = struct.unpack('!IIII', header)  # Desempacota o cabeçalho 

    # Exibe os valores de checksum para comparação
    print(f"[RECEPÇÃO] Checksum recebido: {checksum}")
    print(f"[RECEPÇÃO] Checksum calculado: {calcula_checksum(message_in_bytes)}")

    # Verificar o Checksum
    checksum_calculado = calcula_checksum(message_in_bytes)
    if checksum != checksum_calculado:
        print(f"Fragmento com checksum inválido, ignorando.\nEsperado: {checksum},\nCalculado: {checksum_calculado}")
        return

    if len(lista_fragmentos) < total_fragmentos:
        add = total_fragmentos - len(lista_fragmentos)
        lista_fragmentos.extend([None] * add)
    lista_fragmentos[indice_fragmento] = message_in_bytes
    contador_fragmentos += 1
    if contador_fragmentos == total_fragmentos:
        with open('received_message.txt', 'wb') as file:
            for fragment in lista_fragmentos:
                file.write(fragment)
        contador_fragmentos = 0
        lista_fragmentos = []
        processar_mensagem_recebida(addr)
    elif (contador_fragmentos < total_fragmentos) and (indice_fragmento == total_fragmentos - 1):
        print("Possível perda de pacotes detectada!")
        contador_fragmentos = 0
        lista_fragmentos = []

    # Envia ACK após receber o fragmento
    envia_ack(addr)

# Processa a mensagem e a trata caso seja uma confirmação de Login, Log out ou apenas uma mensagem qualquer
def processar_mensagem_recebida(addr):
    with open('received_message.txt', 'r') as file:
        file_content = file.read()
    os.remove('received_message.txt')
    for line in file_content.strip().split('\n'):
        line = line.strip()
        if "SIGNUP_TAG:" in line: #Login
            name = line.split(":")[1]
            sent_msg = f"{name} entrou na sala"
            messages.put(sent_msg)
        elif "SIGNOUT_TAG:" in line: #Log out
            name = line.split(":")[1]
            sent_msg = f"{name} saiu da sala"
            print(f"{addr} saiu da sala")
            clients.remove(addr)  # Remove o cliente da lista de clientes
            messages.put(sent_msg)
        else:
            messages.put(line)
            print(f"Mensagem recebida de {addr} processada.")
    enviar_para_todos(addr)


def envia_fragmento(fragment, addr):
    ack_event = threading.Event()
    ack_received = False # Variável para verificar se o ACK foi recebido
    print(f"\nMensagem enviada para {addr}\n")
    
    def receive_ack():
        nonlocal ack_received
        while not ack_event.is_set():
            try:
                data, address = server.recvfrom(1024)
                header = data[:16]
                message_type = struct.unpack('!I', header[:4])[0]
                if message_type == 1:  # ACK
                    ack_received = True # Marca que o ACK foi recebido com sucesso
                    ack_event.set()
                    print(f'ACK recebido com sucesso {address}')
            except socket.timeout:
                continue

    # Configurar timeout e thread para receber ACK
    server.settimeout(timeout)
    ack_thread = threading.Thread(target=receive_ack)
    ack_thread.start()

    while not ack_event.is_set():  # Enquanto não receber ACK, reenvia a mensagem
        server.sendto(fragment, addr)
        ack_event.wait(timeout)  # Espera até o timeout ou receber o ACK

    ack_thread.join()  # Garante que a thread de ACK finalize
    server.settimeout(None)  # Remove o timeout

# Faz o broadcast da mensagem para os clientes
def enviar_para_todos(sender_addr):

    tamanho_fragmento = 1008

    while not messages.empty():
        message = messages.get()
        with open('message_server.txt', 'w') as file:
            file.write(message)
        with open('message_server.txt', 'rb') as file:
            dados = file.read()
            total_fragmentos = math.ceil(len(dados) / tamanho_fragmento)
            for client in clients:
                if client != sender_addr:  # Evitar enviar para o remetente original
                    fragment_dados = dados
                    fragment_index = 0
                    while fragment_dados:
                        fragment = gerar_fragmento(fragment_dados, tamanho_fragmento, fragment_index, total_fragmentos)
                        envia_fragmento(fragment, client)
                        fragment_dados = fragment_dados[tamanho_fragmento:]
                        fragment_index += 1
        os.remove('message_server.txt')

# Função de receber dados
def receive():
    while True:
        data, addr = server.recvfrom(1024)
        print("\nMensagem recebida\n")
        if addr not in clients:
            clients.append(addr)
            print(f"Lista de clientes atualizada: {clients}")
        header = data[:16]
        message_type = struct.unpack('!I', header[:4])[0]

        # Se a mensagem recebida for um ACK, não faz nada (será tratado em outra parte)
        if message_type == 1:
            continue
        # Se a mensagem recebida NÃO for um ACK: Trata a mensagem
        else:
            reconstruir_mensagem(data, addr)

thread = threading.Thread(target=receive)
thread.start()
