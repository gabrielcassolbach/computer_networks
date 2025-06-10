import socket
import os
import threading
import time
import sys
import hashlib

""""
Protocolo de aplicação sugerido pelos alunos:

- Conexão TCP/IP

Cada mensagem deve ser precedida do seguinte cabeçalho:

No caso de uma mensagem de arquivo, o cabeçalho deve ser:
+---------------------------+
| Tipo da msg               |
+---------------------------+
| Tamanho em bytes do nome  |
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

class Server:
    def __init__(self, host='localhost', port=6363):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_sockets = []
        self.running = True
        self.lock = threading.Lock()
        
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor conectado com {self.host}:{self.port}")

        threading.Thread(target=self.send_message_clients, args=()).start()

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexao com {addr}")
            with self.lock:
                self.client_sockets.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            
    def send_message_clients(self):
        while self.running:
            msg = sys.stdin.readline().strip()
            if msg:
                with self.lock:
                    for sock in self.client_sockets:
                        try:
                            self.send_message(type=0, content=msg, client_socket=sock)
                        except Exception as e:
                            print(f"Erro ao enviar mensagem para o cliente: {e}")

    def handle_request(self, message, client_socket): 
        if message == "sair":
            print("Operação 'Sair'")
            with self.lock:
                self.client_sockets.remove(client_socket)
            client_socket.close()
            print("Cliente desconectado")
            return
        
        if message.startswith("arquivo "):
            filename = message.split(" ", 1)[1]
            print(f"Operação 'Arquivo' com arquivo: {filename}")
            try:
                with open(filename, 'rb') as f:
                    file_size = os.path.getsize(filename)
                    print(f"Tamanho do arquivo: {file_size} bytes")
                    current_size = 0
                    header_size = 1 + len(filename) + 4 + 1
                    full_content = b''
                    while current_size != file_size:
                        data = f.read(1024 - header_size)
                        full_content += data
                        current_size += len(data)
                        self.send_message(1, data, filename, file_size, client_socket=client_socket)
                    filehash = hashlib.sha256()  
                    filehash.update(full_content)
                    client_socket.sendall(filehash.digest())
                    print(f"Arquivo {filename} enviado para o cliente.")
            except FileNotFoundError:
                print(f"Arquivo {filename} não encontrado.")
                client_socket.sendall(b"0Arquivo nao encontrado.")
                
        elif message.startswith("chat "):
            chat_message = message.split(" ", 1)[1]
            print(f"Operação 'Chat' com mensagem: {chat_message}")
            with self.lock:
                for sock in self.client_sockets:
                    if sock != client_socket:
                        try:
                            # sock.sendall(chat_message.encode())
                            self.send_message(type=0, content=chat_message, client_socket=sock)
                        except Exception as e:
                            print(f"Erro ao enviar mensagem para o cliente: {e}")
        else:
            print(f"Operação desconhecida: {message}")
            client_socket.sendall(b"0Operacao desconhecida.")

    def send_message(self, type =0, content=b"", filename="", file_size=0, client_socket=None):
        if type == 0:
            header = f"0"
            message = header.encode() + content.encode()
        elif type == 1:
            # file_size deve ser convertido para um inteiro de 4 bytes
            len_filename_b = len(filename).to_bytes(1, 'big', signed=False)  # Tamanho do nome do arquivo como um byte
            file_size_b = file_size.to_bytes(4, 'big', signed=False)
            message = f"1".encode() + len_filename_b + filename.encode() + file_size_b + content
        else:
            print("Tipo de mensagem desconhecido.")
            return
        if client_socket:
            try:
                client_socket.sendall(message)
                # print(f"Mensagem enviada: {message.decode()}")
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                # pass

    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Recebido: {data.decode()}")
                message = data.decode().strip()
                self.handle_request(message, client_socket)
            except (ConnectionResetError, ConnectionAbortedError):
                print("Cliente desconectado inesperadamente")
                break
            except Exception as e:
                break
        if client_socket not in self.client_sockets:
            return
        with self.lock:
            self.client_sockets.remove(client_socket)
        client_socket.close()
        print("Cliente desconectado")

    def stop(self):
        self.running = False
        with self.lock:
            for client_socket in self.client_sockets:
                client_socket.close()
            self.client_sockets.clear()
        if self.server_socket:
            self.server_socket.close()
        print("Servidor encerrado.")
        os._exit(0)

if __name__ == "__main__":
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        print(f"Erro no servidor: {e}")
        server.stop()