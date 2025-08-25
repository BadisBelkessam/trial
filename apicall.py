from dotenv import load_dotenv
import os
import requests

load_dotenv()



# resp = requests.post(
#     "https://trial-git-main-badis-projects-76c64976.vercel.app/api/chat",
#     json={"user_query": "what immobil was found in tipaza"}
# )
# print(resp)



url = "https://trial-git-main-badis-projects-76c64976.vercel.app/chat"
headers = {"Content-Type": "application/json"}
data = {"user_query": "what immobil was found in tipaza"}

response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.text)






# url = "http://127.0.0.1:8000/chat"
# headers = {"Content-Type": "application/json"}
# data = {"user_query": "what immobil was found in tipaza"}

# response = requests.post(url, headers=headers, json=data)
# print(response.status_code, response.text)


