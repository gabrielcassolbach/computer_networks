import socket
import struct
import os
import hashlib
import threading 
import queue
import time

TIMEOUT = 1

class server:
    def __init__(self, host='10.181.3.212', port=6363):
        self.host = host
        self.port = port
        self.running = True

        self.client_ack_queues = {}  # Maps client address to Queue
        self.lock = threading.Lock()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))

    def start(self):
        print(f"Servidor UDP iniciado {self.host}:{self.port}.")
        threading.Thread(target=self.receiver_thread, daemon=True).start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Encerrando servidor...")
            self.running = False

    def receiver_thread(self):
        while self.running:
            try:
                data, client_address = self.server_socket.recvfrom(1024)
                
                if self.is_ack(data):
                    with self.lock:
                        if client_address in self.client_ack_queues:
                            self.client_ack_queues[client_address].put(data)

                elif self.is_get_request(data):
                    file_path = data.decode().split("/", 1)[1]
                    self.start_file_transfer(file_path, client_address)
                
            except Exception as e:
                print(f"Erro no receiver: {e}")

    def is_get_request(self, data):
        return True if data.decode().startswith("GET/") else False

    def is_ack(self, data):
        if len(data) != 4:
            return False
        try:
            ack_seq = struct.unpack('!I', data[:4])[0]
            return isinstance(ack_seq, int) and 0 <= ack_seq
        except struct.error:
            return False
                 
    def start_file_transfer(self, file_path, client_address):
        ack_queue = queue.Queue()
        with self.lock:
            self.client_ack_queues[client_address] = ack_queue

        thread = threading.Thread(
            target=self.send_file,
            args=(file_path, client_address, ack_queue),
            daemon=True
        )
        thread.start()

   
    def send_file(self, file_path, client_address, ack_queue):
        if not os.path.exists(file_path):
            print(f"Arquivo {file_path} não encontrado.")
            self.server_socket.sendto(b"NOTFOUND", client_address)
            return
        file_size = os.path.getsize(file_path)
        self.server_socket.sendto(struct.pack('!Q', file_size), client_address)
        print(f"Arquivo {file_path} de {file_size} bytes enviado para {client_address}.")
        
        seq = 0
        with open(file_path, 'rb') as f:
            while True:
                file = f.read(900) # arquivo inteiro quebrado em pacotes de 200 bytes
                if not file:
                    break
                    
                hash = hashlib.sha256(file).digest()
            
                header = struct.pack('!II32s', seq, len(file), hash) # cabeçalho com numero de sequência, tamanho do pacote e hash
                packet = header + file # adiciona o cabeçalho no pacote

                # envia e aguarda ACK
                while True:
                    self.server_socket.sendto(packet, client_address)
                    try:
                        ack_data = ack_queue.get(timeout=TIMEOUT)
                        ack_seq = struct.unpack('!I', ack_data[:4])[0]
                        if ack_seq == seq:
                            break  # próximo pacote
                    except queue.Empty:
                        print(f"Timeout: Ack do pacote {seq} não recebido. Reenviando...")
                        continue  # retransmite
                seq += 1
        
        print("Envio concluído.")
        with self.lock:
            del self.client_ack_queues[client_address]
         
def main():
    server_instance = server()
    server_instance.start()
    
if __name__ == "__main__":
    main()