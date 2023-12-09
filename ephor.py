from flask import Flask, abort, request, send_from_directory, jsonify
import argparse
import datetime
import os
import queue
import threading
import time
import uuid

app = Flask(__name__)

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

@app.route('/logs', methods=['GET'])
def show_logs():
    return jsonify(logs)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    delay = int(request.form.get('duration', 120)) # default delay
    filename = file.filename if not flags['UNIQUE'] else str('%s_%s' % (int(time.time() * 1000000), file.filename))
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    app.logger.info('Successfully uploaded: %s. Removing after %d seconds', filename, delay)

    prod_thread = threading.Thread(target=producer_queue_del, args=(q, filename, delay))
    prod_thread.start()

    delete_key = str(uuid.uuid4())
    deletion_keys.append(delete_key)

    return jsonify({'message': 'File uploaded successfully', \
    'filename': filename, 'deletion_key': delete_key})

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/files/<filename>', methods=['GET', 'DELETE'])
def get_file(filename):
    if request.method == 'DELETE':
        try:
            delete_key_str = request.args.get('key')
            delete_key = uuid.UUID(delete_key_str)
        except ValueError:
            app.logger.error('Invalid key type request; key used: %s', delete_key_str)
            return abort(400)

        if delete_key_str in deletion_keys:
            success, message = delete_file_after_delay(filename, 0) # manual file deletion
            if success:
                app.logger.info('Manually deleted \'%s\' using key %s' % (filename, delete_key_str))
                return jsonify({'message': message}), 200
            else:
                app.logger.error('Unable to delete file, delete key invalid. Key used: %s' % delete_key_str)
                return jsonify({'message': message}), 404
        else:
            app.logger.error('Unable to delete file, no key found.')
            return jsonify({'message': 'Unable to delete file, no key found.'}), 404

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

    con_thread = threading.Thread(target=consumer_queue_del, args=(q,))
    con_thread.start() # start consumer thread

    if args.unique: flags['UNIQUE'] = True
    if args.https:
        try:
            app.run(debug=args.debug, ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0')
            app.logger.info('Starting server in HTTPS mode!')
        except Exception as e:
            app.logger.info('Issue attempting to start server in HTTPS mode...')
            app.logger.error(e)
    else:
        app.run(debug=args.debug, host='0.0.0.0')
        app.logger.info('Starting server!')