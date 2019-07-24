import asyncio
import os
import re
import time
from sys import version_info
from urllib.parse import unquote, urlparse

import aiohttp


class DanbooruAPI:
    def __init__(self, url, page_number):
        self.session = None
        asyncio.run(self.get_picture_urls(url, page_number))

    async def get_picture_urls(self, url, page_number):
        tasks = []
        tags = unquote(url.split('tags=')[1].split('&')[0].replace('+', ' ').strip())
        desiredpath = os.getcwd() + '\\' + re.sub('[<>:\"/|?*]', ' ', tags).strip() + '\\' + urlparse(url).netloc + '\\'
        if not os.path.exists(desiredpath):
            os.makedirs(desiredpath)
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"}
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as self.session:
            for n in range(1, page_number + 1):
                async with self.session.get(f"{url.split('?')[0]}.json", params={'tags': tags, 'page': n}) as response:
                    data = await response.json()
                    if len(data) == 0:
                        print('End of pages')
                        break
                    else:
                        for item in data:
                            if 'file_url' in item:
                                picture_url = item['file_url']
                                picture_name_no_fix = unquote(urlparse(picture_url).path.split('/')[-1])
                                picture_name = re.sub('[<>:\"/|?*]', ' ', picture_name_no_fix)
                                picture_path = desiredpath + picture_name
                                if not os.path.isfile(picture_path):
                                    if 'yande.re' in picture_url:
                                        await self.download(picture_url, picture_path)
                                    else:
                                        tasks.append(asyncio.create_task(self.download(picture_url, picture_path)))
                        await asyncio.gather(*tasks)

    async def download(self, picture_url, picture_path):
        async with self.session.get(picture_url) as r:
            if r.status == 200:
                with open(picture_path, 'wb') as f:
                    print(f'Downloading {picture_url}')
                    f.write(await r.read())
            else:
                print(f'Error {r.status} while getting request for {picture_url}')


def main():
    urliput = input('Paste the url you wish to download images from: ')
    page_number = int(input('Number of pages you wish to download: '))
    x = time.time()
    DanbooruAPI(urliput, page_number)
    print('Time to complete script: ', time.time() - x)
    input('Press Enter to continue . . . ')


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
