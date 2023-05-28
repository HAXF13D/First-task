import requests

r = requests.post('http://127.0.0.1:8000/questions/', json={'questions_amount': '4'})
print(r.status_code)
