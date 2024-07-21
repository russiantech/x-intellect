from web import create_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = create_app('development')  # Set to 'production' if needed
# app = create_app('production')  # Set to 'production' if needed

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
    