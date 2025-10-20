import requests
r = requests.post("http://127.0.0.1:8000/add_item", json={"name":"apple","price":30.0})
print(r.status_code, r.text)
