from app import create_app
from get_products import get_product_info

app = create_app()
with app.app_context():
    get_product_info()