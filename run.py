#!/usr/bin/env python3
"""Run the Flask application."""

import os
from src.app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5001))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )