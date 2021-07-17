import os
from avito_clone import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')