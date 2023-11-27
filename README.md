# Ephor: The Ephemeral Pastebin

Ephor is a RESTful, minimalistic, ephemeral pastebin server designed for quick and secure temporary hosting of documents. It supports both HTTP and HTTPS endpoints and automatically deletes files after a user-defined duration. With its focus on simplicity and lightweight architecture, Ephor is perfect for developers, teams, and individuals seeking an efficient solution for short-term data sharing.

## Features

- **Ephemeral Storage**: Automatically deletes documents after a specified time frame.
- **HTTP/HTTPS Support**: Offers flexibility to host documents over HTTP or HTTPS.
- **Upload & Retrieval API**: Easy-to-use RESTful API for uploading and retrieving documents.
- **Logging**: Maintains logs of server activities, including file uploads and deletions.
- **Debugging Mode**: An option to enable debugging for detailed server logs.
- **File Directory Viewing**: Provides an endpoint to view the list of currently stored files.

## Endpoints

- `POST /upload`: Upload a file with an optional duration (default is 120 seconds). The file will be deleted automatically after this duration.
- `GET /files`: Lists all currently stored files.
- `GET /files/<filename>`: Retrieve a specific file.
- `GET /logs`: View logs of server activities.

#### POST Parameters
- `file=` : The file that will be uploaded to the server
- `duration=` : How long the file will stay active for (in seconds)

## Running the Server

1. **Normal Mode**:
   ```bash
   python3 ephor.py
   ```
2. **Debug Mode**:
   ```bash
   python3 ephor.py --debug
   ```
3. **HTTPS Mode** (requires `cert.pem` and `key.pem`):
   ```bash
   python3 ephor.py --https
   ```

## Installation

Ensure you have Python and Flask installed. Place your SSL certificate (`cert.pem`) and key (`key.pem`) in the same directory as the script for HTTPS support. Do NOT expose these to the public! Register with local CA to prevent self-signed warnings.


## Examples
The following examples are via `curl`. You can use Postman or other REST-based clients.

```
(POST)
curl -X POST -F "file=@/directory/banana.md" -F "duration=60" http://127.0.0.1:5000/upload
```

```
(GET)
curl -X GET http://127.0.0.1:5000/files/banana.md
```

To bypass self-signed warnings in `curl`:
```
curl -k -X POST/GET ...
```

## Contributing

Contributions, feedback, and suggestions are welcome! Please feel free to fork the repository, make changes, and submit pull requests.