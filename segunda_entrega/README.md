# README - Implementação do Chat com Transferência Confiável RDT 3.0

## Visão Geral
Este projeto implementa um sistema de chat básico utilizando o protocolo de transferência confiável RDT 3.0, conforme descrito no livro "Redes de Computadores e a Internet" de Kurose e Ross. A implementação baseia-se no código desenvolvido na primeira etapa do projeto e aprimora a confiabilidade da comunicação ao lidar com perda e corrupção de pacotes.

## Funcionalidades Implementadas
- Troca de mensagens entre participantes do chat via sockets UDP.
- Implementação do protocolo RDT 3.0 para garantir a confiabilidade da comunicação.
- Uso de checksum para verificação de integridade dos pacotes.
- Mecanismo de retransmissão com timeout para pacotes perdidos.
- Controle de fluxo via números de sequência para evitar retransmissões incorretas.
- Impressão de logs para depuração e acompanhamento da transmissão.
- Implementação de threads para permitir comunicação bidirecional simultânea.
- Capacidade de múltiplos clientes se conectarem ao servidor.

## Requisitos
- Python 3.x
- Biblioteca `socket`, `struct`, `threading`, `os`, `math` e `time` (nativas do Python)

## Estrutura do Projeto
```
/
|-- client.py  # Implementação do cliente
|-- server.py  # Implementação do servidor
|-- README.md  # Documentação do projeto
```

## Como Executar

### 1. Iniciar o Servidor
Abra um terminal e execute:
```bash
python server.py
```
O servidor ficará aguardando conexões de clientes e processando mensagens recebidas.

### 2. Iniciar um Cliente
Em outro terminal, execute:
```bash
python client.py
```
O cliente permitirá a entrada de mensagens que serão enviadas para os demais participantes do chat.

## Funcionamento do RDT 3.0
O protocolo RDT 3.0 garante a entrega confiável das mensagens utilizando os seguintes mecanismos:

1. **Checksum**: Cada pacote enviado inclui um checksum para verificar a integridade dos dados.
2. **ACK**: O destinatário responde com um pacote de confirmação (`ACK`) se os dados estiverem corretos.
3. **Timeout e Retransmissão**: Se um `ACK` não for recebido dentro do tempo limite, o pacote é retransmitido.
4. **Controle de Sequência**: Cada pacote recebe um número de sequência para evitar problemas de duplicidade.
5. **Threads**: O cliente e o servidor utilizam threads para permitir envio e recebimento de mensagens simultaneamente.
6. **Suporte a Múltiplos Clientes**: O servidor pode gerenciar múltiplos clientes simultaneamente e encaminhar mensagens corretamente.

## Exemplo de Fluxo de Mensagens
1. O cliente digita uma mensagem e a envia para o servidor.
2. A mensagem é fragmentada, e cada fragmento recebe um checksum e um número de sequência.
3. O servidor recebe os pacotes, verifica a integridade, reagrupa os fragmentos e reenvia para os clientes conectados.
4. Os clientes recebem os fragmentos, validam os checksums e montam a mensagem original.
5. Se houver perda de pacotes ou erro de checksum, a retransmissão é acionada até que o `ACK` seja confirmado.
6. O chat suporta múltiplos clientes, garantindo que todos recebam as mensagens enviadas.



