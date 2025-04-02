package main

import (
	"fmt"
	"net"
)

func main() {
	// Create a raw UDP socket
	conn, err := net.ListenPacket("udp", "")
	if err != nil {
		fmt.Println("Error creating socket:", err)
		return
	}
	defer conn.Close()

	serverAddr, err := net.ResolveUDPAddr("udp", ":8080")
	if err != nil {
		fmt.Println("Error resolving server address:", err)
		return
	}

	message := []byte("Hello, UDP Server!")

	// Manually send the packet
	_, err = conn.WriteTo(message, serverAddr)
	if err != nil {
		fmt.Println("Error sending packet:", err)
		return
	}
	fmt.Println("Message sent to server")

	// Manually receive response
	buffer := make([]byte, 1024)
	n, _, err := conn.ReadFrom(buffer)
	if err != nil {
		fmt.Println("Error reading response:", err)
		return
	}
	fmt.Println("Server response:", string(buffer[:n]))
}
