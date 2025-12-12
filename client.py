import socket
import os
import hashlib

PORT = 5173
DEVICE_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(DEVICE_NAME)
SOCKET_ADDR = (SERVER_IP, PORT)
EXCHANGE_FORMAT = "utf-8"
HEADER_SIZE = 1024  # Larger header for file metadata
BUFFER_SIZE = 4096  # Buffer size for file transfer (4KB chunks)

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate file checksum using specified algorithm (md5 or sha256)"""
    if algorithm.lower() == 'md5':
        hash_obj = hashlib.md5()
    else:
        hash_obj = hashlib.sha256()
    
    print(f"Calculating {algorithm.upper()} checksum...")
    try:
        with open(filepath, 'rb') as f:
            # Read file in chunks for memory efficiency
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                hash_obj.update(chunk)
        checksum = hash_obj.hexdigest()
        print(f"{algorithm.upper()} checksum: {checksum}")
        return checksum
    except Exception as e:
        print(f"Error calculating checksum: {e}")
        return None

def send_file(client, filepath):
    """Send file to server with proper error handling"""
    try:
        # Validate file exists
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' does not exist!")
            return False
        
        if not os.path.isfile(filepath):
            print(f"Error: '{filepath}' is not a file!")
            return False
        
        # Get file information
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        print(f"\n########## File Transfer Information ##########")
        print(f"File: {filename}")
        print(f"Size: {filesize} bytes ({filesize / 1024:.2f} KB)")
        print(f"Full path: {os.path.abspath(filepath)}")
        
        # Calculate checksum before sending
        checksum = calculate_checksum(filepath, 'sha256')
        if not checksum:
            print("Failed to calculate checksum!")
            return False
        
        # Prepare and send header with file metadata
        # Format: "filename|filesize|checksum"
        header = f"{filename}|{filesize}|{checksum}"
        header = header + " " * (HEADER_SIZE - len(header))  # Pad to HEADER_SIZE
        client.send(header.encode(EXCHANGE_FORMAT))
        
        print(f"\nSending file to server...")
        
        # Send file data in chunks
        bytes_sent = 0
        with open(filepath, 'rb') as f:
            while bytes_sent < filesize:
                # Read chunk from file
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                
                # Send chunk to server
                client.send(chunk)
                bytes_sent += len(chunk)
                
                # Progress indicator
                progress = (bytes_sent / filesize) * 100
                if bytes_sent % (BUFFER_SIZE * 10) == 0 or bytes_sent == filesize:
                    print(f"Progress: {progress:.1f}% ({bytes_sent}/{filesize} bytes)")
        
        print(f"\n✓ File sent successfully! ({bytes_sent} bytes)\n")
        
        # Receive response from server
        print("Waiting for server response...")
        response = client.recv(4096).decode(EXCHANGE_FORMAT)
        
        print("\n########## Server Response ##########")
        print(response)
        print("####################################\n")
        
        return True
        
    except Exception as e:
        print(f"\nError sending file: {e}\n")
        return False

def main():
    """Main client function"""
    print(f"########## File Transfer Client ##########")
    print(f"Connecting to server at {SERVER_IP}:{PORT}...\n")
    
    try:
        # Create socket and connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(SOCKET_ADDR)
        print(f"✓ Connected to server successfully!\n")
        
        # Get file path from user
        print("Enter the file path to upload:")
        print("(You can drag and drop the file here, or type the path)")
        filepath = input("> ").strip().strip('"').strip("'")
        
        if not filepath:
            print("No file path provided!")
            client.close()
            return
        
        # Send the file
        success = send_file(client, filepath)
        
        # Close connection
        client.close()
        
        if success:
            print("File transfer completed successfully!")
        else:
            print("File transfer failed!")
            
    except ConnectionRefusedError:
        print(f"Error: Could not connect to server at {SERVER_IP}:{PORT}")
        print("Make sure the server is running!")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
