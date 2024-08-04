from dotenv import load_dotenv, find_dotenv
from os import getenv

load_dotenv(find_dotenv())

# Define OAuth provider configurations
providers = {
    'google': {
        'consumer_key': getenv('GOOGLE_CLIENT_ID'),
        'consumer_secret': getenv('GOOGLE_CLIENT_SECRET'), #YOUR_CLIENT_SECRET
        'base_url': 'https://www.googleapis.com/oauth2/v1/',
        'request_token_params': {
            'scope': 'email',
        },
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
    },
    # Add more providers
}

#OAUTH2_PROVIDERS = {
oauth2providers = {
    # Google OAuth 2.0 documentation:
    # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
    'google': {
        'client_id': getenv('GOOGLE_CLIENT_ID'),
        'client_secret': getenv('GOOGLE_CLIENT_SECRET'),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },

    # GitHub OAuth 2.0 documentation:
    # https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
    'github': {
        'client_id': getenv('github_client_id'),
        'client_secret': getenv('github_client_secret'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo': {
            'url': 'https://api.github.com/user/emails',
            'email': lambda json: json[0]['email'],
        },
        'scopes': ['user:email'],
    },
}