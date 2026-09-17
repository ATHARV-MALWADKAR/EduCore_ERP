import requests
import traceback
try:
    response = requests.post("http://localhost:8000/api/v1/auth/login", data={"username":"admin@college.edu", "password":"admin123"})
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(traceback.format_exc())
