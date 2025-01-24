"""
@file NetworkManager.py
@brief Manages network connectivity, including creating a socket, connecting to a server, sending and receiving data.
       It provides helper functions for forming and parsing header data, and reading exact byte counts.
@details Each method contains docstrings explaining its purpose, parameters, and returns.
         Adjust IP addresses, ports, and other parameters as needed for your environment.
@author Dmitriy Gorodov
@id 342725405
@date 24/01/2025
"""

import socket
import struct

class NetworkManager:
    """
    @class NetworkManager
    @brief A utility class for managing network connections, sending and receiving data, and handling protocol headers.
    """
    def __init__(self):
        """
        @brief Constructs a NetworkManager instance.
        Initializes the socket to None.
        """
        self.sock = None

    def connect(self, ip, port):
        """
        @brief Establishes a socket connection to the specified IP and port.
        @param ip The IP address of the server to connect to.
        @param port The port number of the server to connect to.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))

    def close(self):
        """
        @brief Closes the socket connection if it is open.
        """
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_all(self, data):
        """
        @brief Sends all the data over the socket connection.
        @param data The data to be sent.
        """
        self.sock.sendall(data)

    def recv(self, size):
        """
        @brief Receives data from the socket connection.
        @param size The maximum amount of data to be received.
        @return The received data.
        """
        return self.sock.recv(size)

    def recv_exact(self, num_bytes):
        """
        @brief Receives exactly the specified number of bytes from the socket connection.
        @param num_bytes The exact number of bytes to be received.
        @return The received data or None if the connection is closed.
        """
        buf = b''
        while len(buf) < num_bytes:
            chunk = self.sock.recv(num_bytes - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def build_header(self, user_id, version, op_code, filename=None):
        """
        @brief Builds a protocol header for a request.
        @param user_id The user ID to include in the header.
        @param version The client version to include in the header.
        @param op_code The operation code to include in the header.
        @param filename Optional filename to include in the header.
        @return The constructed header as bytes.
        """
        header = struct.pack("<I", user_id)
        header += struct.pack("<B", version)
        header += struct.pack("<B", op_code)
        if filename:
            encoded_filename = filename.encode('ascii')
            header += struct.pack("<H", len(encoded_filename))
            header += encoded_filename
        else:
            header += struct.pack("<H", 0)
        return header