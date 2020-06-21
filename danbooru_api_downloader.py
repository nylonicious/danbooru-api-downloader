import asyncio
import re
import os
from pathlib import Path
from sys import version_info
from urllib.parse import unquote, urlparse

import aiohttp


async def queue_downloads(url):
    tags = unquote(url.split('tags=')[1].split('&')[0].replace('+', ' ').strip())
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        counter = 1
        while True:
            async with session.get(f"{url.split('?')[0]}.json", params={'tags': tags, 'page': counter}) as response:
                data = await response.json()
                counter += 1
                if len(data) == 0:
                    break
                else:
                    desired_path = Path.cwd() / re.sub('[<>:\"/|?*]', ' ', tags).strip() / urlparse(url).netloc
                    desired_path.mkdir(parents=True, exist_ok=True)
                    for item in data:
                        if 'file_url' in item:
                            picture_url = item['file_url']
                            picture_name = re.sub('[<>:\"/|?*]', ' ', unquote(urlparse(picture_url).path.split('/')[-1]))
                            picture_path = desired_path / picture_name
                            if not picture_path.is_file():
                                await download(session, picture_url, picture_path)


async def download(session, picture_url, picture_path):
    async with session.get(picture_url) as r:
        if r.status == 200:
            picture_path.write_bytes(await r.read())
            print(f'Downloaded {picture_url}')
        else:
            print(f'Error {r.status} while getting request for {picture_url}')


def main():
    urlinput = input('Otherwise, just type in what tags you want here (Press space for multiple tags): ')
    tags = urlinput.split()
    for t in tags:
        print()
        print("Started scraping " + t)
        os.system("title Scraping " + t)
        asyncio.run(queue_downloads("https://yande.re/post?tags=" + t + "+"))
        asyncio.run(queue_downloads("https://konachan.com/post?tags=" + t + "+"))
        asyncio.run(queue_downloads("https://danbooru.donmai.us/posts?tags=" + t + "+"))


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
    os.system("pause")
