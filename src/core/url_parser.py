"""
URL Parser - Proper URL parsing WITHOUT regex
Uses urllib.parse for robust, standards-compliant URL manipulation

THE GOLDEN RULE: Never use regex to parse URLs!
"""
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, unquote
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import copy


@dataclass
class ParsedURL:
    """
    Structured representation of a URL

    Attributes:
        scheme: Protocol (http, https)
        netloc: Network location (hostname:port)
        hostname: Just the hostname
        port: Port number (or None)
        path: URL path
        params: URL parameters (rarely used)
        query: Query string
        query_dict: Parsed query parameters as dict
        fragment: Fragment identifier (#anchor)
        original: Original URL string
    """
    scheme: str
    netloc: str
    hostname: str
    port: Optional[int]
    path: str
    params: str
    query: str
    query_dict: Dict[str, List[str]]
    fragment: str
    original: str

    def __str__(self) -> str:
        """Reconstruct URL from components"""
        # Rebuild query string from query_dict
        if self.query_dict:
            query = urlencode(self.query_dict, doseq=True)
        else:
            query = self.query

        # Rebuild URL
        return urlunparse((
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            query,
            self.fragment
        ))


class URLParser:
    """
    Robust URL parser and manipulator
    NO REGEX - uses Python's urllib.parse for proper URL handling
    """

    def __init__(self, tracker_params: List[str] = None):
        """
        Initialize URL parser

        Args:
            tracker_params: List of query parameters to consider as tracking garbage
        """
        self.tracker_params = set(tracker_params or [])

    def parse(self, url: str) -> ParsedURL:
        """
        Parse URL into structured components

        Args:
            url: URL string to parse

        Returns:
            ParsedURL object with all components
        """
        # Use urllib.parse - the CORRECT way to parse URLs
        parsed = urlparse(url)

        # Parse query string into dictionary
        query_dict = parse_qs(parsed.query, keep_blank_values=True)

        return ParsedURL(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            hostname=parsed.hostname or '',
            port=parsed.port,
            path=parsed.path,
            params=parsed.params,
            query=parsed.query,
            query_dict=query_dict,
            fragment=parsed.fragment,
            original=url
        )

    def remove_tracker_params(self, parsed_url: ParsedURL) -> ParsedURL:
        """
        Remove tracking parameters from URL

        Args:
            parsed_url: ParsedURL object

        Returns:
            New ParsedURL with tracking params removed
        """
        # Create a copy to avoid mutating original
        new_url = copy.deepcopy(parsed_url)

        # Remove tracker params from query dict
        new_url.query_dict = {
            k: v for k, v in new_url.query_dict.items()
            if k not in self.tracker_params
        }

        return new_url

    def normalize(self, parsed_url: ParsedURL,
                  lowercase_hostname: bool = True,
                  remove_www: bool = True,
                  remove_trailing_slash: bool = True,
                  sort_query_params: bool = True,
                  remove_default_ports: bool = True,
                  remove_fragments: bool = True,
                  decode_percent_encoding: bool = True) -> ParsedURL:
        """
        Normalize URL for consistent comparison and deduplication

        Args:
            parsed_url: ParsedURL to normalize
            lowercase_hostname: Convert hostname to lowercase
            remove_www: Remove 'www.' prefix from hostname
            remove_trailing_slash: Remove trailing slash from path
            sort_query_params: Sort query parameters alphabetically
            remove_default_ports: Remove :80 for HTTP, :443 for HTTPS
            remove_fragments: Remove fragment (#anchor)
            decode_percent_encoding: Decode %20 style encoding

        Returns:
            Normalized ParsedURL
        """
        new_url = copy.deepcopy(parsed_url)

        # Lowercase hostname
        if lowercase_hostname:
            new_url.hostname = new_url.hostname.lower()

        # Remove www prefix
        if remove_www and new_url.hostname.startswith('www.'):
            new_url.hostname = new_url.hostname[4:]

        # Remove default ports
        if remove_default_ports:
            if (new_url.scheme == 'http' and new_url.port == 80) or \
               (new_url.scheme == 'https' and new_url.port == 443):
                new_url.port = None

        # Rebuild netloc with potentially modified hostname/port
        if new_url.port:
            new_url.netloc = f"{new_url.hostname}:{new_url.port}"
        else:
            new_url.netloc = new_url.hostname

        # Remove trailing slash from path (but keep '/' for root)
        if remove_trailing_slash and len(new_url.path) > 1 and new_url.path.endswith('/'):
            new_url.path = new_url.path.rstrip('/')

        # Decode percent encoding
        if decode_percent_encoding:
            new_url.path = unquote(new_url.path)

        # Sort query parameters
        if sort_query_params and new_url.query_dict:
            new_url.query_dict = dict(sorted(new_url.query_dict.items()))

        # Remove fragment
        if remove_fragments:
            new_url.fragment = ''

        return new_url

    def clean(self, url: str, normalize: bool = True, remove_trackers: bool = True) -> str:
        """
        Full cleaning pipeline: parse, remove trackers, normalize

        Args:
            url: URL string to clean
            normalize: Whether to normalize the URL
            remove_trackers: Whether to remove tracking parameters

        Returns:
            Clean URL string
        """
        parsed = self.parse(url)

        if remove_trackers:
            parsed = self.remove_tracker_params(parsed)

        if normalize:
            parsed = self.normalize(parsed)

        return str(parsed)

    def extract_components(self, url: str) -> Dict[str, any]:
        """
        Extract all URL components as a dictionary

        Args:
            url: URL to analyze

        Returns:
            Dictionary with all URL components
        """
        parsed = self.parse(url)

        return {
            'scheme': parsed.scheme,
            'hostname': parsed.hostname,
            'port': parsed.port,
            'path': parsed.path,
            'query_params': parsed.query_dict,
            'fragment': parsed.fragment,
            'full_domain': parsed.netloc,
            'path_segments': [s for s in parsed.path.split('/') if s],
            'path_depth': len([s for s in parsed.path.split('/') if s]),
            'has_query': bool(parsed.query_dict),
            'has_fragment': bool(parsed.fragment),
            'query_param_count': len(parsed.query_dict),
        }

    def get_canonical_url(self, url: str) -> str:
        """
        Get canonical (deduplicated) version of URL
        This is the URL you should use for comparison/storage

        Args:
            url: Original URL

        Returns:
            Canonical URL string
        """
        return self.clean(url, normalize=True, remove_trackers=True)

    def get_domain_parts(self, url: str) -> Tuple[str, str, str]:
        """
        Split domain into subdomain, domain, and TLD

        Args:
            url: URL to analyze

        Returns:
            Tuple of (subdomain, domain, tld)
        """
        parsed = self.parse(url)
        hostname_parts = parsed.hostname.split('.')

        if len(hostname_parts) >= 3:
            # e.g., archives.hartford.edu -> ('archives', 'hartford', 'edu')
            subdomain = '.'.join(hostname_parts[:-2])
            domain = hostname_parts[-2]
            tld = hostname_parts[-1]
        elif len(hostname_parts) == 2:
            # e.g., hartford.edu -> ('', 'hartford', 'edu')
            subdomain = ''
            domain = hostname_parts[0]
            tld = hostname_parts[1]
        else:
            # Single part hostname
            subdomain = ''
            domain = hostname_parts[0] if hostname_parts else ''
            tld = ''

        return subdomain, domain, tld


