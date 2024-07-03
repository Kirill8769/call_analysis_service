import asyncio
import os

import requests
from dotenv import load_dotenv


class GPTHandler:
    """Класс для работы с ChatGPT."""

    def __init__(self):
        load_dotenv()
        proxy_url = os.getenv('PROXY_URL')
        self.__api_key = os.getenv('GPT_API')
        self.__proxies = {'https': proxy_url}
        self.proxy_ip = os.getenv('PROXY_IP')
        self.status_proxy = False

    async def check_proxy(self) -> None:
        """"Метод проверки proxy."""

        self.status_proxy = False
        response_ip = requests.get('https://api.ipify.org?format=json', proxies=self.__proxies)
        if response_ip.status_code == 200:
            my_ip = response_ip.json()['ip']
            if my_ip == self.proxy_ip:
                self.status_proxy = True

    async def get_gpt_balance(self):
        pass

    async def get_gpt_response(self, promt: str) -> str:
        """
        Метод делает запрос к GPT и возвращает ответ.

        :param promt: Запрос в текстовом формате.
        :return: Ответ бота.
        """
        answer = 'Произошла ошибка, повторите пожалуйста ваш вопрос'
        await self.check_proxy()
        if not self.status_proxy:
            raise UserWarning('Ошибка прокси')
        headers = {
            'Authorization': f'Bearer {self.__api_key}',
            "Content-Type": "application/json"
        }
        url = 'https://api.openai.com/v1/chat/completions'
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'user', 'content': promt},
            ],
            # 'max_tokens': 50,
            'temperature': 0.5,
            'top_p': 0.5,
        }
        response = requests.post(url, proxies=self.__proxies, headers=headers, json=data)
        json_answer = response.json()
        answer = json_answer['choices'][0]['message']['content']
        return answer

test = GPTHandler()
print(test.status_proxy)
asyncio.run(test.get_gpt_response('Hello. How are you ?'))
print(test.status_proxy)
