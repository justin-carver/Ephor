from flask import Flask, abort, request, send_from_directory, jsonify
import json
import argparse
import os
import queue
import threading
import time
import uuid

app = Flask(__name__)

ALLOWED_EXTENSIONS = set()
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

deletion_keys = []
q = queue.Queue()
stop_thread = threading.Event()

flags = {
    'UNIQUE': False
}

def delete_file_after_delay(filename, delay):
    time.sleep(delay)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    app.logger.info('Deleting file (%ds): %s', delay, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
        return True, 'Successfully deleted: %s' % filename
    else:
        error = 'Unable to delete file: %s. File not found.' % filename
        app.logger.info(error)
        return False, error

def producer_queue_del(q, filename, delay):
    q.put((filename, delay))

def consumer_queue_del(q):
    while not stop_thread.is_set():
        try:
            filename, delay = q.get(timeout=3)
            delete_file_after_delay(filename, delay)
            q.task_done()
        except queue.Empty:
            continue

def stop_consumer():
    stop_thread.set()
    con_thread.join()

def load_allowed_extensions():
    global ALLOWED_EXTENSIONS
    try:
        with open('extensions.json', 'r') as f:
            data = json.load(f)
            ALLOWED_EXTENSIONS = set(data["allowed_extensions"])
    except FileNotFoundError:
        app.logger.error("extensions.json file not found.")
        ALLOWED_EXTENSIONS = set()
    except json.JSONDecodeError:
        app.logger.error("Error decoding extensions.json.")
        ALLOWED_EXTENSIONS = set()

def is_extension_allowed(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

# Routes ---
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file or not is_extension_allowed(file.filename):
        return jsonify({'message': 'File extension not allowed'}), 400

    delay = int(request.form.get('duration', 120)) # default delay
    filename = file.filename if not flags['UNIQUE'] else f"{int(time.time() * 1000000)}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    app.logger.info('Successfully uploaded: %s. Removing after %d seconds', filename, delay)

    prod_thread = threading.Thread(target=producer_queue_del, args=(q, filename, delay))
    prod_thread.start()

    delete_key = str(uuid.uuid4())
    deletion_keys.append(delete_key)

    return jsonify({'message': 'File uploaded successfully',
                    'filename': filename, 'deletion_key': delete_key})

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/files/<filename>', methods=['GET', 'DELETE'])
def get_file(filename):
    if request.method == 'DELETE':
        delete_key_str = request.args.get('key')
        if not delete_key_str:
            app.logger.error('No deletion key provided. Bad Request.')
            return jsonify({'message': 'No deletion key provided'}), 400

        if delete_key_str not in deletion_keys:
            app.logger.error('Deletion key not found or invalid. Key: %s on File: %s', delete_key_str, filename)
            return jsonify({'message': 'Deletion key not found or invalid.'}), 403

        try:
            success, message = delete_file_after_delay(filename, 0)  # manual file deletion
            if success:
                app.logger.info('Manually deleted \'%s\' using key %s', filename, delete_key_str)
                return jsonify({'message': message}), 200
            else:
                app.logger.error('Failed to delete file \'%s\' using key %s', filename, delete_key_str)
                return jsonify({'message': message}), 500  # Internal Server Error
        except Exception as e:
            app.logger.error('Unexpected error occurred: %s', str(e))
            return jsonify({'message': 'Internal Server Error'}), 500

    if request.method == 'GET':
        if filename not in os.listdir(UPLOAD_FOLDER):
            app.logger.error('Attempted to find: %s. File not found!', filename)
            return abort(404)
        return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debugging on server')
    parser.add_argument('--https', action='store_true', help='Run server with HTTPS')
    parser.add_argument('--unique', action='store_true', help='Enforces unique file names')
    args = parser.parse_args()
    
    load_allowed_extensions() # prepare 

    con_thread = threading.Thread(target=consumer_queue_del, args=(q,))
    con_thread.start() # start consumer thread

    if args.unique: flags['UNIQUE'] = True # more flags to come
    if args.https:
        try:
            app.run(debug=args.debug, ssl_context=('cert.pem', 'key.pem'), use_reloader=False, host='0.0.0.0')
            app.logger.info('Starting server in HTTPS mode!')
        except Exception as e:
            app.logger.error('Issue attempting to start server in HTTPS mode...')
            app.logger.error(e)
    else:
        app.run(debug=args.debug, use_reloader=False, host='0.0.0.0')
        app.logger.info('Starting server!')