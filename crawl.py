from asyncio import gather, sleep
from httpx import AsyncClient, Response
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup

from typing import List


class Crawl:
    __playwright_monostate: Playwright = None
    __browser_monostate: Browser = None
    __context_monostate: BrowserContext = None
    __pages_monostate: List[Page] = []
    __http_client_monostate: AsyncClient = AsyncClient()

    __page: Page = None
    __response: Response = None
    __content: str = None

    status_code: int = None


    @classmethod
    async def start(cls, headless = True):
        if not cls.__playwright_monostate:
            cls.__playwright_monostate = await async_playwright().start()
            cls.__browser_monostate = await cls.__playwright_monostate.chromium.launch(headless = headless)
            cls.__context_monostate = await cls.__browser_monostate.new_context()

            cls.__pages_monostate += await gather(*[cls.__context_monostate.new_page() for _ in range(2)])


    @classmethod
    async def close(cls):
        if cls.__browser_monostate:
            await cls.__browser_monostate.close()
            await cls.__playwright_monostate.stop()
            await cls.__http_client_monostate.aclose()


    def __init__(self):
        if not self.__playwright_monostate: raise Exception('browser not started')


        self.__dict__ = {
            '__playwright_monostate': self.__playwright_monostate,
            '__browser_monostate': self.__browser_monostate,
            '__context_monostate': self.__context_monostate,
            '__pages_monostate': self.__pages_monostate,
            '__http_client_monostate': self.__http_client_monostate
        }


    async def _get_page(self) -> Page:
        while True:
            if self.__pages_monostate:
                page = self.__pages_monostate.pop(0)
                return page
            await sleep(1)


    async def __release_page(self):
        if not self.__page: return

        await self.__page.close()
        self.__page = None

        new_page = await self.__context_monostate.new_page()
        self.__pages_monostate.append(new_page)


    async def get(self, url: str):
        self.__response = await self.__http_client_monostate.get(url)
        self.status_code = self.__response.status_code


    async def goto(self, url: str):
        if not self.__page: self.__page = await self._get_page()
        response = await self.__page.goto(url)
        self.status_code = response.status


    async def content(self):
        if not self.__content:
            self.__content = self.__response.text if self.__response else await self.__page.content()
            if self.__page: await self.__release_page()

        return self.__content


    async def scraper(self) -> BeautifulSoup:
        content = await self.content()
        soup = BeautifulSoup(content, 'html.parser')
        return soup


    async def save_file(self, file_name: str = 'index.html'):
        content = await self.content()

        with open(file_name, 'w+', encoding = 'utf-8') as file:
            file.write(content)
