"""
Web Crawler - Fetch and extract content from URLs

The Big Missing Piece: Content-based data extraction
- HTTP status codes
- Final redirected URLs (true canonical)
- Page titles, meta descriptions, H1 tags
- Full text content
- Structured data (JSON-LD/Schema.org)
- Outbound links
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import time
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

from src.core.url_parser import URLParser


@dataclass
class PageContent:
    """
    Comprehensive page content data
    """
    # Request metadata
    url: str
    final_url: str  # After redirects - TRUE canonical URL
    status_code: int
    response_time_ms: int
    redirect_chain: List[str]

    # Content extraction
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: List[str] = None
    h2_tags: List[str] = None
    text_content: Optional[str] = None
    text_length: int = 0

    # Structured data
    json_ld: List[Dict[str, Any]] = None
    schema_org_types: List[str] = None

    # Links
    outbound_links: List[str] = None
    internal_links: List[str] = None
    external_links: List[str] = None

    # Additional metadata
    content_type: Optional[str] = None
    content_length: int = 0
    language: Optional[str] = None

    def __post_init__(self):
        """Initialize lists if None"""
        if self.h1_tags is None:
            self.h1_tags = []
        if self.h2_tags is None:
            self.h2_tags = []
        if self.json_ld is None:
            self.json_ld = []
        if self.schema_org_types is None:
            self.schema_org_types = []
        if self.outbound_links is None:
            self.outbound_links = []
        if self.internal_links is None:
            self.internal_links = []
        if self.external_links is None:
            self.external_links = []
        if self.redirect_chain is None:
            self.redirect_chain = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class WebCrawler:
    """
    Professional web crawler with content extraction
    """

    def __init__(self,
                 timeout: int = 10,
                 max_retries: int = 3,
                 delay_between_requests: float = 1.0,
                 user_agent: str = None):
        """
        Initialize web crawler

        Args:
            timeout: Request timeout in seconds
            max_retries: Number of retries for failed requests
            delay_between_requests: Delay between requests (be polite!)
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.delay = delay_between_requests
        self.parser = URLParser()

        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set user agent
        if user_agent is None:
            user_agent = "Mozilla/5.0 (compatible; URLOrganizer/1.0; +https://github.com/ideal-url-organizer)"
        self.session.headers.update({'User-Agent': user_agent})

        self.last_request_time = 0

    def fetch(self, url: str) -> Optional[PageContent]:
        """
        Fetch and extract content from URL

        Args:
            url: URL to fetch

        Returns:
            PageContent object or None if failed
        """
        # Rate limiting - be polite!
        self._respect_rate_limit()

        try:
            # Make request
            start_time = time.time()
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            response_time_ms = int((time.time() - start_time) * 1000)

            # Get redirect chain
            redirect_chain = []
            if response.history:
                redirect_chain = [r.url for r in response.history]

            # Extract content
            content = PageContent(
                url=url,
                final_url=response.url,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                redirect_chain=redirect_chain,
                content_type=response.headers.get('Content-Type', ''),
                content_length=int(response.headers.get('Content-Length', 0))
            )

            # Only parse HTML content
            if 'text/html' in content.content_type:
                self._extract_html_content(response.text, content)

            return content

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _respect_rate_limit(self):
        """Implement polite crawling with rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def _extract_html_content(self, html: str, content: PageContent):
        """
        Extract all content from HTML

        Args:
            html: Raw HTML
            content: PageContent object to populate
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style tags
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content.title = title_tag.get_text().strip()

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content.meta_description = meta_desc.get('content', '').strip()

        # Extract language
        html_tag = soup.find('html')
        if html_tag:
            content.language = html_tag.get('lang', '')

        # Extract H1 tags
        content.h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]

        # Extract H2 tags
        content.h2_tags = [h2.get_text().strip() for h2 in soup.find_all('h2')][:10]  # Limit to first 10

        # Extract full text content
        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content.text_content = ' '.join(chunk for chunk in chunks if chunk)
        content.text_length = len(content.text_content)

        # Extract JSON-LD structured data (Schema.org)
        self._extract_structured_data(soup, content)

        # Extract links
        self._extract_links(soup, content)

    def _extract_structured_data(self, soup: BeautifulSoup, content: PageContent):
        """
        Extract JSON-LD and Schema.org structured data
        This is the GOLDMINE for semantic understanding!
        """
        # Find all JSON-LD scripts
        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                content.json_ld.append(data)

                # Extract @type for quick categorization
                if isinstance(data, dict):
                    schema_type = data.get('@type', '')
                    if schema_type:
                        content.schema_org_types.append(schema_type)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            schema_type = item.get('@type', '')
                            if schema_type:
                                content.schema_org_types.append(schema_type)
            except json.JSONDecodeError:
                pass

    def _extract_links(self, soup: BeautifulSoup, content: PageContent):
        """
        Extract all outbound links and categorize them
        """
        base_domain = urlparse(content.final_url).netloc

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert relative URLs to absolute
            absolute_url = urljoin(content.final_url, href)

            # Skip anchors, javascript, etc.
            if absolute_url.startswith(('http://', 'https://')):
                content.outbound_links.append(absolute_url)

                # Categorize as internal or external
                link_domain = urlparse(absolute_url).netloc
                if link_domain == base_domain:
                    content.internal_links.append(absolute_url)
                else:
                    content.external_links.append(absolute_url)