def demo_url_parsing():
    """Demonstrate proper URL parsing vs regex"""
    print("URL Parsing Demo - No Regex!")

    tracker_params = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'msclkid'
    ]

    parser = URLParser(tracker_params)

    messy_url = "http://catalog.hartford.edu/preview_program.php?catoid=20&poid=4445&utm_source=facebook&fbclid=IwAR123#details"

    print(f"\nOriginal messy URL:\n  {messy_url}\n")

    # Parse it
    parsed = parser.parse(messy_url)
    print(f"Parsed components:")
    print(f"  Scheme: {parsed.scheme}")
    print(f"  Hostname: {parsed.hostname}")
    print(f"  Port: {parsed.port}")
    print(f"  Path: {parsed.path}")
    print(f"  Query params: {parsed.query_dict}")
    print(f"  Fragment: {parsed.fragment}")

    # Remove trackers
    no_trackers = parser.remove_tracker_params(parsed)
    print(f"\nAfter removing trackers:\n  {str(no_trackers)}")

    # Full normalization
    normalized = parser.normalize(no_trackers)
    print(f"\nFully normalized:\n  {str(normalized)}")

    # One-shot clean
    clean_url = parser.clean(messy_url)
    print(f"\nOne-shot clean:\n  {clean_url}")

    # Extract components
    components = parser.extract_components(messy_url)
    print(f"\nExtracted components:")
    for key, value in components.items():
        print(f"  {key}: {value}")

    print("\nNo regex needed - just proper URL parsing.")


if __name__ == '__main__':
    demo_url_parsing()
