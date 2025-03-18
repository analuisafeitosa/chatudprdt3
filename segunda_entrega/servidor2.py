import socket #Conexão e comunicação
import time
from queue import * #Estrutura com comportamento desejado para assegurar fragmentação
from datetime import datetime #Extrair data do sistema para formato de print de mensagens
import threading  #Para programação concorrente
from threading import *

class Server:
    def __init__(self, port):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.mensagens = Queue()
        self.clientes_lista = []  # Enquanto mensagens auxiliará na manipulação das mesmas, clientes auxiliara armazenando infos sobre cada um dos nós
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.servidor.bind((self.host, self.port)) #Criamos servidor e alocamos porta e nome qualquer
        self.rcv_ack = threading.Event()
        self.acknowlodge_number = 0
        self.numero_seq = None
        self.flags = ["SYN".encode(), "ACK".encode(), "SYN ACK".encode()] #Flags que vamos usar pra o ordenamento
        print(f"Servidor online na porta {self.port}") #Para verificação de erro e melhor comunicação
        connection_thread = Thread(target=self.conexao)
        connection_thread.start()
        connection_thread.join()# Prioriza o handshake, só podendo executar as próximas funções com a conexão estabelecida
        receive_thread = Thread(target=self.receber)
        send_thread = Thread(target=self.broadcast)
        send_thread.start()
        receive_thread.start()


    def checksum(self, mensagem):
        tamanho = len(mensagem)
        if tamanho & 1:
            tamanho -= 1
            soma = ord(mensagem[tamanho])
        else:
            soma = 0
        while tamanho>0:
            tamanho-=2
            soma+= (ord(mensagem[tamanho+1])<<8)+ ord(mensagem[tamanho])
        soma = (soma>>16) + (soma & 0xffff)
        soma += (soma>>16)
        resultado = (~soma) & 0xffff
        resultado = resultado>>8 | ((resultado&0xff)<<8)
        return chr(resultado//256)+chr(resultado%256)

    def conexao(self, cl_mensagem=None, cl_endereco = None):
        while True:
            if not cl_mensagem: #Caso ainda não definida, aguardará o SYN
                flag_syn, cl_endereco = self.servidor.recvfrom(1024) #Recebe SYN aqui
                cl_mensagem = flag_syn.decode()
            if cl_mensagem=="SYN": #Recebeu SYN e agora enviará SYN ACK
                print("Pedido de conexão recebido. Enviando confirmação...")
                self.servidor.sendto(self.flags[2], cl_endereco)
                time.sleep(0.01)
                flag_ack, solicitante = self.servidor.recvfrom(1024) #Aguardando ACK
                if flag_ack.decode()=="ACK":
                    print(f"Enviada confirmação. Estabelecendo conexão via {self.port}")
                    self.acknowlodge_number = 1
                    break
            else:
                print("Não houve pedido de conexão.")

    def receber(self):
        while 1:
            try:
                # Nome do arquivo e endereço que será solicitado
                nome_arquivo, addr_remetente = self.servidor.recvfrom(1024) #Aguardando mensagens, recebo uma e com ela há: conteúdo em bytes e uma tupla com "ip" e porta
                nome_arquivo = nome_arquivo.decode()
                if nome_arquivo=="SYN":
                    n_seq = 0
                    self.conexao(nome_arquivo, addr_remetente)
                    self.eh_novo_cliente(nome_arquivo, addr_remetente)
                if nome_arquivo== "ACK 0" or nome_arquivo=="ACK 1":
                    self.numero_seq = int(nome_arquivo[-1:])
                    self.rcv_ack.set()
                elif nome_arquivo!="ACK 0" and nome_arquivo!="ACK 1":
                    if nome_arquivo!="SYN":
                        checksum = nome_arquivo[:2]
                        n_seq = nome_arquivo[2]
                        pacote = nome_arquivo[3:]
                        resultado_checksum = self.checksum(pacote)
                        if checksum == resultado_checksum:
                            self.mensagens.put((pacote, addr_remetente)) #Adiciona na fila com o conteúdo já em string, especificações utf-8 para os char especiais, e o endereço do remetente
                            #Observe que será uma fila com uma tupla, aonde o primeiro elemento[0] também é uma tupla, por conter "ip" e porta
                            self.servidor.sendto(f"ACK {str(n_seq)}".encode(), addr_remetente)
                        elif not checksum == resultado_checksum:
                            self.servidor.sendto(f"ACK {str(1 - int(n_seq))}".encode(), addr_remetente)
                            if nome_arquivo != "SYN":
                                print("Erro de integridade")
            except OSError as os_error:
                # Verificando se é um erro de conexão interrompida pelo usuário
                if os_error.errno == 10054:
                    print("Conexão encerrada pelo cliente.")
                    continue
                else:
                    print(f"Erro do sistema operacional: {os_error}")
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")


    def eh_novo_cliente (self, mensagem, addr):
        conectados = [c[0] for c in self.clientes_lista]
        '''Essa lista compreensada retorna para mim apenas o [0] de cada tupla da lista, ou seja o endereço de cada nó, pois essa lista mais tarde
        se comportará assim: clientes = [((x, y), nome), ((x2, y2), nome2)], aonde x é "ip" e y é porta de cada cliente'''
        if addr not in conectados: #Se o endereço não está conectado, temos um novo cliente
            if mensagem.startswith("hi, meu nome eh:"): #Logo, ele está se conectando informando seu nome
                nome = mensagem[len("hi, meu nome eh:"):] #Fatiamento coletando tudo após a mensagem padrão, ou seja o nome em si
                self.clientes_lista.append((addr, nome)) #Adicionado na lista
                return nome #Retorno o nome, pois será utilizado nas outras funções
        return False

    def handle_file(self,mensagem, addr, nome):
        formato = f">>>({addr[0]}:{addr[1]}/~{nome}): " #Addr é uma tupla com "ip" e porta, vamos adicionar essa formatação como primeira mensagem em uma sequência qualquer de envios
        envio = [formato]
        while mensagem != "\\END": #Enquanto não for a flag que representa o fim, seguiremos adicionando os pacotes na lista
            envio.append(mensagem)
            mensagem, _ = self.mensagens.get()#Perceba que também tenho o addr aqui, mas se fosse utilizar para definir a formatação daria conflito com a lógica do END
            #mensagem = mensagem.decode("utf-8")
        timestamp = datetime.now().strftime(" (%H:%M:%S %d/%m/%Y)") #Outra parte da formatação
        envio.append(timestamp)
        return envio

    def enviar(self, n_seq, mensagem, dst, nome):
        ack = False
        while not ack:
            checksum = self.checksum(mensagem).encode()  # Estabelece o checksum da mensagem
            numero_seq = str(n_seq).encode()  # Coleta e estabelece o número de seq
            pacote = (checksum + numero_seq + mensagem.encode())  # Formato da mensagem, do chunk
            self.servidor.sendto(pacote, dst) # Envia o pacote
            if self.rcv_ack.wait(3): #Timeout de três segundos para receber um ACK
                time.sleep(0.1)
                if self.numero_seq == n_seq: #Recebido ACK e foi o esperado
                    ack = True
                    print(f"ACK {n_seq} recebido com sucesso {nome}")
                else: #Recebido, mas não foi o esperado, não é setado como true e ocorre assim retransmissão
                    print(f"Houve algum erro na entrega de {nome}, tentando novamente...")
            else: #Timeout estourado
                print("Tempo esgotado, tentando estabelecer... Reenviando...")
                pass

    def broadcast(self):
        while 1:
            try:
                nome_arquivo, addr_remetente = self.mensagens.get()#Coleta o nome do arquivo solicitado
                envio = []  # Irá armazenar a mensagem que será enviada
                novo_cliente = self.eh_novo_cliente(nome_arquivo, addr_remetente) #Verifica se o remetente é novo
                if novo_cliente: #Se for novo cliente enviará uma mensagem para todos alertando a sua chegada, além de uma confirmação de entrada para o próprio
                    envio.append(f"\n>>>>{novo_cliente} entrou na sala")
                    self.enviar(self.acknowlodge_number, "VOCÊ ENTROU NA SALA", addr_remetente, novo_cliente)
                    self.acknowlodge_number = 1 - self.acknowlodge_number
                    self.enviar(self.acknowlodge_number, "\\END", addr_remetente, novo_cliente)
                    self.acknowlodge_number = 1 - self.acknowlodge_number
                elif not novo_cliente: #Se não for, irei transformar a lista de clientes em um dicionário, para que acesse facilmente seus endereços, pois serão colunas
                    clientes_dicionario = dict(self.clientes_lista)
                    nome = clientes_dicionario.get(addr_remetente)
                    print(f"Remetente: {nome}")
                    print(f"Conectados: {clientes_dicionario}")
                    if nome_arquivo=="bye": #Desconectando caso seja bye
                        envio.append(f"{nome} saiu da sala")
                        self.enviar(self.acknowlodge_number, "Você saiu da sala", addr_remetente, nome)
                        self.acknowlodge_number = 1 - self.acknowlodge_number
                        self.enviar(self.acknowlodge_number, "\\END",addr_remetente, nome)
                        self.acknowlodge_number = 1 - self.acknowlodge_number
                        self.clientes_lista.remove((addr_remetente, nome))
                    elif nome_arquivo!="bye":
                        envio = self.handle_file(nome_arquivo, addr_remetente, nome) #Por fim, se for uma mensagem padrão enviada, será chamada a função handle_file para formatar corretamente
                for c in self.clientes_lista: #O broadcast em si acontece aqui, enviando a mensagem para todos conectados que tenham endereço diferente do remetente
                    addr_dst, nome_dst = c
                    if addr_dst == addr_remetente:
                        pass
                    elif addr_dst != addr_remetente:
                        for pacote in envio: #Cada parte do envio
                            self.enviar(self.acknowlodge_number, pacote, addr_dst, nome_dst)
                            self.acknowlodge_number = 1 - self.acknowlodge_number
                        self.enviar(self.acknowlodge_number, "\\END", addr_dst, nome_dst)
                        self.acknowlodge_number = 1 - self.acknowlodge_number
            except Exception as e:
                print(f"Erro ao enviar arquivo: {e}")

sv = Server(7777)