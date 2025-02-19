import socket
import os
import queue
import math
import threading
import struct
from zlib import crc32

# Configuração do Servidor
usuarios_conectados = []  # Lista de clientes conectados
fila_mensagens = queue.Queue()
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(('localhost', 7777))  # Define o endereço e a porta do servidor

# Armazena fragmentos recebidos
lista_fragmentos = []
contador_fragmentos = 0

# Função para criar fragmentos de dados
def gerar_fragmento(dados, tamanho_fragmento, indice_fragmento, total_fragmentos):
    
    #Divide os dados em partes menores (fragmentos) para envio.
    #Adiciona um cabeçalho contendo informações como tamanho, índice, total e checksum (CRC32).
    
    parte_dados = dados[:tamanho_fragmento]
    checksum = crc32(parte_dados)
    cabecalho = struct.pack('!IIII', tamanho_fragmento, indice_fragmento, total_fragmentos, checksum)
    return cabecalho + parte_dados

# Função para reconstruir a mensagem original a partir dos fragmentos recebidos
def reconstruir_mensagem(dados_recebidos, endereco_cliente):

    #Reagrupa os fragmentos recebidos, verifica a integridade dos dados pelo checksum (CRC32)
    #e processa a mensagem quando todos os fragmentos forem recebidos.
    
    global contador_fragmentos, lista_fragmentos
    cabecalho = dados_recebidos[:16]  # Primeiro bloco contém metadados
    corpo_mensagem = dados_recebidos[16:]
    tamanho, indice, total, checksum = struct.unpack('!IIII', cabecalho)
   
    # Validação do checksum para garantir a integridade dos dados
    if checksum != crc32(corpo_mensagem):
        print("Fragmento corrompido (CRC inválido), ignorando...")
        return
   
    # Ajusta a lista de fragmentos se necessário
    if len(lista_fragmentos) < total:
        lista_fragmentos.extend([None] * (total - len(lista_fragmentos)))
   
    lista_fragmentos[indice] = corpo_mensagem
    contador_fragmentos += 1
   
    # Se todos os fragmentos foram recebidos, reconstroi a mensagem
    if contador_fragmentos == total:
        with open('mensagem_recebida.txt', 'wb') as arquivo:
            for fragmento in lista_fragmentos:
                arquivo.write(fragmento)
       
        contador_fragmentos = 0
        lista_fragmentos = []
        processar_mensagem(endereco_cliente)
    elif (contador_fragmentos < total) and (indice == total - 1):
        print("Possível perda de pacotes detectada!")
        contador_fragmentos = 0
        lista_fragmentos = []

# Processa a mensagem recebida, identificando login, logout ou mensagens comuns
def processar_mensagem(endereco_cliente):

    # le a mensagem reconstruída, identifica se é login/logout ou uma mensagem normal,
    #e envia para os demais usuários conectados.
    
    with open('mensagem_recebida.txt', 'r') as arquivo:
        conteudo = arquivo.read()
    os.remove('mensagem_recebida.txt')
   
    for linha in conteudo.strip().split('\n'):
        linha = linha.strip()
        if "LOGIN:" in linha:
            nome_usuario = linha.split(":")[1]
            mensagem = f"{nome_usuario} entrou no chat"
            print(f"{endereco_cliente} conectado como {nome_usuario}")
            fila_mensagens.put(mensagem)
        elif "LOGOUT:" in linha:
            nome_usuario = linha.split(":")[1]
            mensagem = f"{nome_usuario} saiu do chat"
            print(f"{endereco_cliente} desconectado ({nome_usuario})")
            usuarios_conectados.remove(endereco_cliente)
            print(f"Usuários ativos: {usuarios_conectados}")
            fila_mensagens.put(mensagem)
        else:
            fila_mensagens.put(linha)
            print(f"Mensagem recebida de {endereco_cliente}: {linha}")
   
    enviar_para_todos(endereco_cliente)

# envia mensagens para todos os usuários conectados
def enviar_para_todos(remetente):
    
    #Recupera mensagens da fila e as envia fragmentadas para todos os clientes conectados,
    #exceto o remetente original.
    
    tamanho_fragmento = 1008
    while not fila_mensagens.empty():
        mensagem = fila_mensagens.get()
       
        with open('mensagem_servidor.txt', 'w') as arquivo:
            arquivo.write(mensagem)
       
        with open('mensagem_servidor.txt', 'rb') as arquivo:
            dados = arquivo.read()
            total_fragmentos = math.ceil(len(dados) / tamanho_fragmento)
           
            for cliente in usuarios_conectados:
                if cliente != remetente:
                    dados_restantes = dados
                    indice_fragmento = 0
                    while dados_restantes:
                        fragmento = gerar_fragmento(dados_restantes, tamanho_fragmento, indice_fragmento, total_fragmentos)
                        servidor.sendto(fragmento, cliente)
                        dados_restantes = dados_restantes[tamanho_fragmento:]
                        indice_fragmento += 1
                    print(f"Mensagem enviada para {cliente}")
       
        os.remove('mensagem_servidor.txt')

# Thread que fica em espera para receber dados de clientes
def escutar():
    
    #Loop principal do servidor que recebe mensagens e gerencia conexões dos clientes.
    
    while True:
        dados, endereco = servidor.recvfrom(1024)
        print("Novo pacote recebido")
        if endereco not in usuarios_conectados:
            usuarios_conectados.append(endereco)
            print(f"Usuários conectados: {usuarios_conectados}")
       
        reconstruir_mensagem(dados, endereco)

# Inicia a thread para receber mensagens dos clientes
thread_recebimento = threading.Thread(target=escutar)
thread_recebimento.start()