import requests


body = requests.get("http://numbersapi.com/371/math")
print(body.text)