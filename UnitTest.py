import unittest
from flask import session
from ytr import app


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_main_route(self):
        with self.app as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)

    def test_login(self):
        with self.app as client:
            response = client.post('/api/login', data=dict(username='admin', password='admin'))
            self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        with self.app as client:
            response = client.post('/api/login', data=dict(username='invaliduser', password='invalidpassword'))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid username or password', response.data)

    def test_register(self):
        with self.app as client:
            response = client.post('/api/register', data=dict(username='newuser', password='newpassword'))
            self.assertEqual(response.status_code, 200)

    def test_logout(self):
        with self.app as client:
            with client:
                client.post('/api/login', data=dict(username='testuser', password='testpassword'))
                response = client.get('/api/logout')
                self.assertEqual(response.status_code, 200)

    def test_prizes_view(self):
        with self.app as client:
            with client:
                client.post('/api/login', data=dict(username='testuser', password='testpassword'))
                response = client.get('/prizes')
                self.assertEqual(response.status_code, 200)

    def test_boards(self):
        with self.app as client:
            with client:
                client.post('/api/login', data=dict(username='testuser', password='testpassword'))
                response = client.get('/api/boards')
                self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
