'Shortens the screenshot URL'
import bitly_api

def get_connection():
    """Create a Connection base on username and access token credentials"""
    # access_token = os.getenv(BITLY_ACCESS_TOKEN)
    return bitly_api.Connection(access_token="0dab6b9201bba86875e0a5dbe52a77c39649caf1")

conn = get_connection()
short = conn.shorten('http://google.com')
print short
