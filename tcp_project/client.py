import socket
import threading
import sys
import os

""""
Protocolo de aplicação sugerido pelos alunos:

- Conexão TCP/IP

Cada mensagem deve ser precedida do seguinte cabeçalho:

No caso de uma mensagem de arquivo, o cabeçalho deve ser:
+---------------------------+
| Tipo da msg               |
+---------------------------+
| Nome do arquivo           |
+---------------------------+
| Tamanho total do arquivo  |
+---------------------------+
| Conteúdo da msg           |

No caso de uma mensagem de texto, o cabeçalho deve ser:
+---------------------------+
| Tipo da msg               |
+---------------------------+
| Conteúdo da msg           |

Onde:
- Tipo da msg: um byte que indica o tipo da mensagem (0 para texto para buffer CLI, 1 para arquivo)
- Tamanho da msg: um valor binario representando o tamanho da mensagem em bytes
- Conteúdo da msg: o conteúdo da mensagem, que pode ser texto ou dados de arquivo
"""

class Client:
    def __init__(self, host='localhost', port=6363):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.receive_thread = None

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Conexao com sucesso em {self.host}:{self.port}")
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
        except Exception as e:
            print(f"Nao foi possivel conectar {self.host}:{self.port}: {e}")
            sys.exit(1)

    def _receive_messages(self):
        while self.running:
            try:
                self.handle_data() 
            except Exception as e:
                if self.running:
                    print(f"Erro ao receber: {e}")
                break
        self.stop()

    def handle_data(self):
        # Extrai informações do cabeçalho
        message_type = self.socket.recv(1).decode()
        if message_type == '0':
            # Mensagem de texto
            content = self.socket.recv(1024-1).decode()
            if content:
                print(f"Mensagem recebida: {content}")
            
        elif message_type == '1': 
            print("handle_Data -> 1")
            file_name = self.socket.recv(128)
            print("file_name", file_name)
            file_size = int (self.socket.recv(4))
            content = self.socket.recv(1024 - 128 - 4)
            print("file_size",  file_size)
            
            with open(f"{file_name}.received", 'ab') as f:
                file_current_size = f.tell()
                if file_current_size < file_size and content:
                    print("escrevendo: ", content)
                    f.write(content)

    def send(self, message):
        if self.running and message:
            try:
                self.socket.send(message.encode())
            except Exception as e:
                print(f"Erro ao enviar msg: {e}")
                self.stop()
            
    def stop(self):
        if self.running:
            self.running = False
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.socket.close()
            print("Desconectado.")
        sys.exit(0)

    def run(self):
        self.connect()
        try:
            while True:
                message = input()
                if message.lower() in ('sair'):
                    print("Desconectado...")
                    break
                self.send(message)
        except KeyboardInterrupt:
            print("\nSaindo...")
        finally:
            self.stop()

if __name__ == "__main__":
    host = 'localhost'
    port = 6363
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Usando porta padrão 6363.")

    client = Client(host, port)
    client.run()
