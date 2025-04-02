package main

import (
	"fmt"
	"log"
	"net"
)

const (
	port = ":8080"
)

func create_socket() net.PacketConn {
	conn, err := net.ListenPacket("udp", port)
	if err != nil {
		log.Fatal("Error:", err)
	}
	log.Println("Server is listening on port", port)
	return conn
}

func send_data(conn net.PacketConn, addr net.Addr) {
	_, err := conn.WriteTo([]byte("Message received"), addr)
	if err != nil {
		log.Println("Error sending response: ", err)
	}
}

func listen_clients(conn net.PacketConn, buffer []byte) {
	for {
		n, addr, err := conn.ReadFrom(buffer)
		if err != nil {
			log.Println("Error reading from udp client: ", err)
			continue
		}
		fmt.Println("Message: ", string(buffer[:n]))
		send_data(conn, addr)
	}
}

func main() {
	conn := create_socket()
	buffer := make([]byte, 1024)
	listen_clients(conn, buffer)
	defer conn.Close()
}
