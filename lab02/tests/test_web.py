import unittest

from app import app


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def post(self, **overrides):
        data = {
            "vcc": "12", "r1": "100", "r2": "22", "rc": "2.2",
            "re": "1", "beta": "100", "vbe": "0.70",
        }
        data.update(overrides)
        return self.client.post("/calculate", data=data)

    def test_get_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for field in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{field}"', html)

    def test_post_valid_shows_results(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("1.942", html)
        self.assertIn("8.052", html)

    def test_post_invalid_shows_error(self):
        response = self.post(r1="0")
        self.assertEqual(response.status_code, 200)
        self.assertIn("มากกว่าศูนย์", response.get_data(as_text=True))

    def test_post_cutoff_shows_warning(self):
        html = self.post(r2="1").get_data(as_text=True)
        self.assertIn("Cutoff", html)


if __name__ == "__main__":
    unittest.main()
