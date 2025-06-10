import socket
import os
import threading

class Server: 
    def __init__(self, host='localhost', port=6363):
        self.host = host
        self.port = port
        self.running = True
        self.server_socket = None
        self.client_sockets = []
        self.running = True
        self.lock = threading.Lock()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor conectado com {self.host}:{self.port}")

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexao com {addr}")
            with self.lock:
                self.client_sockets.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            # Lê e responde com Hello World
            request = client_socket.recv(1024).decode()
            print(f"Recebido:\n{request}")
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Content-Length: 11\r\n"
                "Connection: close\r\n"
                "\r\n"
                "Hello World"
            )
            client_socket.sendall(response.encode())
        finally:
            client_socket.close()
            with self.lock:
                self.client_sockets.remove(client_socket)

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