class ContentExtractor:
    """
    High-level content extraction API
    """

    def __init__(self, crawler: WebCrawler = None):
        """Initialize content extractor"""
        self.crawler = crawler if crawler else WebCrawler()

    def extract_from_url(self, url: str) -> Optional[PageContent]:
        """
        Extract content from a single URL

        Args:
            url: URL to extract from

        Returns:
            PageContent or None
        """
        return self.crawler.fetch(url)

    def extract_from_urls(self, urls: List[str],
                         max_pages: int = None,
                         verbose: bool = True) -> Dict[str, PageContent]:
        """
        Extract content from multiple URLs

        Args:
            urls: List of URLs to extract from
            max_pages: Maximum number of pages to fetch
            verbose: Print progress

        Returns:
            Dictionary mapping URL -> PageContent
        """
        results = {}

        urls_to_fetch = urls[:max_pages] if max_pages else urls
        total = len(urls_to_fetch)

        for idx, url in enumerate(urls_to_fetch, 1):
            if verbose:
                print(f"Fetching {idx}/{total}: {url}")

            content = self.extract_from_url(url)
            if content:
                results[url] = content

        if verbose:
            print(f"\n✓ Successfully fetched {len(results)}/{total} pages")

        return results


def demo_content_extraction():
    """Demonstrate content extraction"""
    print("Content Extraction Demo")

    # Example URL
    test_url = "http://catalog.hartford.edu/"

    crawler = WebCrawler()
    content = crawler.fetch(test_url)

    if content:
        print(f"\n✓ Successfully fetched: {test_url}")
        print(f"\nStatus Code: {content.status_code}")
        print(f"Final URL: {content.final_url}")
        print(f"Response Time: {content.response_time_ms}ms")

        if content.redirect_chain:
            print(f"\nRedirect Chain:")
            for redirect in content.redirect_chain:
                print(f"  → {redirect}")

        print(f"\nTitle: {content.title}")
        print(f"Meta Description: {content.meta_description}")

        if content.h1_tags:
            print(f"\nH1 Tags ({len(content.h1_tags)}):")
            for h1 in content.h1_tags[:3]:
                print(f"  • {h1}")

        print(f"\nText Length: {content.text_length} characters")
        print(f"Internal Links: {len(content.internal_links)}")
        print(f"External Links: {len(content.external_links)}")

        if content.schema_org_types:
            print(f"\nSchema.org Types Found:")
            for schema_type in content.schema_org_types:
                print(f"  • {schema_type}")
    else:
        print(f"\n✗ Failed to fetch: {test_url}")


if __name__ == '__main__':
    demo_content_extraction()
