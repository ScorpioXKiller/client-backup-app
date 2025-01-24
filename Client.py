"""
@file Client.py
@brief Implements the client class, which handles reading server info, loading backup files, connecting,
       and sending various requests to the server (list, backup, restore, delete).
@details This file demonstrates how to interact with the server using different operations such as
         listing files, backing up local files to the server, restoring them, or deleting them.
         Each method contains docstrings explaining its purpose and usage.
@author Dmitriy Gorodov
@id 342725405
@date 24/01/2025
"""

import random
import struct
import os
import constants

from FileManager import FileManager
from NetworkManager import NetworkManager

class Client:
    """
    @class Client
    @brief Represents a client that connects to the server and sends requests to perform operations with files.
    """
    def __init__(self):
        """
        @brief Constructs a Client instance.
        Initializes the user ID, client version, and helper managers for file and network operations.
        """
        self.user_id = random.getrandbits(constants.USER_ID_LENGTH)
        self.version = constants.CLIENT_VERSION
        self.server_ip = None
        self.server_port = None
        self.file_manager = FileManager()
        self.network_client = NetworkManager()
        self.files_to_backup = []

    def read_server_info(self, filename="server.info"):
        """
        @brief Reads the server IP and port from a file.
        @param filename The path to the file containing server information (default "server.info").
        """
        ip, port = self.file_manager.read_server_info(filename)
        self.server_ip = ip
        self.server_port = port

    def load_backup_files(self, filename="backup.info"):
        """
        @brief Loads the list of files to be backed up from a file.
        @param filename The path to the file containing names of backup files (default "backup.info").
        """
        self.files_to_backup = self.file_manager.read_backup_files(filename)

    def connect(self):
        """
        @brief Establishes a socket connection to the server using the NetworkManager.
        """
        self.network_client.connect(self.server_ip, self.server_port)
        print(f"Connected to {self.server_ip}:{self.server_port}")

    def close(self):
        """
        @brief Closes the socket connection.
        """
        self.network_client.close()
        print("Connection closed.")

    def _send_request(self, op_code, filename=None, file_path=None):
        """
        @brief Sends a request header (and payload if applicable) to the server.
        @param op_code The code describing the operation (e.g. backup, list, etc.).
        @param filename Optional filename to send in the request header.
        @param file_path If sending a file (e.g., backup), the local path of that file.
        """
        header = self.network_client.build_header(self.user_id, self.version, op_code, filename)
        self.network_client.send_all(header)
        if op_code == constants.BACKUP_FILE and file_path:
            file_size = os.path.getsize(file_path)
            size_header = struct.pack("<I", file_size)
            self.network_client.send_all(size_header)
            for chunk in self.file_manager.read_file_chunks(file_path):
                self.network_client.send_all(chunk)

    def _receive_response(self):
        """
        @brief Receives and parses the server's response header and optional payload.
        @return A dictionary containing the server's response (version, status, filename, payload, etc.).
        """
        data = self.network_client.recv_exact(1)
        if not data:
            return None
        server_version = struct.unpack("<B", data)[0]

        data = self.network_client.recv_exact(2)
        if not data:
            return None
        status = struct.unpack("<H", data)[0]

        data = self.network_client.recv_exact(2)
        if not data:
            return None
        name_len = struct.unpack("<H", data)[0]

        filename = None
        if name_len > 0:
            data = self.network_client.recv_exact(name_len)
            if not data:
                return None
            filename = data.decode('ascii', errors='replace')

        size = None
        payload = None
        if status in (constants.SUCCESS_FOUND, constants.SUCCESS_FILE_LIST):
            data = self.network_client.recv_exact(4)
            if not data:
                return None
            size = struct.unpack("<I", data)[0]
            if size > 0:
                payload = self.network_client.recv_exact(size)

        return {
            'version': server_version,
            'status': status,
            'name_len': name_len,
            'filename': filename,
            'size': size,
            'payload': payload
        }

    def request_backup_file(self, file_name):
        """
        @brief Sends a request to back up a local file on the server.
        @param file_name The local file path to upload to the server.
        """
        print(f"--- Saving file '{file_name}' ---")
        self._send_request(op_code=constants.BACKUP_FILE, filename=file_name, file_path=file_name)
        resp = self._receive_response()
        print("Response:", {k: resp[k] for k in resp if not k.startswith(('size', 'payload'))})
        print("\n")

    def request_restore_file(self, file_name, save_as=None):
        """
        @brief Sends a request to retrieve a file from the server.
        @param file_name The name of the file to retrieve from the server.
        @param save_as Optional local file path to save the retrieved data, defaults to file_name.
        """
        print(f"--- Restoring file '{file_name}' ---")
        self._send_request(op_code=constants.RESTORE_FILE, filename=file_name)
        resp = self._receive_response()

        if resp.get('status') == constants.ERR_FILE_NOT_FOUND:
            print(f"File '{file_name}' not found on the server.")
            print("Response:", {k: resp[k] for k in resp if not k.startswith(('size', 'payload'))})
        elif resp.get('status') == constants.ERR_GENERAL:
            print("Fatal error: server failed to restore file.")
            print("Response:", {k: resp[k] for k in ('version', 'status')})
        else:
            if not save_as:
                save_as = file_name

            self.file_manager.write_file(save_as, resp['payload'])
            print(f"Restored '{file_name}' to '{save_as}'.")
            resp['payload'] = ' '.join(f"{byte:02x}" for byte in resp['payload'])
            print("Response:", resp)
        print("\n")

    def request_delete_file(self, file_name):
        """
        @brief Sends a request to delete a file from the server's storage.
        @param file_name The name of the file to be deleted on the server.
        """
        print(f"--- Deleting file '{file_name}' ---")
        self._send_request(op_code=constants.DELETE_FILE, filename=file_name)
        resp = self._receive_response()

        if resp.get('status') == constants.ERR_FILE_NOT_FOUND:
            print(f"File '{file_name}' not found on the server.")
            print("Response:", {k: resp[k] for k in resp if not k.startswith(('size', 'payload'))})
        elif resp.get('status') == constants.ERR_GENERAL:
            print("Fatal error: server failed to delete file.")
            print("Response:", {k: resp[k] for k in ('version', 'status')})
        else:
            print(f"File deleted successfully.")
            print("Response:", {k: resp[k] for k in resp if not k.startswith(('size', 'payload'))})
        print("\n")

    def request_list_files(self):
        """
        @brief Sends a request to the server for a list of all files belonging to the current user.
        """
        print("--- Requesting list of files ---")
        self._send_request(op_code=constants.LIST_FILES)
        resp = self._receive_response()

        if resp.get('status') == constants.ERR_NO_FILES:
            print("No files found on the server.")
            print("Response:", {k: resp[k] for k in ('version', 'status')})
        elif resp.get('status') == constants.ERR_GENERAL:
            print("Fatal error: server failed to list files.")
            print("Response:", {k: resp[k] for k in ('version', 'status')})
        else:
            print("--- List of files ---")
            if resp['payload']:
                print(resp['payload'].decode('ascii', errors='replace'))

            print("--- End of list ---")
            resp['payload'] = ' '.join(f"{byte:02x}" for byte in resp['payload'])
            print("Response:", resp)
        print("\n")
