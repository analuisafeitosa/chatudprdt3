import socket
import threading
from threading import *
from pathlib import *
import time



class Client:
    def __init__(self, servidor):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cliente.connect(servidor)
        self.nome = None
        self.flags = ["SYN".encode(), "ACK".encode()] #Flags que vamos usar pra o ordenamento
        self.servidor = servidor
        self.acknowlodge_number = None
        self.rcv_ack = threading.Event() #Detecta o recebimento de ack, o próprio algoritmo aponta se houver e seta
        connection_thread = Thread(target=self.conexao)
        connection_thread.start()
        connection_thread.join() #Prioriza o handshake, só podendo executar as próximas funções com a conexão estabelecida
        receiveClient_thread = Thread(target=self.receber)
        receiveClient_thread.start()


    def conexao(self): #Three Way Handshake
        time.sleep(0.01)
        self.cliente.sendto(self.flags[0], self.servidor) #Envio de SYN
        print("Solicitada conexão")
        time.sleep(0.01)
        flag_synack, _ = self.cliente.recvfrom(1024) #Espera-se receber SYN-ACK
        if flag_synack.decode() == "SYN ACK":
            print("Conexão aceita")
            time.sleep(0.01)
            self.cliente.sendto(self.flags[1], self.servidor) #Envia ACK
            time.sleep(0.01)
            print("Conexão estabelecida com sucesso")

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

    def receber(self):
        mensagem_rc = ""
        while 1:
            try:
                mensagem_pt, addr_remetente = self.cliente.recvfrom(1024) #Aguarda o recebimento de pacotes, recebendo coleta endereço do remetente e payload
                mensagem_pt = mensagem_pt.decode("utf-8") #Deixo em str
                if mensagem_pt == "ACK 0" or mensagem_pt=="ACK 1": #Gravando número de sequência
                    self.acknowlodge_number = int(mensagem_pt[-1:])
                    self.rcv_ack.set() #Aponta que foi recebido o ACK
                elif mensagem_pt != "ACK 0" and mensagem_pt != "ACK 1": #Se não for flag
                    checksum = mensagem_pt[:2] #Formatação
                    numero_seq = mensagem_pt[2]
                    pacote = mensagem_pt[3:]
                    resultado_checksum = self.checksum(pacote) #Calculo do checksum para comparar com o que se espera
                    if checksum == resultado_checksum:
                        if pacote != "\\END":  # Se for a flag de fim a mensagem está completa, trata-se do último fragmento (ou único), caso não é concatenado
                            mensagem_rc += pacote
                            print(f"\nIntegridade validada. Enviando ACK {numero_seq}")
                            self.cliente.sendto(f"ACK {str(numero_seq)}".encode(), self.servidor)
                        else:
                            print(mensagem_rc)
                            if mensagem_rc != "VOCÊ ENTROU NA SALA" and mensagem_rc != "Você saiu da sala":
                                print("Nome do arquivo .txt: ")
                            mensagem_rc = "" #Reset para próxima solicitação
                            self.cliente.sendto(f"ACK {str(numero_seq)}".encode(), self.servidor)
                    elif not checksum == resultado_checksum:
                        self.cliente.sendto(f"ACK {str(1-int(numero_seq))}".encode(), self.servidor)
                        if mensagem_pt != "SYN ACK":
                            print("Erro de integridade")
            except:
                pass
    def enviar(self, n_seq, mensagem):
        ack = False
        while not ack:
            checksum = self.checksum(mensagem).encode() #Estabelece o checksum da mensagem
            numero_seq = str(n_seq).encode() #Coleta e estabelece o número de seq
            pacote = (checksum + numero_seq + mensagem.encode()) #Formato da mensagem, do chunk
            self.cliente.sendto(pacote, self.servidor) #Envia o pacote
            if self.rcv_ack.wait(3): #Timeout de três segundos para receber um ACK
                time.sleep(0.1)
                if self.acknowlodge_number == n_seq: #Recebido ACK e foi o esperado
                    ack = True
                    print("Mensagem recebida com sucesso")
                else: #Recebido, mas não foi o esperado, não é setado como true e ocorre assim retransmissão
                    print("Houve algum erro na entrega, tentando novamente...")
            else: #Timeout estourado
                print("Tempo esgotado, tentando estabelecer... Reenviando...")
                pass

cl = None
conexao = int(input("Digite a porta do servidor que deseja se conectar:\n"))
host = socket.gethostbyname(socket.gethostname())
try:
    cl = Client((host, conexao))
except:
    print("Erro: Servidor não responde ou não existe.")

n_seq, verificacao = 0, False

while not verificacao:
    solicitacao = "hi, meu nome eh:"+ input("Seu nome:")
    if solicitacao.startswith("hi, meu nome eh:"): #Se enviou o comando para inserir nome e realmente ainda não estiver conectado
        if not cl.nome:
            cl.nome = solicitacao[len("hi, meu nome eh:"):]
            cl.enviar(n_seq, solicitacao)
            n_seq = 1 - n_seq
            verificacao = True
        elif cl.nome:
            print("Já conectado!")
    else:
        print("Para se conectar, insira seu nome")

while 1:
    time.sleep(0.1)
    print("\nEnvie o caminho de um arquivo .txt")
    solicitacao = input("Nome do arquivo .txt:")
    if solicitacao=="bye" and cl.nome: #Se conectado e solicitar desligamento, basta alertar o servidor e depois liberar o socket
        cl.enviar(n_seq, solicitacao)
        n_seq = 1 - n_seq
        time.sleep(0.1)
        cl.cliente.close()
        cl.nome = None
        exit()
    elif cl.nome and solicitacao!="bye":
        nome_arquivo = Path(solicitacao)
        if nome_arquivo.is_file() and nome_arquivo.suffix.lower()==".txt": #Verificando se há um arquivo com o path solicitado e se seu sufixo (extensão) é txt
            with open(nome_arquivo, 'rb') as arquivo: #Abre o arquivo e lhe declara um nome no contexto
                data = arquivo.read(1024) #Lê os primeiros 1024 bytes
                while data: #Enquanto for possivel, envia os dados
                    cl.enviar(n_seq, data.decode())
                    n_seq = 1 - n_seq
                    data = arquivo.read(1024) #E lê os próximos pacotes de até 1024
            cl.enviar(n_seq, "\\END") #Envia flag de fim
            n_seq = 1 - n_seq
        elif not nome_arquivo.is_file() or not nome_arquivo.suffix.lower()==".txt":
            print("Erro: Envie o caminho de um arquivo existente no formato .txt em sua máquina")
            time.sleep(0.01)
            print("Se estiver na pasta atual basta digitar seu nome e a extensão .txt")
    time.sleep(1)