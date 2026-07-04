import time
from urllib.parse import urljoin, urldefrag, urlparse, quote

from bs4 import BeautifulSoup
import requests

from . import config_crawler
from amon_hen.common.http import http_get


class Crawler:
    """
    Base class for implementing a crawler that traverse and process data sources.
    """

    def __init__(self):
        """
        Initialize a Crawler with the specified search behavior and target URL.
        """
        self.base_url = ""
        self.base_url_hostname = ""
        self.share_host = False
        self.max_depth = 0
        self.visited = set()

    def _crawl(self, url, depth=0):
        """
        Recursively traverse links in the website.
        """
        # Base case - URL is already visited
        if url in self.visited:
            return

        # Base case - depth exceeds maximum depth threshold
        if depth > self.max_depth:
            return

        self.visited.add(url)
        response = http_get(url)

        # Processing function
        self._process_response(response)

        # Only extract links if HTML
        if self._is_html(response):
            links = self._extract_links(response)
            links = self._filter_links(links)

            for link in links:
                self._crawl(link, depth + 1)

    def _is_html(self, response):
        """
        Identify whether or not a downloaded response is of type HTML.
        """
        content_type = response.headers.get("Content-Type").lower()

        if config_crawler.EXTENSION_INFO[".html"]["mime"] in content_type:
            return True

        return False

    def _filter_links(self, links):
        """
        Remove links that do not meet criteria from list of candidate links.
        """
        filtered_links = []

        for link in links:
            # Convert relative link to absolute link
            absolute_link = urljoin(self.base_url, link)

            # Remove fragments
            absolute_link, _ = urldefrag(absolute_link)

            # Break link into individual components
            parsed_link = urlparse(absolute_link)

            # Must be HTTP or HTTPS
            if parsed_link.scheme not in ("http", "https"):
                continue

            # Must share the same host name as base URL, if enabled
            if self.share_host:
                if not (
                    parsed_link.hostname == self.base_url_hostname
                    or parsed_link.hostname.endswith("." + self.base_url_hostname)
                ):

                    continue

            # Specific application filtering
            if self._non_exhaustive_discard(parsed_link):
                continue

            filtered_links.append(absolute_link)

        # Remove duplicates
        filtered_links = list(set(filtered_links))

        return filtered_links

    def _extract_links(self, response):
        """
        Retrieve all href and src links from web page.
        """
        soup = BeautifulSoup(response.text, "html.parser")

        links = []

        links.extend(
            quote(tag["href"].replace("\\", "/"), safe=":/?=&")
            for tag in soup.find_all(href=True)
        )
        links.extend(
            quote(tag["src"].replace("\\", "/"), safe=":/?=&")
            for tag in soup.find_all(src=True)
        )

        return links

    def _process_response(self, response):
        """
        Process a crawl response.
        """
        pass

    def _non_exhaustive_discard(self, link):
        """
        Determine whether or not a link should be discarded in a non-exhaustive search.
        """
        return False

    def crawl(self, base_url, max_depth=0, share_host=False):
        """
        Initiate the crawling process.
        """
        self.base_url = base_url
        self.base_url_hostname = urlparse(base_url).hostname
        self.max_depth = max_depth
        self.share_host = share_host
        self.visited = set()

        self._crawl(base_url, depth=0)

        return self.visited
