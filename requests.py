import requests
import json

class Requests:
    def get_mom_joke():
        response = requests.get('https://api.yomomma.info/')
        json_data = json.loads(response.text)
        joke = json_data['joke']
        return joke.lower()

    def get_insult():
        response = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
        json_data = json.loads(response.text)
        insult = json_data['insult']
        return insult.lower()