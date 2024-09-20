import requests

# URL of your Flask app's endpoint
url = 'https://lono.pythonanywhere.com/chat'

# Sample query data
data = {
    'query': 'What is artificial intelligence?'
}

# Send POST request to the endpoint
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Print the JSON response from the server
    print(response.json())
else:
    print(f"Error: Received status code {response.status_code}")
