import requests

url = "http://127.0.0.1:8000/process-form/"

# Replace with actual path to your test form image
files = {"image": open("reference_form.png", "rb")}

response = requests.post(url, files=files)
print(response.json())