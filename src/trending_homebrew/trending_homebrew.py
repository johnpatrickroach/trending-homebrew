"""Trending homebrew.

better-dotfiles/lib/trending-homebrew.sh
Requests current analytics data from Homebrew and calculates trends.
https://github.com/better-wealth/better-dotfiles
MIT License
2022 (C) John Patrick Roach
"""

import asyncio
from typing import AsyncGenerator, Generator
import aiohttp
from aiomultiprocess import Pool
import numpy as np

DATA_DAY_RANGES: "list[str]" = ["30", "90", "365"]

CATEGORIES: "list[dict[str, str]]" = [
    {
        "name": "install",
        "category_data_url": (
            "https://formulae.brew.sh/api/analytics/install/{days}d.json"
        ),
    },
    {
        "name": "install_on_request",
        "category_data_url": (
            "https://formulae.brew.sh/api/analytics/install-on-request/"
            "{days}d.json"
        ),
    },
    {
        "name": "cask_install",
        "category_data_url": (
            "https://formulae.brew.sh/api/analytics/cask-install/{days}d.json"
        ),
    },
    {
        "name": "BuildError",
        "category_data_url": (
            "https://formulae.brew.sh/api/analytics/build-error/{days}d.json"
        ),
    },
]

HEADERS: "dict[str, str]" = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) "
        "Gecko/20100101 Firefox/108.0"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://brew.sh/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-User": "?1",
    "If-Modified-Since": "Sat, 31 Dec 2022 00:00:00 GMT",
    "If-None-Match": 'W/"63b09975-27bc"',
}


class Category:
    """Category class."""

    data_day_ranges: "list[str]" = DATA_DAY_RANGES

    def __init__(self, name: str, category_data_url: str, k: int = 10) -> None:
        """Construct the instance."""
        self.name: str = name
        self.data_coverage: int = 0
        self.category_data_url: str = category_data_url
        self.k: int = k
        self.data: dict = {}
        self.total_counts: dict = {}
        self.items: dict = {}

    async def request_category_data(self) -> AsyncGenerator:
        """Request data for a category and date range from Homebrew."""
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            for data_day_range in self.data_day_ranges:
                async with session.get(
                    self.category_data_url.format(days=data_day_range),
                    headers=HEADERS,
                ) as req:
                    json_body: dict = await req.json()
                    yield data_day_range, json_body

    def get_windows(self) -> Generator:
        """Create an async generator for windows."""
        yield from [
            [i, j]
            for i, j in zip(self.data_day_ranges[:-1], self.data_day_ranges[1:])
        ]

    def set_windows(self) -> None:
        """Set the window data."""
        for window in self.get_windows():
            if self.total_counts[window[1]] == 0:
                self.total_counts[window[1]] = self.total_counts[window[0]]
            self.total_counts[f"{window[1]}_to_{window[0]}"] = (
                self.total_counts[window[1]] - self.total_counts[window[0]]
            )

    async def set_category_data(self) -> None:
        """Set the category data."""
        async for data_day_range, json_body in self.request_category_data():
            self.data[data_day_range] = json_body

    def get_total_counts(self) -> Generator:
        """Create an async generator for total counts."""
        for data_day_range in self.data_day_ranges:
            yield data_day_range, self.data[data_day_range]["total_count"]

    async def set_total_counts(self) -> None:
        """Set the total counts."""
        await self.set_category_data()
        for data_day_range, total in self.get_total_counts():
            self.total_counts[data_day_range] = total
            self.data_coverage += 1
            if self.data_coverage == len(self.data_day_ranges):
                self.set_windows()

    def get_data_by_date_range(self) -> Generator:
        """Create an async generator for items by date range."""
        for data_day_range in self.data_day_ranges:
            yield data_day_range, self.data[data_day_range]["items"]

    def get_data(self) -> Generator:
        """Create an async generator for items."""
        for data_day_range, items in self.get_data_by_date_range():
            for item in items:
                yield data_day_range, item

    def set_items(self) -> None:
        """Set the item values."""
        for data_day_range, item in self.get_data():
            item_instance = self.items.setdefault(
                item.get("formula", item.get("cask")),
                Item(item.get("formula", item.get("cask"))),
            )
            item_instance.counts[data_day_range] = int(
                item["count"].replace(",", "")
            )

    def get_items(self) -> Generator:
        """Get items."""
        yield from self.items.values()

    def set_item_trends(self) -> None:
        """Set the item windows."""
        for item in self.get_items():
            item.set_windows()
            item.set_percents(
                self.total_counts
            )
            item.set_trend()

    def sort_items(self) -> None:
        """Sort the items."""
        self.items = dict(
            sorted(self.items.items(), reverse=True, key=lambda x: x[1].trend))


class Item:
    """Item class."""

    data_day_ranges: "list[str]" = DATA_DAY_RANGES

    def __init__(self, name: str, trend: int = 0) -> None:
        """Construct the Item instance."""
        self.name: str = name
        self.counts: dict = {
            data_day_range: 0 for data_day_range in self.data_day_ranges
        }
        self.percents: dict = {
            data_day_range: 0 for data_day_range in self.data_day_ranges
        }
        self.trend: float = trend

    def get_windows(self) -> Generator:
        """Create an async generator for windows."""
        yield from [
            [i, j]
            for i, j in zip(self.data_day_ranges[:-1], self.data_day_ranges[1:])
        ]

    def set_windows(self) -> None:
        """Set the window data."""
        for window in self.get_windows():
            if self.counts[window[1]] == 0:
                self.counts[window[1]] = self.counts[window[0]]
            self.counts[f"{window[1]}_to_{window[0]}"] = (
                self.counts[window[1]] - self.counts[window[0]]
            )

    def get_counts(self) -> Generator:
        """Create an async generator for counts."""
        for data_day_range in self.data_day_ranges:
            yield data_day_range, self.counts[data_day_range]

    def set_percents(self, total_counts) -> None:
        """Set items percents of total counts."""
        for data_day_range, count in self.counts.items():
            self.percents[data_day_range] = count / \
                total_counts[data_day_range]

    def set_trend(self) -> None:
        """Set item trend value."""
        percs: list = list(self.percents.values()
                           )[-(len(self.data_day_ranges) - 1):]
        percs.reverse()
        percs.append(self.percents[str(min(int(data_day_range)
                     for data_day_range in self.data_day_ranges))])
        zeros: int = min(next(x[0] for x in enumerate(
            percs) if x[1] > 0), len(percs) - 2)
        percs = percs[zeros:]
        windows: range = range(len(percs))
        self.trend = np.polyfit(windows, percs, 1)[0]


async def get_trending_homebrew(category: dict) -> Category:
    """Get Homebrew trends for a Category."""
    category_instance: Category = Category(
        category["name"], category["category_data_url"]
    )
    await category_instance.set_total_counts()
    category_instance.set_items()
    category_instance.set_item_trends()
    category_instance.sort_items()
    return category_instance


async def main() -> None:
    """Execute the main code."""
    async with Pool() as pool:
        async for category in pool.map(get_trending_homebrew, CATEGORIES):
            print("\n")
            print("==================")
            print(f"{category.name}:")
            print("==================")
            print(f"TOP {str(category.k)} (trend slope):")
            print("==================")
            for top in list(category.items.values())[:category.k - 1]:
                print(f"{top.name} || {str(top.trend)}")
            print("==================")
            print(f"BOTTOM {str(category.k)} (trend slope):")
            print("==================")
            for bottom in list(category.items.values())[-category.k:]:
                print(f"{bottom.name} || {str(bottom.trend)}")
            print("==================")
            print("\n")


if __name__ == "__main__":
    asyncio.run(main())
