import socket
import threading
import os
import hashlib
from datetime import datetime

PORT = 5173
DEVICE_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(DEVICE_NAME)
SOCKET_ADDR = (SERVER_IP, PORT)
EXCHANGE_FORMAT = "utf-8"
HEADER_SIZE = 1024  # Larger header for file metadata
BUFFER_SIZE = 4096  # Buffer size for file transfer (4KB chunks)
UPLOAD_FOLDER = "server_uploads"

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created upload folder: {UPLOAD_FOLDER}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SOCKET_ADDR)
server.listen()
print(f"########## File Transfer Server listening on {SERVER_IP}:{PORT} ##########")
print(f"########## Upload folder: {os.path.abspath(UPLOAD_FOLDER)} ##########\n")

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate file checksum using specified algorithm (md5 or sha256)"""
    if algorithm.lower() == 'md5':
        hash_obj = hashlib.md5()
    else:
        hash_obj = hashlib.sha256()
    
    try:
        with open(filepath, 'rb') as f:
            # Read file in chunks for memory efficiency
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error calculating checksum: {e}")
        return None

def receive_file(conn, client_id, thread_id):
    """Receive file from client with proper error handling"""
    try:
        # Step 1: Receive file metadata (filename, filesize, client_checksum)
        header = conn.recv(HEADER_SIZE).decode(EXCHANGE_FORMAT).strip()
        if not header:
            print(f"[Thread {thread_id}] No header received from client {client_id}")
            return
        
        # Parse header: format is "filename|filesize|client_checksum"
        parts = header.split('|')
        if len(parts) != 3:
            print(f"[Thread {thread_id}] Invalid header format from client {client_id}")
            return
        
        original_filename = parts[0]
        filesize = int(parts[1])
        client_checksum = parts[2]
        
        # Generate unique filename with timestamp and client ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(original_filename)[1]
        base_name = os.path.splitext(original_filename)[0]
        new_filename = f"{base_name}_{timestamp}_client{client_id}{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        
        print(f"[Thread {thread_id}] Receiving file from client {client_id}")
        print(f"[Thread {thread_id}]   Original filename: {original_filename}")
        print(f"[Thread {thread_id}]   File size: {filesize} bytes ({filesize / 1024:.2f} KB)")
        print(f"[Thread {thread_id}]   Saving as: {new_filename}")
        print(f"[Thread {thread_id}]   Client checksum: {client_checksum}")
        
        # Step 2: Receive file data in chunks
        bytes_received = 0
        with open(filepath, 'wb') as f:
            while bytes_received < filesize:
                # Calculate remaining bytes
                remaining = filesize - bytes_received
                # Receive chunk (at most BUFFER_SIZE bytes)
                chunk_size = min(BUFFER_SIZE, remaining)
                chunk = conn.recv(chunk_size)
                
                if not chunk:
                    print(f"[Thread {thread_id}] Connection lost during file transfer")
                    return
                
                f.write(chunk)
                bytes_received += len(chunk)
                
                # Progress indicator
                progress = (bytes_received / filesize) * 100
                if bytes_received % (BUFFER_SIZE * 10) == 0 or bytes_received == filesize:
                    print(f"[Thread {thread_id}]   Progress: {progress:.1f}% ({bytes_received}/{filesize} bytes)")
        
        print(f"[Thread {thread_id}] File received successfully!")
        
        # Step 3: Calculate server-side checksum for verification
        print(f"[Thread {thread_id}] Calculating server-side checksum...")
        server_checksum_sha256 = calculate_checksum(filepath, 'sha256')
        server_checksum_md5 = calculate_checksum(filepath, 'md5')
        
        # Verify file size
        actual_filesize = os.path.getsize(filepath)
        
        # Check if checksums match
        checksum_match = (client_checksum == server_checksum_sha256) or (client_checksum == server_checksum_md5)
        
        print(f"[Thread {thread_id}] Server SHA-256: {server_checksum_sha256}")
        print(f"[Thread {thread_id}] Server MD5: {server_checksum_md5}")
        print(f"[Thread {thread_id}] Checksum verification: {'PASSED' if checksum_match else 'FAILED'}")
        
        # Step 4: Prepare response with file info
        response = (
            f"FILE_RECEIVED_SUCCESSFULLY\n"
            f"Saved filename: {new_filename}\n"
            f"File size: {actual_filesize} bytes ({actual_filesize / 1024:.2f} KB)\n"
            f"SHA-256 checksum: {server_checksum_sha256}\n"
            f"MD5 checksum: {server_checksum_md5}\n"
            f"Checksum verification: {'PASSED' if checksum_match else 'FAILED'}\n"
            f"Timestamp: {timestamp}\n"
            f"Client ID: {client_id}"
        )
        
        # Send response to client
        encoded_response = response.encode(EXCHANGE_FORMAT)
        conn.send(encoded_response)
        
        print(f"[Thread {thread_id}] Response sent to client {client_id}\n")
        
    except Exception as e:
        print(f"[Thread {thread_id}] Error receiving file: {e}\n")
        error_msg = f"ERROR: {str(e)}"
        try:
            conn.send(error_msg.encode(EXCHANGE_FORMAT))
        except:
            pass

def thread_routine(conn, client_addr):
    """Handle each client connection in a separate thread"""
    thread_id = threading.get_ident()
    client_id = f"{client_addr[0]}_{client_addr[1]}"
    
    print(f"[Thread {thread_id}] ########## New connection from {client_addr} ##########")
    
    try:
        receive_file(conn, client_id, thread_id)
    except Exception as e:
        print(f"[Thread {thread_id}] Unexpected error: {e}")
    finally:
        conn.close()
        print(f"[Thread {thread_id}] Connection closed with {client_addr}\n")

# Main server loop
while True:
    try:
        conn, client_addr = server.accept()
        # Create a new thread for each client
        thread = threading.Thread(target=thread_routine, args=(conn, client_addr))
        thread.start()
        print(f"########## Active threads: {threading.active_count() - 1} ##########\n")
    except KeyboardInterrupt:
        print("\n\nServer shutting down...")
        break
    except Exception as e:
        print(f"Error accepting connection: {e}")

server.close()
