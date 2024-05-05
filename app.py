from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

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
    # Retrieve query parameters for pagination
    limit = request.args.get('limit', default=10, type=int)  # Default limit to 10 items per page
    skip = request.args.get('skip', default=0, type=int)

    # Query for products with pagination
    products = Product.query.limit(limit).offset(skip).all()

    # Return paginated results
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
