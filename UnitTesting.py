import unittest
from app import app, Game

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Route Testing

    def test_homepage(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register_route(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_login_route(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    # Function Testing

    def test_algorithm_function(self):
        game = Game('X', 0, 1)
        game.previous_move = [1, 1]  # Set a previous move for testing
        result = game.algorithm()
        self.assertIsNotNone(result)

    # Edge Case Testing

    def test_invalid_aimatch(self):
        response = self.app.post('/aimatch', data=dict(row_col='33'))
        self.assertEqual(response.json['status'], 'error')

    def test_valid_aimatch(self):
        response = self.app.post('/aimatch', data=dict(row_col='11'))
        self.assertEqual(response.json['status'], 'next_move')

    def test_invalid_player1_move(self):
        response = self.app.post('/player1', data=dict(row_col='11'))
        self.assertEqual(response.json['status'], 'error')

    def test_valid_player1_move(self):
        response = self.app.post('/player1', data=dict(row_col='00'))
        self.assertEqual(response.json['status'], 'next_move')

    def test_invalid_player2_move(self):
        response = self.app.post('/player2', data=dict(row_col='11'))
        self.assertEqual(response.json['status'], 'error')

    def test_valid_player2_move(self):
        response = self.app.post('/player2', data=dict(row_col='00'))
        self.assertEqual(response.json['status'], 'next_move')

if __name__ == '__main__':
    unittest.main()
