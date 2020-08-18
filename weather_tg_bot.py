import flask
import requests
import asyncio
import aiohttp
from urllib.parse import urlencode

app = flask.Flask(__name__)

TG_TOKEN = ''
WEATHER_KEY = 'cd83b9fb3661155ca1fab99cdcd359a9'
QUERY_URL = 'http://api.weatherstack.com/current'


def get_weather(query):
    params = {
        'access_key': WEATHER_KEY,
        'query': query
    }
    response = requests.get('http://api.weatherstack.com/current', params)
    print(response)
    return f"Сейчас в местности {query} {response.json()['current']['temperature']} градус(-а, -ов)"

def get_weather_async(city_list: list) -> list:
    async def donwload_aio(urls):
        async def download(url):
            # print(f"Start downloading {url}")
            async with aiohttp.ClientSession() as s:
                resp = await s.get(url)
                if resp.status == 200:
                    out = await resp.json()
                else:
                    out = {}
            print(out)
            return out

        return await asyncio.gather(*[download(url) for url in urls])

    urls = []
    for city in city_list:
        url =  QUERY_URL+'?'+urlencode({"access_key": WEATHER_KEY, "query": city})

        urls.append(url)

    urls_response = asyncio.run(donwload_aio(urls))

    return urls_response


@app.route('/', methods=['GET', 'POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        print(flask.request.json)

        chat_id = flask.request.json['message']['chat']['id']
        request_text = flask.request.json['message']['text']
        weather_response = get_weather(request_text)

        for response in get_weather_async(request_text.split(',')):
            print(f"Сейчас в местности {response['location']['name']} {response['current']['temperature']} градус(-а, -ов)")
        print('!!!!')

        method = "sendMessage"
        url = f"https://api.telegram.org/bot{TG_TOKEN}/{method}"
        data = {
            'chat_id': chat_id,
            'text': weather_response
        }
        requests.post(url, data=data)

    return None


URI = ''

if __name__ == '__main__':
    requests.get("https://api.telegram.org/bot{}/setWebhook?url={}".format(TG_TOKEN, URI))
    app.run()
