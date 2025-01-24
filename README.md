# File Client Manager

## Overview

This repository contains a Python-based client that interacts with a server to perform various file operations such as listing, backing up, restoring, and deleting files. The client reads server information, connects to the server, and sends requests to perform these operations.

## Features

- **Read Server Info**: Reads the server IP and port from a configuration file.
- **Load Backup Files**: Reads the list of files to be backed up from a configuration file.
- **List Files**: Requests the server to list all files belonging to the current user.
- **Backup Files**: Sends a request to the server to back up local files.
- **Restore Files**: Sends a request to the server to retrieve files.
- **Delete Files**: Sends a request to the server to delete files.

## File Structure

- `main.py`: The main program that demonstrates the client simulation.
- `Client.py`: Implements the client class, which handles reading server info, loading backup files, connecting, and sending various requests to the server.
- `FileManager.py`: Provides file-related utilities, including reading server information and handling local file I/O operations.
- `NetworkManager.py`: Manages network connectivity, including creating a socket, connecting to a server, sending and receiving data.
- `constants.py`: Defines client and server constant values, including version numbers, request codes, and response status codes.

## Usage

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/file-client-manager.git
    cd file-client-manager
    ```

2. **Install dependencies**:
    Ensure you have Python installed. You may need to install additional dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure server and backup files**:
    - Create a [server.info](http://_vscodecontentref_/0) file with the server IP and port in the format [ip:port](http://_vscodecontentref_/1).
    - Create a [backup.info](http://_vscodecontentref_/2) file with the list of files to be backed up, one per line.

4. **Run the client**:
    ```bash
    python main.py
    ```

## Example

Here is an example of how to use the client:

1. **Create [server.info](http://_vscodecontentref_/3)**:
    ```
    127.0.0.1:8080
    ```

2. **Create [backup.info](http://_vscodecontentref_/4)**:
    ```
    demofile.txt
    maman14.pdf
    ```

3. **Run the client**:
    ```bash
    python main.py
    ```

## Documentation

Each file and method in the repository is documented with docstrings explaining its purpose, parameters, and returns. Adjust paths and filenames as needed for your environment.

## Author

- **Dmitriy Gorodov**
- **ID**: 342725405
- **Date**: 24/01/2025

## License

This project is licensed under the MIT License - see the LICENSE file for details.