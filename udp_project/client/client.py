import socket
import struct
import sys
import os
import hashlib
import random
import numpy as np
import select

SERVER_IP='10.181.3.212'
SERVER_PORT=6363
TIMEOUT = 5

class client:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def request_file(self, file_name, debug=False):
        message = f"GET/{file_name}"
        self.server_socket.sendto(message.encode(), (self.host, self.port))

        if debug:
            print("Modo de simulacao de perda ativado.")
            self._debug_receive_file(file_name + ".received")
        else:
            self._receive_file(file_name + ".received")
        

    def _receive_file(self, file_name):
        ready = select.select([self.server_socket], [], [], TIMEOUT)
        if not ready[0]:
            print("SERVER NOT FOUND!")
            return
        data, _ = self.server_socket.recvfrom(1024)
        message = struct.unpack('!Q', data)[0] 
        message_str = message.to_bytes(8, 'big').decode('utf-8')
        if(message_str == "NOTFOUND"):
            print("Erro: Arquivo nâo encontrado!")
            return
        total_size = message
        bytes_length_packets = -1
        seq = -1

        with open(file_name, 'wb') as f:
            while seq != int(np.ceil(total_size/bytes_length_packets) - 1):
                ready = select.select([self.server_socket], [], [], TIMEOUT)
                if not ready[0]:
                    print("SERVER IS DOWN!")
                    return
                packet, _ = self.server_socket.recvfrom(1024)  
                new_seq, bytes_length, hash = struct.unpack('!II32s', packet[:40])
            
                bytes_length_packets = max(bytes_length_packets, bytes_length)
                data = packet[40:]
                
                # Hash verification
                calculated_hash = hashlib.sha256(data).digest()
                if calculated_hash != hash:
                    print(f"Erro: Hash do pacote {seq} não confere.")
                    break
                    
                if seq+1 == new_seq:
                    seq = new_seq
                    f.write(data)

                ack = struct.pack('!I', new_seq)
                self.server_socket.sendto(ack, (self.host, self.port))
        
        print(f"Arquivo {file_name} recebido com sucesso.")

    def _debug_receive_file(self, file_name):
        ready = select.select([self.server_socket], [], [], TIMEOUT)
        if not ready[0]:
            print("SERVER NOT FOUND!")
            return
        data, _ = self.server_socket.recvfrom(1024)
        total_size = struct.unpack('!Q', data)[0] 

        bytes_length_packets = -1
        seq = -1 # sorry. a qtd de pacotes é total_size/900
        random_seq = random.randint(0, int(total_size/900) - 1)

        print(random_seq)

        with open(file_name, 'wb') as f:
            
            while seq != int(np.ceil(total_size/bytes_length_packets) - 1):
                ready = select.select([self.server_socket], [], [], TIMEOUT)
                if not ready[0]:
                    print("SERVER IS DOWN!")
                    return
                packet, _ = self.server_socket.recvfrom(1024)  
                new_seq, bytes_length, hash = struct.unpack('!II32s', packet[:40])
            
                bytes_length_packets = max(bytes_length_packets, bytes_length)
                data = packet[40:]
                
                # Debugging
                if(new_seq == random_seq):
                    print(f"Simulando perda de pacote: {seq}")
                    random_seq = -1
                    continue
                    
                # Hash verification
                calculated_hash = hashlib.sha256(data).digest()
                if calculated_hash != hash:
                    print(f"Erro: Hash do pacote {seq} não confere.")
                    break
                    
                if seq+1 == new_seq:
                    seq = new_seq
                    f.write(data)

                ack = struct.pack('!I', new_seq)
                self.server_socket.sendto(ack, (self.host, self.port))


# acho que ajustei o debug=True bora testar com qual arquivo?

def main():
    # Parse command line arguments
    if len(sys.argv) != 2:
        print("Uso: python client.py <nome_do_arquivo>")
        sys.exit(1)

    file_name = sys.argv[1]
    client_instance = client()
    client_instance.request_file(file_name, debug=False) # Modo de simulação de perda ativado

if __name__ == "__main__":
    main()