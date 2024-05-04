from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import unittest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.id}>'

# Routes
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'title': p.title, 'description': p.description, 'price': p.price} for p in products])

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({'id': product.id, 'title': product.title, 'description': product.description, 'price': product.price})

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    if 'title' not in data or 'price' not in data:
        return jsonify({'error': 'Missing required fields (title, price)'}), 400

    title = data.get('title')
    price = data.get('price')

    if not isinstance(title, str) or not isinstance(price, (int, float)):
        return jsonify({'error': 'Invalid data types for title or price'}), 400

    description = data.get('description', None)

    try:
        product = Product(title=title, description=description, price=price)
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'id': product.id}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    if 'title' in data:
        product.title = data['title']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']

    try:
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500


# Error Handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_get_products(self):
        # Test case for retrieving products when the database is empty
        response = self.app.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

        # Test case for retrieving products when the database has entries
        # You may need to add products to the database for this test

    def test_create_product(self):
        # Test case for creating a product with valid data
        data = {'title': 'Test Product', 'description': 'Test Description', 'price': 10.99}
        response = self.app.post('/products', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

        # Test case for creating a product with missing required fields
        data_missing_fields = {'description': 'Test Description', 'price': 10.99}
        response_missing_fields = self.app.post('/products', json=data_missing_fields)
        self.assertEqual(response_missing_fields.status_code, 400)
        self.assertEqual(response_missing_fields.json, {'error': 'Missing required fields (title, price)'})

        # Test case for creating a product with invalid data types
        data_invalid_types = {'title': 123, 'description': 'Test Description', 'price': 'invalid'}
        response_invalid_types = self.app.post('/products', json=data_invalid_types)
        self.assertEqual(response_invalid_types.status_code, 400)
        self.assertEqual(response_invalid_types.json, {'error': 'Invalid data types for title or price'})

    def test_get_product(self):
        # Test case for retrieving an existing product
        # You may need to add a product to the database for this test
        response = self.app.get('/products/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)

        # Test case for retrieving a non-existing product
        response_non_existing = self.app.get('/products/1000')
        self.assertEqual(response_non_existing.status_code, 404)
        self.assertEqual(response_non_existing.json, {'error': 'Not found'})

    def test_update_product(self):
        # Test case for updating an existing product
        # You may need to add a product to the database for this test
        data = {'title': 'Updated Title', 'description': 'Updated Description', 'price': 20.99}
        response = self.app.put('/products/1', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Product updated successfully'})

        # Test case for updating a non-existing product
        data_non_existing = {'title': 'Updated Title', 'description': 'Updated Description', 'price': 20.99}
        response_non_existing = self.app.put('/products/1000', json=data_non_existing)
        self.assertEqual(response_non_existing.status_code, 404)
        self.assertEqual(response_non_existing.json, {'error': 'Not found'})

    def test_delete_product(self):
        # Test case for deleting an existing product
        # You may need to add a product to the database for this test
        response = self.app.delete('/products/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Product deleted successfully'})

        # Test case for deleting a non-existing product
        response_non_existing = self.app.delete('/products/1000')
        self.assertEqual(response_non_existing.status_code, 404)
        self.assertEqual(response_non_existing.json, {'error': 'Not found'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
