from crawl import Crawl

from asyncio import run, gather


async def goto(url: str):
    crawl = Crawl()
    await crawl.goto(url)

    soup = await crawl.scraper()
    title = soup.find('title')

    if crawl.status_code == 200: print(f'with goto: {title.text}')
    else: await crawl.save_file(f'{title.text}.html')


async def get(url: str):
    crawl = Crawl()
    await crawl.get(url)

    soup = await crawl.scraper()
    title = soup.find('title')

    if crawl.status_code == 200: print(f'with get: {title.text}')
    else: await crawl.save_file(f'{title.text}.html')



async def main():
    await Crawl.start(False)

    await gather(
        get('https://example.com'),
        goto('https://python.org'),
        goto('https://youtube.com'),
        goto('https://google.com'),
    )

    await Crawl.close()


run(main())
