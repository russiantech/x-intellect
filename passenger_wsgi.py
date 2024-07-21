from web import create_app
from flask import jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Create app instance
# app = create_app('development')  # Set to 'production' if needed
application = create_app('production')  # Set to 'production' if needed

# make site-map
@application.route("/routes")
def site_map():
    links = []
    # for rule in app.url_map.iter_rules():
    for rule in application.url_map._rules:
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        links.append({'url': rule.rule, 'view': rule.endpoint})
    return jsonify(links), 200
    
if __name__ == '__main__':
    application.run("localhost", 8000, True, True)
     
    