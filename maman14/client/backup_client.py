import os
import socket
import struct
import random

class BackupClient:
    """
    A client that implements the described backup protocol over TCP.
    """

    def __init__(self):
        """
        Initialize client variables but do not connect yet.
        """
        # Generate a unique 4-byte random number (unsigned 32-bit).
        self.user_id = random.getrandbits(32)
        
        # Using version 1 as an example.
        self.version = 1
        
        self.server_ip = None
        self.server_port = None
        self.backup_files = []
        self.sock = None

    def read_server_info(self, filename="maman14/server.info"):
        """
        Reads the server address and port from the 'server.info' file.
        Format: IP:PORT
        Example line: 127.0.0.1:1234
        """
        with open(filename, "r") as f:
            line = f.read().strip()
            ip_part, port_part = line.split(":")
            self.server_ip = ip_part
            self.server_port = int(port_part)

    def read_backup_info(self, filename="maman14/backup.info"):
        """
        Reads the filenames (one per line) from 'backup.info'.
        These files are the ones to be backed up.
        """
        with open(filename, "r") as f:
            lines = f.readlines()
            self.backup_files = [line.strip() for line in lines if line.strip()]

    def connect(self):
        """
        Create a TCP socket and connect to the server.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_port))
        print(f"Connected to server at {self.server_ip}:{self.server_port}")

    def close(self):
        """
        Close the TCP socket.
        """
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Connection closed.")

    def _build_header(self, op_code, filename=None):
        """
        Build the request header according to the specification:

        Header fields (binary, little-endian):
          - user_id  (4 bytes)
          - version  (1 byte)
          - op       (1 byte)
          - name_len (2 bytes) -> length of filename (if any)
          - filename (variable) -> ASCII, no null terminator
        """
        # user_id (4 bytes, little-endian unsigned)
        header = struct.pack("<I", self.user_id)

        # version (1 byte, e.g., 1)
        header += struct.pack("<B", self.version)

        # op code (1 byte)
        header += struct.pack("<B", op_code)

        if filename:
            encoded_filename = filename.encode('ascii')  # or 'utf-8' if needed
            name_len = len(encoded_filename)
            # name_len (2 bytes, little-endian)
            header += struct.pack("<H", name_len)
            # filename (name_len bytes, ASCII)
            header += encoded_filename
        else:
            # If there's no filename, name_len = 0
            header += struct.pack("<H", 0)
            # no filename content appended

        return header

    def _build_save_payload(self, file_path):
        """
        Build the payload for saving a file (op=100).
        Payload structure (binary, little-endian):
          - size (4 bytes) -> size of file
          - payload (file content)
        """
        file_size = os.path.getsize(file_path)
        # First, 4 bytes representing the file size.
        payload_header = struct.pack("<I", file_size)
        return payload_header  # The actual file data is sent separately in chunks.

    def _send_request(self, op_code, filename=None, file_path=None):
        """
        Send a request to the server.
        For 'save file' (op=100), also include the file data after the header.
        """
        # Build the header
        header = self._build_header(op_code, filename)

        print(f"Sending request header: {header}")
        
        # Send header
        self.sock.sendall(header)

        if op_code == 100 and file_path:
            # Build and send payload header (size)
            payload_header = self._build_save_payload(file_path)
            self.sock.sendall(payload_header)

            # Send file data in chunks
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    self.sock.sendall(chunk)

    def _receive_response(self):
        """
        Receive a response from the server.
        We do not have a fully specified format for the response,
        so we treat it in a simplified manner:
          - First 4 bytes might contain 'response length' or 'status code'.
          - Then read the rest accordingly.
        """
        try:
            # Try to read 4 bytes (some minimal header).
            data = self._recv_exact(1)
            if not data:
                print("No response (version) received.")
                return None
            
            sercer_version = struct.unpack("<B", data)[0]

            data = self._recv_exact(2)
            if not data:
                print("No response (status) received.")
                return None
            
            status = struct.unpack("<B", data)[0]

            if status in (1001, 1002, 1003):
                print(f"Server error: {status}")
                return {"version": sercer_version, "status": status}

            data = self._recv_exact(2)
            if not data:
                print("No response (name_len) received.")
                return None
            
            name_len = struct.unpack("<H", data)[0]
            filename = None
            if name_len > 0:
                data = self._recv_exact(name_len)
                if not data:
                    print("No response (filename) received.")
                    return None
                filename = data.decode('ascii', errors='replace')

            size = None
            payload = None

            if status in (210, 211):
                data = self._recv_exact(4)
                if not data:
                    print("No response (size) received for payload.")
                    return None
                size = struct.unpack("<I", data)[0]

                if size > 0:
                    payload = self._recv_exact(size)
                    if not payload:
                        print("No payload data received.")
                        return None
                    
            return {
                'version': sercer_version,
                'status': status,
                'filename': filename,
                'size': size,
                'payload': payload
            }

        except Exception as e:
            print(f"Error processing server response: {e}")
            return None

    def _recv_exact(self, num_bytes):
        """
        Helper to read exactly num_bytes from the socket.
        Returns the bytes read or None if there's an error or closed connection.
        """
        buf = b''
        while len(buf) < num_bytes:
            chunk = self.sock.recv(num_bytes - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def request_list_files(self):
        """
        Send a request (op=202) to list files for this client.
        """
        print("\n--- Requesting file list from server (op=202) ---")
        self._send_request(op_code=202, filename=None)
        response = self._receive_response()
        
        if response and response["status"] == 211:  # LIST_RETURNED
            print("File list received:")
            if response["payload"]:
                file_list = response["payload"].decode("utf-8").splitlines()
                for file_name in file_list:
                    print(f"- {file_name}")
            else:
                print("No files available on the server.")
        elif response:
            print(f"Error response from server: {response}")
        else:
            print("No response or error occurred during list request.")

    def request_save_file(self, file_name):
        """
        Send a request (op=100) to save (backup) a file on the server.
        """
        print(f"\n--- Saving file '{file_name}' (op=100) ---")
        self._send_request(op_code=100, filename=file_name, file_path=file_name)
        response = self._receive_response()
        if response:
            print("Server response:", response)
        else:
            print("Error or no response for save request.")

    def request_retrieve_file(self, file_name):
        """
        Send a request (op=200) to retrieve a file.
        If received, save content to 'tmp'.
        """
        print(f"\n--- Retrieving file '{file_name}' (op=200) ---")
        self._send_request(op_code=200, filename=file_name)
        
        # Read file size from server (4 bytes).
        header_bytes = self._recv_exact(4)
        if not header_bytes:
            print("No response header for retrieval.")
            return
        file_size = struct.unpack("<I", header_bytes)[0]

        if file_size == 0:
            # Possibly an error or no file
            # The server may send an error message next
            error_msg = self._receive_response()
            if error_msg:
                print("Server response:", error_msg)
            else:
                print("Server indicated file size = 0. No file retrieved.")
            return

        # Otherwise, read the file in chunks
        print(f"Server indicated file size: {file_size} bytes.")
        with open("tmp", "wb") as out_file:
            remaining = file_size
            while remaining > 0:
                chunk_size = min(4096, remaining)
                chunk = self.sock.recv(chunk_size)
                if not chunk:
                    print("Connection lost while retrieving file.")
                    break
                out_file.write(chunk)
                remaining -= len(chunk)

        # (Optional) read additional response if the server sends it
        trailing_msg = self._receive_response()
        if trailing_msg:
            print("Server trailing message:", trailing_msg)

        print(f"File '{file_name}' saved as 'tmp'.")

    def request_delete_file(self, file_name):
        """
        Send a request (op=201) to delete a file from the server.
        """
        print(f"\n--- Deleting file '{file_name}' (op=201) ---")
        self._send_request(op_code=201, filename=file_name)
        response = self._receive_response()
        if response:
            print("Server response:", response)
        else:
            print("Error or no response for delete request.")


    def test_simple_message(self):
        """
        Test sending a simple message to the server and receiving a response.
        """
        try:
            # Send a simple message
            message = "Hello from client"
            self.sock.sendall(message.encode('utf-8'))
            print(f"Sent to server: {message}")

            # Receive the response
            response = self._recv_exact(1024).decode('utf-8').strip()
            print(f"Received from server: {response}")
        except Exception as e:
            print(f"Error during simple message test: {e}")
