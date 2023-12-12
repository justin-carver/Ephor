from locust import HttpUser, task, between
import random
import sys
import time

class EasyLoadUser(HttpUser):
    wait_time = between(5, 15)

    file_index = None

    @task
    def upload_file(self):
        self.file_index = int(time.time() * 1000000)
        self.client.post("/upload", files={"file": ("test_%d.txt" % self.file_index, "test data")})

class MedianLoadUser(HttpUser):
    wait_time = between(1, 5)

    file_index = None

    @task
    def upload_file(self):
        self.file_index = int(time.time() * 1000000)
        self.client.post("/upload", files={"file": ("test_%d.txt" % self.file_index, "test data")})

    @task
    def get_file(self):
        if self.file_index is not None:
            self.client.get("/files/test_%d.txt" % self.file_index)

class HeavyLoadUser(HttpUser):
    wait_time = between(0.5, 2)

    deletion_keys = {}
    file_index = None

    @task
    def upload_file(self):
        self.file_index = int(time.time() * 1000000)
        with self.client.post("/upload", files={"file": ("test_%d.txt" % self.file_index, "test data")}) as response:
            if response.status_code == 200:
                data = response.json()
                self.deletion_keys[data['filename']] = data['deletion_key']

    @task
    def get_file(self):
        if self.file_index is not None:
            self.client.get("/files/test_%d.txt" % self.file_index)

    @task
    def delete_file(self):
        # You would need to handle the deletion key retrieval and usage here
        # self.client.delete("/files/test.txt?key=UUID_HERE")
        if self.deletion_keys:
            filename, delete_key = self.deletion_keys.popitem()
            self.client.delete(f"/files/{filename}?key={delete_key}")
