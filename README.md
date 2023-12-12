# Ephor: Ephemeral Pastebin Service

Ephor is a sleek, ephemeral pastebin service crafted for secure and transient document hosting. Engineered with RESTful principles, Ephor caters to developers and teams who need a reliable platform for temporary data exchange. Supporting both HTTP and HTTPS, Ephor stands out with its user-centric design that prioritizes ease of use and security.

## Key Features

- **Transient File Storage**: Automates the deletion of documents post a user-specified lifespan.
- **Dual Protocol Support**: Facilitates document hosting via HTTP or HTTPS, ensuring versatility.
- **RESTful API**: Streamlined API endpoints for document upload and retrieval processes.
- **Activity Logging**: Comprehensive logging of server actions, including document lifecycle events.
- **Debugging Support**: Offers a debugging mode for in-depth server operation insights.
- **Directory Listing**: Endpoint availability to inspect the list of present documents.

## API Endpoints

- `POST /upload` - Uploads a document with an optional lifespan (defaults to 120 seconds).
- `DELETE /files/<filename>?key={UUID}` - Allows manual document deletion using a unique key.
- `GET /files` - Enumerates all stored documents.
- `GET /files/<filename>` - Facilitates retrieval of a specific document.
- `GET /logs` - Accesses logs of server operations.

### POST Parameters

- `file` - The document to be uploaded.
- `duration` - The active duration of the document on the server (in seconds).

## Getting Started

### Prerequisites

- Python 3.11.6 or higher
- Flask
- SSL certificate (`cert.pem`) and key (`key.pem`) for HTTPS setup.

### Setup and Installation

1. Ensure Python and `pip` are installed on your system.
2. Install Flask using `pip`:
   ```bash
   pip install flask
   ```

### Launching the Server

1. **Standard Mode**:
   ```bash
   python3 ephor.py
   ```
2. **Debug Mode** (for detailed logging):
   ```bash
   python3 ephor.py --debug
   ```
3. **HTTPS Mode** (requires SSL certificates, enables unique filenames):
   ```bash
   python3 ephor.py --https --unique
   ```

## Interacting with the Server

Utilize `curl` for command-line interactions, or opt for any RESTful client like Postman.

Upload a document:
```bash
curl -X POST -F "file=@/path/to/document.txt" -F "duration=60" http://127.0.0.1:5000/upload
```

Retrieve a document(s):
```bash
curl -X GET http://127.0.0.1:5000/files
curl -X GET http://127.0.0.1:5000/files/document.txt
```

Delete a document:
```bash
curl -X DELETE http://127.0.0.1:5000/files/document.txt\?key\=72772ee2-b0f7-4a32-8f13-756640c108c7
```

> Note: Use `curl -k` to ignore self-signed SSL warnings during local testing.

## How to Contribute

Your contributions make Ephor better! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Commit your changes.
4. Push to your branch.
5. Submit a pull request.

We appreciate your input and are open to your ideas and feedback.