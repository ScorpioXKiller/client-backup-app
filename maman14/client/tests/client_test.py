import socket
import os
import random
import struct

class BackupClient:
    def __init__(self):
        self.user_id = random.getrandbits(32)
        self.version = 1
        self.server_ip = None
        self.server_port = None
        self.sock = None

    def read_server_info(self, filename="maman14/server.info"):
        with open(filename, "r") as f:
            line = f.read().strip()
            ip_part, port_part = line.split(":")
            self.server_ip = ip_part
            self.server_port = int(port_part)

    def read_backup_info(self, filename="maman14/backup.info"):
        with open(filename, "r") as f:
            self.backup_files = f.read().strip().split("\n")

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[Client] Connecting to server at {self.server_ip}:{self.server_port}...")
            self.sock.connect((self.server_ip, self.server_port))
            print("[Client] Connected.")
        except Exception as e:
            print(f"Error connecting to server: {e}")

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("[Client] Connection closed.")
            
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
        Receive and parse the server's response:

        Response Header (little-endian):
            version  (1 byte)
            status   (2 bytes)
            name_len (2 bytes)
            filename (name_len bytes, ASCII)

        Possible payload (if status in [210, 211]):
            size     (4 bytes)
            payload  (size bytes)
        """
        # 1) Read 1 byte for 'version'
        data = self.sock.recv(1)
        if not data:
            print("No response (version) received.")
            return None
        server_version = struct.unpack("<B", data)[0]

        # 2) Read 2 bytes for 'status'
        data = self.sock.recv(2)
        if not data:
            print("No response (status) received.")
            return None
        status = struct.unpack("<H", data)[0]

        # 3) Read 2 bytes for 'name_len'
        data = self.sock.recv(2)
        if not data:
            print("No response (name_len) received.")
            return None
        name_len = struct.unpack("<H", data)[0]

        # 4) If name_len > 0, read 'filename'
        filename = None
        if name_len > 0:
            data = self.sock.recv(name_len)
            if not data:
                print("No response (filename) received.")
                return None
            filename = data.decode('ascii', errors='replace')

        # Prepare to store 'size' and 'payload'
        size = None
        payload = None

        # -- Decide if we need to read size+payload --
        # For status = 210 or 211 -> we have size & payload
        # For status = 212, 1001, 1002, 1003 -> no size/payload
        if status in (210, 211):
            # 5) Read the 4-byte 'size'
            data = self.sock.recv(4)
            if not data:
                print("No response (size) received for payload.")
                return None
            size = struct.unpack("<I", data)[0]

            # 6) Read 'payload' of length 'size'
            if size > 0:
                payload = self.sock.recv(size)
                if not payload:
                    print("No payload data received.")
                    return None

        # Return the parsed response as a dictionary
        response_dict = {
            'version':   server_version,
            'status':    status,
            'filename':  filename,
            'size':      size,
            'payload':   payload
        }

        return response_dict
    
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

    def backup_file(self, filename):
        if not os.path.isfile(filename):
            print(f"Error: File '{filename}' does not exist.")
            return

        try:
            request_line = f"BACKUP:{self.user_id}:{filename}\n"
            self.sock.sendall(request_line.encode('utf-8'))
            print(f"[Client] Sent backup request for user={self.user_id}, file={filename}")

            # 2) Wait for server's "READY" response
            ready_response =  self.sock.recv(1024).decode('utf-8')
            if ready_response != "READY":
                print("[Client] Server did not respond with READY. Exiting.")
                return
            else:
                print("[Client] Server is ready to receive the file.")

            # 3) Send the file in chunks
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    self.sock.sendall(chunk)

            print("[Client] File data sent successfully.")

        except Exception as e:
            print(f"Error sending request: {e}")