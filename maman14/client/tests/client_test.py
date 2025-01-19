import socket
import os
import random

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