#  Sistema de Chat com UDP e RDT 3.0

## 📌 Visão Geral
Este repositório contém a implementação de um sistema de comunicação Cliente-Servidor utilizando o protocolo UDP, com suporte a fragmentação de mensagens e retransmissão confiável via RDT 3.0. O projeto foi desenvolvido em duas etapas:

1. **Primeira Entrega**: Implementação básica do chat com envio de mensagens fragmentadas e verificação de integridade via CRC32.
2. **Segunda Entrega**: Aprimoramento da comunicação com a adição do protocolo RDT 3.0, garantindo confiabilidade na entrega das mensagens.

---

## 🚀 Funcionalidades

### ✅ Primeira Entrega - Cliente e Servidor UDP com Fragmentação
- Envio e recebimento de mensagens fragmentadas.
- Uso de CRC32 para garantir a integridade dos dados.
- Implementação de login ("Oi, meu nome é <username>") e logout ("Tchau").
- Servidor realiza broadcast das mensagens para todos os clientes conectados.

### ✅ Segunda Entrega - Implementação de RDT 3.0
- Confiabilidade na comunicação através do protocolo RDT 3.0.
- Uso de checksum para verificação de pacotes.
- Retransmissão automática de pacotes perdidos ou corrompidos.
- Controle de fluxo com números de sequência.
- Threads para comunicação bidirecional simultânea.
- Suporte a múltiplos clientes conectados.

---

## 🛠️ Tecnologias Utilizadas
- **Python 3**
- **Sockets UDP** para comunicação Cliente-Servidor
- **CRC32 e Checksum** para integridade dos pacotes
- **Threading** para comunicação simultânea
- **Timeouts e Retransmissão** para confiabilidade via RDT 3.0

---

## 📚 Estrutura do Repositório
```
/
|-- primeira_entrega/
|   |-- cliente.py   # Código do Cliente UDP
|   |-- servidor.py  # Código do Servidor UDP
|   |-- message_client.txt  # Armazena mensagens enviadas
|   |-- received_message.txt  # Armazena mensagens recebidas
|
|-- segunda_entrega/
|   |-- cliente2.py  # Cliente UDP com RDT 3.0
|   |-- servidor2.py  # Servidor UDP com RDT 3.0
|
|-- README.md  # Documentação principal
```

---

## 🔧 Como Executar

### 📌 Primeira Entrega
1. **Rodar o Servidor**:
   ```bash
   cd primeira_entrega
   python servidor.py
   ```
2. **Rodar o Cliente**:
   ```bash
   python cliente.py
   ```

### 📌 Segunda Entrega (com RDT 3.0)
1. **Rodar o Servidor**:
   ```bash
   cd segunda_entrega
   python servidor2.py
   ```
2. **Rodar o Cliente**:
   ```bash
   python cliente2.py
   ```

---

## 🎯 Funcionamento do RDT 3.0
1. O cliente envia a mensagem fragmentada com checksum e número de sequência.
2. O servidor verifica a integridade e reagrupa os fragmentos.
3. Caso haja perda ou erro, o pacote é retransmitido automaticamente.
4. O servidor envia a mensagem reconstituída para os clientes conectados.
5. Cada cliente confirma o recebimento com um ACK.

---

## 👥 Equipe
- **Ana Luisa Feitosa**
- **Lucas dos Santos Silva**
- **Maria Clara Gomes**

---

## 📌 Notas Importantes
- O código assume que a comunicação ocorre em **localhost**.
- Pacotes corrompidos ou fora de ordem são detectados e retransmitidos automaticamente.
- O sistema suporta múltiplos clientes conectados simultaneamente.

Este projeto é uma implementação prática de comunicação confiável sobre UDP, explorando conceitos fundamentais de redes. 🚀

---
## 🎥 Demonstração
[Veja uma explicação e demonstração do código no YouTube](https://youtu.be/hQqm9-NRLoc?si=drZPWPh5kFN8U5Uq)

