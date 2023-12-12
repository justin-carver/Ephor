from locust import SequentialTaskSet, HttpUser, task, between
import random
import sys

class EasyLoadUserTasks(SequentialTaskSet):
    wait_time = between(5, 15)

    @task
    def upload_file(self):
        file_index = random.randrange(sys.maxsize)
        self.client.post("/upload", files={"file": (f"test_{file_index}.txt", "test data")})

class EasyLoadUser(HttpUser):
    tasks = [EasyLoadUserTasks]

class MedianLoadUserTasks(SequentialTaskSet):
    wait_time = between(1, 5)

    @task
    def upload_file(self):
        file_index = random.randrange(sys.maxsize)
        self.client.post("/upload", files={"file": (f"test_{file_index}.txt", "test data")})

    @task
    def get_file(self):
        if hasattr(self, 'file_index'):
            self.client.get(f"/files/test_{self.file_index}.txt")

class MedianLoadUser(HttpUser):
    tasks = [MedianLoadUserTasks]

class HeavyLoadUserTasks(SequentialTaskSet):
    wait_time = between(0.5, 2)
    deletion_keys = {}

    @task
    def upload_file(self):
        file_index = random.randrange(sys.maxsize)
        with self.client.post("/upload", files={"file": (f"test_{file_index}.txt", "test data")}, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.deletion_keys[data['filename']] = data['deletion_key']
                self.file_index = file_index

    @task
    def get_file(self):
        if hasattr(self, 'file_index'):
            self.client.get(f"/files/test_{self.file_index}.txt")

    @task
    def delete_file(self):
        if self.deletion_keys:
            filename, delete_key = self.deletion_keys.popitem()
            self.client.delete(f"/files/{filename}?key={delete_key}")

class HeavyLoadUser(HttpUser):
    tasks = [HeavyLoadUserTasks]
