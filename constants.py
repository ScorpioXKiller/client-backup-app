"""
@file constants.py
@brief Defines client and server constant values, including version numbers, request codes, and response status codes.
@author Dmitriy Gorodov
@id 342725405
@date 24/01/2025
"""


# Client version
CLIENT_VERSION = 1
# User ID length in bits
USER_ID_LENGTH = 32

# Request Codes
BACKUP_FILE = 100
RESTORE_FILE = 200
DELETE_FILE = 201
LIST_FILES = 202

# Response Status Codes
SUCCESS_FOUND = 210
SUCCESS_FILE_LIST = 211
SUCCESS_NO_PAYLOAD = 212
ERR_FILE_NOT_FOUND = 1001
ERR_NO_FILES = 1002
ERR_GENERAL = 1003