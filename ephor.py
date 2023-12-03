from flask import Flask, abort, request, send_from_directory, jsonify
import argparse
import datetime
import os
import threading
import time
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logs = [{str(datetime.datetime.now()): 'Server started! 🎉'}] # init logs
deletion_keys = [] # init deletion keys

@app.route('/logs', methods=['GET'])
def show_logs(): # upload / delete logs
    return jsonify(logs)

def delete_file_after_delay(filename, delay):
    time.sleep(delay)
    app.logger.info('Deleting file (%ds): %s', delay, filename)
    logs.append({str(datetime.datetime.now()): 'Deleted file %s after %d seconds' % (filename, delay)})
    if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
    else:
        error = 'Unable to delete file: %s. File not found.' % filename
        app.logger.info(error)
        logs.append({str(datetime.datetime.now()): error})
        return jsonify({'message': error})

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    duration = int(request.form.get('duration', 120))  # Default duration: 120 seconds
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Successful load
    app.logger.info('Succesfully uploaded: %s. Removing after %d seconds', filename, duration)
    logs.append({str(datetime.datetime.now()): 'Successfully uploaded %s' % (filename)})

    # Start a thread to delete the file after the specified duration
    thread = threading.Thread(target=delete_file_after_delay, args=(filename, duration))
    thread.start()

    delete_key = uuid.uuid4()
    deletion_keys.append(delete_key)

    return jsonify({'message': 'File uploaded successfully', 'filename': filename, 'deletion_key': delete_key})

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/files/<filename>', methods=['GET', 'DELETE'])
def get_file(filename):
    if request.method == 'DELETE':
        delete_key = request.args.get('key')
        if delete_key.length > 0 and delete_key in deletion_keys: # deletion called
            status = delete_file_after_delay(filename, 0)
            if 'message' in status:
                return jsonify({'message': status.message})
            else:
                return jsonify({'message': 'Successfully deleted: %s' % filename})
    if request.method == 'GET':
        if filename not in os.listdir(UPLOAD_FOLDER):
            app.logger.info('Attempted to find: %s. File not found!', filename)
            return abort(404)
        return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debugging on server')
    parser.add_argument('--https', action='store_true', help='Run server with HTTPS')
    args = parser.parse_args()

    if args.https:
        app.run(debug=args.debug, ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0')
        logs.append({str(datetime.datetime.now()): "Running server on HTTPS!"})
    else:
        app.run(debug=args.debug, host='0.0.0.0')