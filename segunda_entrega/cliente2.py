import random
import threading
import socket
import struct
import time
import os
import math
from datetime import datetime

# Configuração do Cliente 
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9000)))

# Lista para armazenar fragmentos recebidos
lista_fragmentos = []
contador_fragmentos = 0

# Variáveis relacionadas ao RDT 3.0
timeout = 2  # Timeout de 2 segundos
flag_recebimento_ack = False
lock = threading.Lock()

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

    # Converte o checksum binário para inteiro para facilitar a conferencia
    return int(checksum, 2)


# Função para verificar se recebeu ACK
def ack_recebido():
    global flag_recebimento_ack
    flag_recebimento_ack = True

# Verificação da integridade dos dados recebidos por meio de desempacotamento e reagrupação
def reconstruir_mensagem(data):
    global contador_fragmentos, lista_fragmentos

    header = data[:16]
    message_in_bytes = data[16:]
    tamanho_fragmento, indice_fragmento, total_fragmentos, checksum = struct.unpack('!IIII', header)

    if len(lista_fragmentos) < total_fragmentos:
        add = total_fragmentos - len(lista_fragmentos)
        lista_fragmentos.extend([None] * add)
    lista_fragmentos[indice_fragmento] = message_in_bytes  # Armazena o fragmento na lista na posição correta
    contador_fragmentos += 1

    # Envia ACK após receber o fragmento
    envia_ack()

    
    # Verifica se todos os fragmentos do pacote foram recebidos corretamente e, caso contrário, identifica a perda de pacotes. 
    # Em seguida, reinicia a lista de fragmentos para processar o próximo pacote.
    if contador_fragmentos == total_fragmentos:
        with open('received_message.txt', 'wb') as file:
            for fragmento in lista_fragmentos:
                file.write(fragmento)
        contador_fragmentos = 0
        lista_fragmentos = []
        exibir_mensagem_recebida()
    elif (contador_fragmentos < total_fragmentos) and (indice_fragmento == total_fragmentos - 1):
        print("Possível perda de pacotes detectada!")
        contador_fragmentos = 0
        lista_fragmentos = []

# Lê o arquivo txt e printa a mensagem
def exibir_mensagem_recebida():
    with open('received_message.txt', 'r') as file:
        file_content = file.read()
    print(file_content)

# Função para enviar ACK
def envia_ack():
    ack_packet = struct.pack('!I', 1)
    client.sendto(ack_packet, ('localhost', 7777))


# Função que trata o recebimento da mensagem
def receive():
    global flag_recebimento_ack
    while True:
        data, addr = client.recvfrom(1024)
        header = data[:16]
        message_type = struct.unpack('!I', header[:4])[0]

        # Se a mensagem recebida for um ACK, altera a flag de ACK para True
        if message_type == 1:  # ACK
            flag_recebimento_ack = True
        # Se a mensagem recebida NÃO for um ACK: Trata a mensagem
        else:
            reconstruir_mensagem(data)

thread1 = threading.Thread(target=receive)
thread1.start()

# Cria um fragmento
def gerar_fragmento(dados, tamanho_fragmento, indice_fragmento, total_fragmentos):
    data = dados[:tamanho_fragmento]
    checksum = calcula_checksum(data)
    header = struct.pack('!IIII', tamanho_fragmento, indice_fragmento, total_fragmentos, checksum)

    return header + data

def envia_fragmento(fragmento, addr):
    global flag_recebimento_ack
    flag_recebimento_ack = False
    # Loop de ACK
    while not flag_recebimento_ack:  # Enquanto a função "ACK Received" não indicar true, continuará ocorrendo o reenvio da mensagem
        client.sendto(fragmento, addr)
        start = time.time()
        while time.time() - start < timeout:
            if flag_recebimento_ack: # Aqui definimos finalmente que quando indicar true o processo de reenvio seja interrompido
                break

def main():
    username = ''
    # Loop principal, aqui ocorrerá a interação do usuário com o código
    while True:
        message = input("")
        # Trata o login ideal do usuário
        if message.startswith("oi, meu nome eh") or message.startswith("Oi, meu nome eh"):
            username = message[len("oi, meu nome eh") + 1:].strip()
            sent_msg = f"SIGNUP_TAG:{username}"
            if username.strip() == "": #Checagem se é um username válido
                print("Você precisa se conectar primeiro digitando 'Oi, meu nome eh' seguido do seu nome.")
            else:
                with open('message_client.txt', 'w') as file:
                    file.write(sent_msg)
                enviar_txt()
                print(f"Usuário {username}, você está conectado.")
        # Trata a saída do usuário
        elif username and message == "tchau":
            sent_msg = f"SIGNOUT_TAG:{username}"
            with open('message_client.txt', 'w') as file:
                file.write(sent_msg)
            enviar_txt()
            print("Você saiu do chat. Até logo!")
            exit()  # Encerra a conexão
        
        # Trata a mensagem do usuário
        else:
            if username:
                timestamp = datetime.now().strftime('%H:%M:%S - %d/%m/%Y')
                formatted_message = f"{client.getsockname()[0]}:{client.getsockname()[1]}/~{username}: {message} {timestamp}"
                with open('message_client.txt', 'w') as file:
                    file.write(formatted_message)
                enviar_txt()
            else:
                print("Você precisa se conectar primeiro digitando 'Oi, meu nome eh' seguido do seu nome.") # Aqui também garantimos que o cliente possui um username válido

# Função que manda a mensagem
def enviar_txt():
    indice_fragmento = 0
    tamanho_fragmento = 1008
    with open('message_client.txt', 'rb') as file:
        dados = file.read()
        total_fragmentos = math.ceil(len(dados) / tamanho_fragmento)  # Calcula o número de fragmentos
        while dados:
            fragmento = gerar_fragmento(dados, tamanho_fragmento, indice_fragmento, total_fragmentos)
            envia_fragmento(fragmento, ('localhost', 7777))
            dados = dados[tamanho_fragmento:]
            indice_fragmento += 1
    os.remove('message_client.txt')

main()
