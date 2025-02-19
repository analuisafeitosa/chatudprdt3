# 🖥️ **Cliente e Servidor UDP com Fragmentação de Mensagens** 

Este repositório contém dois scripts em Python para simular uma comunicação entre **cliente** e **servidor** utilizando o protocolo UDP, onde as mensagens são fragmentadas, transmitidas e reagrupadas com verificação de integridade via CRC32.

## 💡 **Funcionalidade**

1. **Cliente**: 
   - Conecta ao servidor, se autenticando com um nome de usuário.
   - Envia mensagens fragmentadas, com cada fragmento contendo um cabeçalho de controle para reconstituir a mensagem corretamente no servidor.
   - Envia também mensagens de login (`hi, meu nome eh <username>`) e logout (`bye`).

2. **Servidor**:
   - Recebe os fragmentos das mensagens enviadas pelo cliente.
   - Reagrupa e valida os fragmentos, verificando a integridade dos dados com CRC.
   - Processa as mensagens de login e logout, além de fazer o *broadcast* das mensagens para todos os clientes conectados.

## 🚀 **Como Usar**

### 🧑‍💻 **Cliente**:
1. Defina o nome de usuário com o comando `Oi, meu nome eh <username>`.
2. Envie suas mensagens.
3. Para desconectar, digite `tchau`.

### 🖥️ **Servidor**:
1. O servidor aguarda por fragmentos de mensagem de clientes.
2. As mensagens são recebidas, processadas e retransmitidas para todos os clientes conectados.

### 💾 **Arquivos Importantes**
- **message_client.txt**: Armazena a mensagem a ser enviada pelo cliente.
- **received_message.txt**: Armazena a mensagem recebida e reconstituída pelo servidor.

---

## 🛠️ **Tecnologias Usadas**
- **Python 3**.
- **Socket UDP** para comunicação entre cliente e servidor.
- **CRC32** para verificação da integridade dos fragmentos.
- **Threading** para comunicação simultânea.

## 🔧 **Instruções para Rodar**

1. Execute o servidor:
   - Abra um terminal e execute o arquivo do servidor.
   - O servidor começará a escutar na porta 7777.

2. Execute o cliente:
   - Abra outro terminal e execute o arquivo do cliente.
   - O cliente se conecta ao servidor e pode começar a enviar mensagens.

---

### 🎨 **Arquitetura**
1. O cliente fragmenta a mensagem em pacotes e os envia para o servidor.
2. O servidor reagrupa esses pacotes e verifica a integridade usando CRC32.
3. Quando todos os fragmentos são recebidos corretamente, o servidor retransmite a mensagem para todos os clientes conectados.

### 📜 **Estrutura de Fragmento**
- O fragmento consiste em:
  - **Cabeçalho**: Contém o tamanho do fragmento, índice, número total de fragmentos e CRC.
  - **Dados**: A parte da mensagem dividida no fragmento.

---

## 📌 **Notas Importantes**
- O código assume que a comunicação é feita em `localhost`.
- A integridade dos fragmentos é verificada com CRC32. Caso um fragmento tenha erro, ele será ignorado.
- Ao alcançar o número total de fragmentos, o servidor reconstituirá a mensagem e a enviará de volta aos clientes.

---

## 🧠 **Desafios Enfrentados e Soluções**

### 💥 **Desafio: Implementação da Fragmentação de Mensagens**
A principal dificuldade deste projeto foi entender como implementar a fragmentação das mensagens. Como o protocolo UDP não garante a entrega sequencial dos pacotes, tivemos que dividir as mensagens em pequenos fragmentos para enviá-los de forma mais confiável. Além disso, precisávamos garantir que todos os fragmentos fossem reagrupados corretamente no servidor, mantendo a integridade da mensagem original. 

Outro desafio foi lidar com a reordenação dos fragmentos, o que exigiu que os fragmentos fossem recebidos e armazenados em uma lista, e só a mensagem completa seria reconstituída. Para isso, tivemos que implementar um sistema de controle de índice, além de calcular o número total de fragmentos para garantir que todos os dados fossem recebidos.

### 🧑‍🏫 **Facilitador: Monitoria e CRC**
Um dos grandes facilitadores desse projeto foi a ajuda da monitoria, que indicou a pesquisa sobre o uso do **CRC32** (Cyclic Redundancy Check). A sugestão de implementar esse algoritmo foi essencial para garantir a verificação de integridade dos fragmentos de mensagem. Usando CRC32, conseguimos detectar pacotes corrompidos e garantir que apenas fragmentos válidos fossem reconstituídos e retransmitidos.

Essa abordagem foi fundamental para resolver os problemas de confiabilidade e integridade, e sem a indicação da monitoria, certamente teríamos enfrentado mais dificuldades para garantir que os dados chegassem ao servidor de maneira correta.

---

## **Equipe**
[Ana Luisa Feitosa <alfg>](https://github.com/analuisafeitosa) <br>
[Lucas dos Santos Silva <lss11>](https://github.com/0lucasantos) <br>
[Maria Clara Gomes <mcga>](https://github.com/M4riaclaragomes)


## 📄 **Arquivos do Projeto**

### **Cliente:**
O código do cliente está no arquivo `cliente.py`. Este script gerencia a criação, envio e recebimento de mensagens fragmentadas. Ele também gerencia o login e logout dos usuários.

### **Servidor:**
O código do servidor está no arquivo `servidor.py`. Este script recebe as mensagens fragmentadas, reagrupa-as e envia para todos os clientes conectados.

---
