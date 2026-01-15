import asyncio
import aiofiles
from urllib.parse import urlparse, urljoin
from aiohttp import ClientSession
from bs4 import BeautifulSoup


class AsyncCrawler:
    def __init__(self, start_url, max_tasks=20, timeout=5):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc

        self.visited = set()
        self.visited_lock = asyncio.Lock()

        self.queue = asyncio.Queue()
        self.queue.put_nowait(start_url)

        self.max_tasks = max_tasks
        self.timeout = timeout

        self.results = {}

    async def fetch(self, session: ClientSession, url: str):
        try:
            async with session.get(url, timeout=self.timeout, allow_redirects=False) as resp:
                status = resp.status
                self.results[url] = status

                content_type = resp.headers.get("Content-Type", "")
                if status == 200 and "html" in content_type:
                    return await resp.text()
                return None
        except:
            self.results[url] = -1
            return None

    async def worker(self, session: ClientSession):
        while True:
            url = await self.queue.get()

            async with self.visited_lock:
                if url in self.visited:
                    self.queue.task_done()
                    continue
                self.visited.add(url)

            html = await self.fetch(session, url)

            if html:
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    full_url = urljoin(url, href)
                    parsed = urlparse(full_url)

                    if parsed.netloc == self.domain:
                        clean = full_url.split("#")[0]
                        async with self.visited_lock:
                            if clean not in self.visited:
                                await self.queue.put(clean)

            self.queue.task_done()

    async def run(self):
        async with ClientSession() as session:
            tasks = [asyncio.create_task(self.worker(session)) for _ in range(self.max_tasks)]
            await self.queue.join()

            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

        # теперь вместо файла — возвращаем grouped
        grouped = {}
        for url, code in self.results.items():
            grouped.setdefault(code, []).append(url)
        
        return grouped