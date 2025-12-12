# Task 5: Client-Server File Transfer System

## Overview
A robust file transfer system that allows clients to upload files to a server with integrity verification using checksums.

## Features Implemented

### Core Requirements ✓
1. **File Selection & Transfer**
   - Client can select any file from their system
   - Files are transferred in chunks (4KB buffer) for memory efficiency
   - Supports files of any size

2. **Server Storage with Metadata**
   - Files saved with timestamp: `filename_YYYYMMDD_HHMMSS_clientIP_PORT.ext`
   - Client ID embedded in filename for tracking
   - All uploads stored in `server_uploads/` folder

3. **Checksum Verification**
   - Supports both **SHA-256** and **MD5** algorithms
   - Client calculates checksum before sending
   - Server recalculates and verifies after receiving
   - Returns both SHA-256 and MD5 checksums to client

4. **Advanced Features**
   - **Partial reads handling**: Uses fixed-size buffer (4KB) for chunk-based transfer
   - **Large buffer support**: Configurable BUFFER_SIZE for optimal performance
   - **Memory safety**: Reads and writes in chunks, never loading entire file into memory
   - **Progress tracking**: Real-time progress indicators for both client and server
   - **Multi-threading**: Server handles multiple simultaneous uploads
   - **Error handling**: Comprehensive exception handling and validation

## File Structure
```
task5/
├── server.py          # File transfer server
├── client.py          # File transfer client
├── README.md          # This file
└── server_uploads/    # Created automatically - stores uploaded files
```

## How to Run

### 1. Start the Server
```bash
python server.py
```
Output:
```
########## File Transfer Server listening on 192.168.x.x:5173 ##########
########## Upload folder: f:\BRACU\11th Sem\cse421\lab03\Socket Programming\task5\server_uploads ##########
```

### 2. Run the Client
```bash
python client.py
```

### 3. Upload a File
When prompted, enter the file path:
- You can drag and drop the file into the terminal
- Or type/paste the full path
- Example: `C:\Users\YourName\Documents\test.txt`

## Example Output

### Client Output:
```
########## File Transfer Client ##########
Connecting to server at 192.168.1.100:5173...

✓ Connected to server successfully!

Enter the file path to upload:
> C:\Users\test\document.pdf

########## File Transfer Information ##########
File: document.pdf
Size: 524288 bytes (512.00 KB)
Full path: C:\Users\test\document.pdf
Calculating SHA-256 checksum...
SHA-256 checksum: a1b2c3d4e5f6...

Sending file to server...
Progress: 10.0% (52428/524288 bytes)
Progress: 20.0% (104856/524288 bytes)
...
Progress: 100.0% (524288/524288 bytes)

✓ File sent successfully! (524288 bytes)

Waiting for server response...

########## Server Response ##########
FILE_RECEIVED_SUCCESSFULLY
Saved filename: document_20251213_143022_client192.168.1.101_54321.pdf
File size: 524288 bytes (512.00 KB)
SHA-256 checksum: a1b2c3d4e5f6...
MD5 checksum: f1e2d3c4b5a6...
Checksum verification: PASSED
Timestamp: 20251213_143022
Client ID: 192.168.1.101_54321
####################################

File transfer completed successfully!
```

### Server Output:
```
[Thread 12345] ########## New connection from ('192.168.1.101', 54321) ##########
[Thread 12345] Receiving file from client 192.168.1.101_54321
[Thread 12345]   Original filename: document.pdf
[Thread 12345]   File size: 524288 bytes (512.00 KB)
[Thread 12345]   Saving as: document_20251213_143022_client192.168.1.101_54321.pdf
[Thread 12345]   Client checksum: a1b2c3d4e5f6...
[Thread 12345]   Progress: 10.0% (52428/524288 bytes)
[Thread 12345]   Progress: 20.0% (104856/524288 bytes)
...
[Thread 12345]   Progress: 100.0% (524288/524288 bytes)
[Thread 12345] File received successfully!
[Thread 12345] Calculating server-side checksum...
[Thread 12345] Server SHA-256: a1b2c3d4e5f6...
[Thread 12345] Server MD5: f1e2d3c4b5a6...
[Thread 12345] Checksum verification: PASSED
[Thread 12345] Response sent to client 192.168.1.101_54321
[Thread 12345] Connection closed with ('192.168.1.101', 54321)
```

## Technical Implementation Details

### Memory Safety
- **Chunk-based transfer**: Files are never loaded entirely into memory
- **Buffer size**: 4KB (4096 bytes) - optimal for most systems
- **Streaming**: Both reading and writing use streaming with fixed buffers

### Partial Read Handling
```python
while bytes_received < filesize:
    remaining = filesize - bytes_received
    chunk_size = min(BUFFER_SIZE, remaining)
    chunk = conn.recv(chunk_size)
    # ... process chunk
```

### Checksum Algorithms
- **SHA-256**: 256-bit cryptographic hash (more secure)
- **MD5**: 128-bit hash (faster, but less secure)
- Both calculated in chunks for memory efficiency

### Multi-threading
- Each client connection handled in separate thread
- Server can process multiple uploads simultaneously
- Thread-safe file operations

### Error Handling
- Connection loss detection
- File validation (exists, is file, readable)
- Checksum verification
- Comprehensive exception handling

## Testing Scenarios

1. **Small Text File** (< 1KB)
   - Quick transfer, instant checksum

2. **Medium Document** (1-10 MB)
   - Progress tracking visible
   - Checksum calculation noticeable

3. **Large File** (> 100 MB)
   - Demonstrates chunk-based transfer
   - Memory usage remains constant
   - Progress updates throughout transfer

4. **Multiple Simultaneous Uploads**
   - Run multiple clients at once
   - Each handled in separate thread
   - No interference between transfers

## Configuration

Modify these constants in both files:
```python
PORT = 5173                # Server port
BUFFER_SIZE = 4096         # Transfer chunk size (4KB)
HEADER_SIZE = 1024         # Metadata header size
```

## Key Advantages

✓ **Memory Efficient**: Fixed memory usage regardless of file size
✓ **Reliable**: Checksum verification ensures file integrity
✓ **Scalable**: Multi-threaded design handles concurrent uploads
✓ **Traceable**: Files timestamped with client information
✓ **Robust**: Comprehensive error handling and validation
✓ **Flexible**: Supports both MD5 and SHA-256 checksums
