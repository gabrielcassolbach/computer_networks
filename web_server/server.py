import socket
import os
import threading
import mimetypes

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

    def receive_request(self, client_socket):
        request = client_socket.recv(1024).decode()

        request_line = request.splitlines()[0]
        parts = request_line.split()
        if len(parts) < 3:
            return
        
        method, path, version = parts
        print("received: ", method)
        return method, path, version

    def send_error(self, client_socket):
        response = (
            "HTTP/1.1 404 Method Not Allowed\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        client_socket.sendall(response.encode())

    def send_defaultpage(self, client_socket):
        files = os.listdir("www")
        allowed_exts = [".html", ".jpeg"]
        links = ""

        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in allowed_exts and f != "index.html":
                links += f'<li><a href="/{f}">{f}</a></li>\n'

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Available Files</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h1 {{ color: #333; }}
                ul {{ list-style: none; padding-left: 0; }}
                li {{ margin-bottom: 10px; }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Available Files</h1>
            <ul>
                {links}
            </ul>
        </body>
        </html>
        """

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )
        client_socket.sendall(response.encode())

    def handle_client(self, client_socket):
        try:
            method, path, version = self.receive_request(client_socket)
            if method != "GET":
                self.send_error(client_socket)
                return

            file_path = os.path.join("www", path.lstrip("/"))

            if path == "/":
                self.send_defaultpage(client_socket)
                return

            if not os.path.isfile(file_path):
                self.send_error(client_socket)
                return


            with open(file_path, "rb") as f:
                content = f.read()

            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"

            header = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {mime_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client_socket.sendall(header.encode() + content)
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
    network_ip = socket.gethostbyname(socket.gethostname())
    print(f"IP local do servidor: {network_ip}")
    server = Server(host=network_ip, port=6363)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        print(f"Erro no servidor: {e}")
        server.stop()