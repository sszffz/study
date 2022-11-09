import requests


url = 'http://artofproblemsolving.com/assets/pythonbook/_static/files/wordlist.txt'
r = requests.get(url, allow_redirects=True)

open('wordlist.txt', 'wb').write(r.content)