"""
@file FileManager.py
@brief Provides file-related utilities, including reading server information and handling local file I/O operations.
       It supports reading backup file lists, reading file chunks, and writing files locally.
@details Each method contains docstrings explaining its purpose, parameters, and returns.
         Adjust paths and filenames as needed for your environment.
@author Dmitriy Gorodov
@id 342725405
@date 24/01/2025
"""

class FileManager:
    """
    @class FileManager
    @brief A utility class for local file handling, including reading server info, reading backup file lists,
           reading file chunks, and writing files to disk.
    """
    def read_server_info(self, filename):
        """
        @brief Reads server info (IP and port) from a file.
        @param filename The path to the file containing server info in the format "ip:port".
        @return A tuple (ip, port) representing the server address information.
        """
        with open(filename, "r") as f:
            line = f.read().strip()
        ip_part, port_part = line.split(":")
        return ip_part, int(port_part)

    def read_backup_files(self, filename):
        """
        @brief Reads a list of filenames to back up from a file.
        @param filename The path to the file containing filenames (one per line).
        @return A list of filenames.
        """
        with open(filename, "r") as f:
            return f.read().strip().split("\n")

    def read_file_chunks(self, file_path, chunk_size=4096):
        """
        @brief Yields chunks of binary data from a file.
        @param file_path The path to the file to be read.
        @param chunk_size The maximum size of each read chunk (in bytes).
        @yield Byte data of size up to chunk_size from the file.
        """
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def write_file(self, file_path, data):
        """
        @brief Writes binary data to a local file.
        @param file_path The path to the file to write data to.
        @param data The raw bytes to be written to the file.
        @return None
        """
        with open(file_path, "wb") as f:
            f.write(data)