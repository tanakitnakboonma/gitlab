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

    def test_page_uses_mockup_layout(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Input Parameters", html)
        self.assertIn("Circuit: Common-Emitter Amplifier", html)
        self.assertIn("DC Bias Results", html)
        self.assertIn("Week 2 Goal", html)

    def test_page_states_model_assumptions(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Model assumptions", html)
        self.assertIn("constant β", html)
        self.assertIn("ideal resistors", html)

    def test_post_valid_shows_results(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("1.942", html)
        self.assertIn("8.052", html)

    def test_post_active_shows_ok_status(self):
        html = self.post().get_data(as_text=True)
        self.assertIn("Active region approximation OK", html)

    def test_post_invalid_shows_error(self):
        response = self.post(r1="0")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('class="error"', html)
        self.assertIn("R1", html)
        self.assertIn("มากกว่าศูนย์", html)

    def test_post_blank_field_shows_error(self):
        html = self.post(r1="").get_data(as_text=True)
        self.assertIn('class="error"', html)
        self.assertIn("R1", html)

    def test_post_missing_field_shows_error(self):
        data = {"vcc": "12", "r1": "100", "rc": "2.2",
                "re": "1", "beta": "100", "vbe": "0.70"}
        response = self.client.post("/calculate", data=data)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('class="error"', html)
        self.assertIn("R2", html)

    def test_post_keeps_submitted_values(self):
        html = self.post(r1="0").get_data(as_text=True)
        self.assertIn('name="r1"', html)
        self.assertIn('value="0"', html)

    def test_post_cutoff_shows_warning(self):
        html = self.post(r2="1").get_data(as_text=True)
        self.assertIn('class="warning"', html)
        self.assertIn("Cutoff", html)
        self.assertIn("ไม่ใช่ค่าที่ใช้ได้จริง", html)

    def test_post_saturation_shows_warning(self):
        html = self.post(re="0.1").get_data(as_text=True)
        self.assertIn('class="warning"', html)
        self.assertIn("Saturation", html)
        self.assertIn("ไม่น่าเชื่อถือ", html)

    def test_units_and_stylesheet_are_linked(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("kΩ", html)
        self.assertIn('rel="stylesheet"', html)
        static_response = self.client.get("/static/style.css")
        self.assertEqual(static_response.status_code, 200)
        static_response.close()


if __name__ == "__main__":
    unittest.main()
