import socket
import threading
import struct
import os
import math
import random
from zlib import crc32
from datetime import datetime

# Configuração do Cliente
cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cliente.bind(("localhost", random.randint(8000, 9000)))  # Porta aleatória para o cliente

# Lista para armazenar fragmentos recebidos
lista_fragmentos = []
contador_fragmentos = 0

# Função para criar fragmentos
def gerar_fragmento(dados, tamanho_fragmento, indice_fragmento, total_fragmentos):
    
    #Divide a mensagem em fragmentos e adiciona um cabeçalho com informações para reagrupamento.
    
    parte_dados = dados[:tamanho_fragmento]
    checksum = crc32(parte_dados)
    cabecalho = struct.pack('!IIII', tamanho_fragmento, indice_fragmento, total_fragmentos, checksum)
    return cabecalho + parte_dados

# Função para reconstruir a mensagem original
def reconstruir_mensagem(dados_recebidos):
    
    #Junta os fragmentos recebidos e verifica a integridade pelo checksum (CRC32).
    
    global contador_fragmentos, lista_fragmentos
    cabecalho = dados_recebidos[:16]
    corpo_mensagem = dados_recebidos[16:]
    tamanho, indice, total, checksum = struct.unpack('!IIII', cabecalho)
   
    if checksum != crc32(corpo_mensagem):
        print("Fragmento corrompido, ignorando...")
        return
   
    if len(lista_fragmentos) < total:
        lista_fragmentos.extend([None] * (total - len(lista_fragmentos)))
   
    lista_fragmentos[indice] = corpo_mensagem
    contador_fragmentos += 1
   
    if contador_fragmentos == total:
        with open('mensagem_recebida.txt', 'wb') as arquivo:
            for fragmento in lista_fragmentos:
                arquivo.write(fragmento)
        contador_fragmentos = 0
        lista_fragmentos = []
        exibir_mensagem_recebida()
    elif (contador_fragmentos < total) and (indice == total - 1):
        print("Possível perda de pacotes!")
        contador_fragmentos = 0
        lista_fragmentos = []

# Exibe a mensagem recebida
def exibir_mensagem_recebida():
    with open('mensagem_recebida.txt', 'r') as arquivo:
        conteudo = arquivo.read()
    os.remove('mensagem_recebida.txt')
    print(conteudo)

# Thread para receber mensagens
def receber():
    while True:
        dados, _ = cliente.recvfrom(1024)
        print("Mensagem recebida")
        reconstruir_mensagem(dados)

# Envia uma mensagem fragmentada
def enviar_mensagem():
    tamanho_fragmento = 1008
    with open('mensagem_cliente.txt', 'rb') as arquivo:
        dados = arquivo.read()
        total_fragmentos = math.ceil(len(dados) / tamanho_fragmento)
       
        indice_fragmento = 0
        while dados:
            fragmento = gerar_fragmento(dados, tamanho_fragmento, indice_fragmento, total_fragmentos)
            cliente.sendto(fragmento, ('localhost', 7777))
            dados = dados[tamanho_fragmento:]
            indice_fragmento += 1
   
    os.remove('mensagem_cliente.txt')

# Função principal de envio
def iniciar_cliente():
    usuario = ""
    while True:
        mensagem = input("Digite sua mensagem: ")
       
        if mensagem.lower().startswith("oi, meu nome eh"):
            usuario = mensagem[15:].strip()
            with open('mensagem_cliente.txt', 'w') as arquivo:
                arquivo.write(f"LOGIN:{usuario}")
            enviar_mensagem()
            print(f"Bem-vindo, {usuario}! Você está conectado.")
        elif usuario and mensagem.lower() == "tchau":
            with open('mensagem_cliente.txt', 'w') as arquivo:
                arquivo.write(f"LOGOUT:{usuario}")
            enviar_mensagem()
            print("Você saiu do chat. Até logo!")
            exit()
        else:
            if usuario:
                timestamp = datetime.now().strftime('%H:%M:%S - %d/%m/%Y')
                mensagem_formatada = f"{cliente.getsockname()[0]}:{cliente.getsockname()[1]}/~{usuario}: {mensagem} {timestamp}"
                with open('mensagem_cliente.txt', 'w') as arquivo:
                    arquivo.write(mensagem_formatada)
                enviar_mensagem()
            else:
                print("Você precisa se conectar primeiro digitando 'Oi, meu nome eh' seguido do seu nome.")

# Inicia a thread para receber mensagens
thread_recebimento = threading.Thread(target=receber)
thread_recebimento.start()

# Inicia a função principal
tentar_conectar = threading.Thread(target=iniciar_cliente)
tentar_conectar.start()