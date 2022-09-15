from functools import wraps
import base64, json


def cookie_parser(cookie_string):
    splitPairs = {}
    if cookie_string:
        pairs = cookie_string.split(";")
        for item in pairs:
            values = item.strip().split("=")
            splitPairs[values[0]] = values[1]
        return splitPairs

def pre_open(self, *args, **kwargs):
    cookiesstring = self.request.headers.get('Cookie')
    if cookiesstring:
        cookies = cookie_parser(cookiesstring)
        if 'connect.sid' in cookies:
            st_user = { 'email': cookies['connect.sid'], 'isPublicCloudApp': False}
            self.request.headers['X-Streamlit-User'] = base64.b64encode(json.dumps(st_user).encode('utf-8')).decode()

def inject_pre(f, pre):
    @wraps(f)
    def w(*args, **kwargs): 
        pre(*args, *kwargs)
        return f(*args, **kwargs)
    return w

def patch():    
    from streamlit.web.server.browser_websocket_handler import BrowserWebSocketHandler
    BrowserWebSocketHandler.open = inject_pre(BrowserWebSocketHandler.open, pre_open)

# copied from streamlit/__main__.py
from streamlit.web.cli import main
if __name__ == "__main__":
    patch()
    main(prog_name="streamlit")