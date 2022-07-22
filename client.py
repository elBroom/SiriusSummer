import requests

# POST запрос на IP на порт 5000 на path /auth
resp = requests.post('<YOUR PATH>', json={'name': 'Name', 'surname': 'Surname'})
print(resp.text)

# GET запрос на IP на порт 5000 на path /info/<TOKEN>
resp = requests.get('<YOUR PATH>')
print(resp)

