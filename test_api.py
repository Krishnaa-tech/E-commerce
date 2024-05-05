import unittest
from app import app, db, Product

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        cls.app_context.pop()

    def test_get_products(self):
        response = self.app.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_create_product(self):
        data = {'title': 'Test Product', 'description': 'Test Description', 'price': 10.99}
        response = self.app.post('/products', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

        data_missing_fields = {'description': 'Test Description', 'price': 10.99}
        response_missing_fields = self.app.post('/products', json=data_missing_fields)
        self.assertEqual(response_missing_fields.status_code, 400)
        self.assertEqual(response_missing_fields.json, {'error': 'Missing required fields (title, price)'})

        data_invalid_types = {'title': 123, 'description': 'Test Description', 'price': 'invalid'}
        response_invalid_types = self.app.post('/products', json=data_invalid_types)
        self.assertEqual(response_invalid_types.status_code, 400)
        self.assertEqual(response_invalid_types.json, {'error': 'Invalid data types for title or price'})

    def test_get_product(self):
        response = self.app.get('/products/1')
        self.assertEqual(response.status_code, 404)

    def test_update_product(self):
        data = {'title': 'Updated Title', 'description': 'Updated Description', 'price': 20.99}
        response = self.app.put('/products/1', json=data)
        self.assertEqual(response.status_code, 404)

    def test_delete_product(self):
        response = self.app.delete('/products/1')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
