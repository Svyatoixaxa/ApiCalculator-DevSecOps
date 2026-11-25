import unittest

from fastapi.testclient import TestClient
from main import app, APP_VERSION

client = TestClient(app)


class CalculatorTests(unittest.TestCase):
    def test_operations(self):
        for path, a, b, expected in [
            ("add", 2, 3, 5), ("subtract", 2, 3, -1),
            ("multiply", 2.5, 4, 10), ("divide", 7, 2, 3.5),
            ("power", 2, 3, 8), ("mod", 7, 3, 1),
        ]:
            with self.subTest(path=path):
                response = client.get(f"/{path}", params={"a": a, "b": b})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"result": expected})

    def test_zero_divisor(self):
        for path in ("divide", "mod"):
            with self.subTest(path=path):
                self.assertEqual(client.get(f"/{path}?a=1&b=0").status_code, 400)

    def test_bad_input(self):
        for query in ("a=hello&b=1", "a=1", "a=NaN&b=1", "a=inf&b=1", "a=1&b=-inf"):
            with self.subTest(query=query):
                self.assertEqual(client.get(f"/add?{query}").status_code, 422)

    def test_out_of_range(self):
        for path in ("/power?a=-1&b=0.5", "/power?a=0&b=-1", "/power?a=10&b=1000",
                     "/multiply?a=1e308&b=1e308", "/add?a=1e308&b=1e308",
                     "/divide?a=1e308&b=1e-308"):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 400)

    def test_version(self):
        self.assertEqual(client.get("/version").json(), {"version": APP_VERSION})
        self.assertEqual(client.get("/openapi.json").json()["info"]["version"], APP_VERSION)

    def test_home_and_docs(self):
        self.assertEqual(client.get("/").status_code, 200)
        self.assertEqual(client.get("/docs").status_code, 200)


if __name__ == "__main__":
    unittest.main()
