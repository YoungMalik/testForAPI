from locust import HttpUser, task, between

class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post("/register", json={"email": "loadtest@example.com", "password": "pass123"})
        response = self.client.post("/token", data={"username": "loadtest@example.com", "password": "pass123"})
        self.token = response.json()["access_token"]

    @task(3)
    def create_short_link(self):
        self.client.post(
            "/links/shorten",
            json={"original_url": "https://example.com"},
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def redirect(self):
        self.client.get("/abc123")  # Предполагаем существующий short_code