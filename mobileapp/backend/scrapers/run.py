import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrapy.crawler import CrawlerProcess  # noqa: E402

from scrapers import settings  # noqa: E402
from scrapers.gem_spider import GemSpider  # noqa: E402
from scrapers.snapdeal_scraper import SnapdealScraper  # noqa: E402
from scrapers.vijaysales_scraper import VijaySalesScraper  # noqa: E402


def run() -> None:
    process = CrawlerProcess(settings.__dict__)
    process.crawl(GemSpider)
    process.start()

    # Scrapy/Twisted swaps the Windows asyncio policy to SelectorEventLoop,
    # which cannot launch subprocesses; Playwright needs ProactorEventLoop.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    print("Running Vijay Sales scraper...")
    vs_saved = VijaySalesScraper().run()
    print(f"Vijay Sales saved {vs_saved} listings")

    print("Running Snapdeal scraper...")
    sd_saved = SnapdealScraper().run()
    print(f"Snapdeal saved {sd_saved} listings")


if __name__ == "__main__":
    run()
