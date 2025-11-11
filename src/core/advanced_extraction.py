"""
Advanced Content Extraction - Pro-Level Techniques

Implements 5 expert-level extraction methods:
1. API Reverse Engineering - Find the hidden JSON endpoints
2. Embedded Data Extraction - Extract hydration state from <script> tags
3. LLM-Based Parsing - Use AI to parse without fragile selectors
4. Computer Vision/OCR - Extract text from images
5. DOM Data Attributes - Extract data-* attributes

These methods get you CLEAN, STRUCTURED data instead of messy HTML parsing!
"""
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests

try:
    import pytesseract
    from PIL import Image
    from io import BytesIO
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR not available. Install: pip install pytesseract Pillow")


@dataclass
class ExtractedData:
    """Container for extracted structured data"""
    # API data
    api_endpoints: List[str] = None
    api_data: Dict[str, Any] = None

    # Embedded data (hydration state)
    embedded_json: List[Dict[str, Any]] = None

    # Data attributes
    data_attributes: Dict[str, Any] = None

    # OCR text from images
    image_text: Dict[str, str] = None  # image_url -> extracted_text

    # LLM extracted data
    llm_extracted: Dict[str, Any] = None

    def __post_init__(self):
        if self.api_endpoints is None:
            self.api_endpoints = []
        if self.api_data is None:
            self.api_data = {}
        if self.embedded_json is None:
            self.embedded_json = []
        if self.data_attributes is None:
            self.data_attributes = {}
        if self.image_text is None:
            self.image_text = {}
        if self.llm_extracted is None:
            self.llm_extracted = {}


class APIReverseEngineer:
    """
    TECHNIQUE 1: Reverse-Engineer the API

    Find hidden JSON endpoints that the page uses to load data.
    This is THE GOLDMINE - clean, structured data!
    """

    def __init__(self):
        self.common_api_patterns = [
            r'/api/',
            r'/v\d+/',  # e.g., /v1/, /v2/
            r'\.json',
            r'/graphql',
            r'/rest/',
            r'/data/',
        ]

    def detect_api_endpoints(self, html: str, base_url: str) -> List[str]:
        """
        Detect potential API endpoints from inline JavaScript

        Args:
            html: Raw HTML
            base_url: Base URL of the page

        Returns:
            List of potential API URLs
        """
        endpoints = []
        soup = BeautifulSoup(html, 'html.parser')

        # Find all script tags
        for script in soup.find_all('script'):
            script_content = script.string
            if not script_content:
                continue

            # Look for URL patterns in JavaScript
            # Common patterns: fetch('/api/courses'), axios.get('/v1/data')
            url_patterns = [
                r'fetch\(["\']([^"\']+)["\']',
                r'axios\.get\(["\']([^"\']+)["\']',
                r'axios\.post\(["\']([^"\']+)["\']',
                r'\.ajax\(["\']([^"\']+)["\']',
                r'url:\s*["\']([^"\']+)["\']',
            ]

            for pattern in url_patterns:
                matches = re.findall(pattern, script_content)
                for match in matches:
                    # Check if it looks like an API endpoint
                    if any(api_pattern in match for api_pattern in self.common_api_patterns):
                        # Convert relative to absolute URL
                        if match.startswith('/'):
                            full_url = base_url.rstrip('/') + match
                        elif match.startswith('http'):
                            full_url = match
                        else:
                            continue

                        if full_url not in endpoints:
                            endpoints.append(full_url)

        return endpoints

    def fetch_api_data(self, api_url: str, headers: Dict = None) -> Optional[Dict[str, Any]]:
        """
        Fetch data from discovered API endpoint

        Args:
            api_url: API endpoint URL
            headers: Optional headers to send

        Returns:
            JSON data from API or None
        """
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Failed to fetch API {api_url}: {e}")

        return None


class EmbeddedDataExtractor:
    """
    TECHNIQUE 2: Extract Embedded Data (Hydration State)

    Many modern sites embed JSON data directly in <script> tags.
    This is cleaner than parsing HTML!
    """

    def __init__(self):
        # Common variable names for hydration state
        self.common_patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'window\.__STATE__\s*=\s*({.+?});',
            r'window\.__PRELOADED_STATE__\s*=\s*({.+?});',
            r'window\.APP_STATE\s*=\s*({.+?});',
            r'var\s+data\s*=\s*({.+?});',
            r'const\s+data\s*=\s*({.+?});',
            r'window\.__NEXT_DATA__\s*=\s*({.+?})</script>',  # Next.js
            r'window\.__NUXT__\s*=\s*({.+?});',  # Nuxt.js
        ]

    def extract_embedded_json(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract all JSON objects embedded in <script> tags

        Args:
            html: Raw HTML

        Returns:
            List of JSON objects found
        """
        embedded_data = []
        soup = BeautifulSoup(html, 'html.parser')

        # Method 1: Look for common patterns
        for script in soup.find_all('script'):
            script_content = script.string
            if not script_content:
                continue

            for pattern in self.common_patterns:
                matches = re.findall(pattern, script_content, re.DOTALL)
                for match in matches:
                    try:
                        # Try to parse as JSON
                        data = json.loads(match)
                        embedded_data.append(data)
                    except json.JSONDecodeError:
                        # Sometimes there's trailing code, try to clean
                        try:
                            # Remove trailing semicolons and code
                            cleaned = match.split(';')[0]
                            data = json.loads(cleaned)
                            embedded_data.append(data)
                        except:
                            continue

        # Method 2: Look for JSON-LD (Schema.org structured data)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                embedded_data.append(data)
            except:
                continue

        return embedded_data


class DataAttributeExtractor:
    """
    TECHNIQUE 5: Extract DOM Data Attributes

    Modern HTML uses data-* attributes for machine-readable metadata.
    Much more reliable than parsing text!
    """

    def extract_data_attributes(self, html: str, target_selectors: List[str] = None) -> Dict[str, Any]:
        """
        Extract all data-* attributes from HTML elements

        Args:
            html: Raw HTML
            target_selectors: Optional CSS selectors to target specific elements

        Returns:
            Dictionary of extracted data attributes
        """
        soup = BeautifulSoup(html, 'html.parser')
        extracted = {}

        # Default selectors for common data-rich elements
        if target_selectors is None:
            target_selectors = [
                '[data-product-id]',    # E-commerce
                '[data-course-id]',      # Education
                '[data-price]',          # Pricing
                '[data-author]',         # Content
                '[data-category]',       # Categories
                '[data-sku]',            # Products
                '[class*="product"]',    # Product containers
                '[class*="course"]',     # Course containers
            ]

        for selector in target_selectors:
            elements = soup.select(selector)
            for idx, element in enumerate(elements):
                # Extract all data-* attributes
                data_attrs = {
                    key: value
                    for key, value in element.attrs.items()
                    if key.startswith('data-')
                }

                if data_attrs:
                    # Store with unique key
                    key = f"{selector}_{idx}"
                    extracted[key] = {
                        'selector': selector,
                        'tag': element.name,
                        'text': element.get_text(strip=True)[:100],  # First 100 chars
                        'attributes': data_attrs
                    }

        return extracted


class OCRExtractor:
    """
    TECHNIQUE 4: Computer Vision & OCR

    Extract text from images - the only way to get data that's literally
    part of an image (banners, charts, scanned documents)
    """

    def __init__(self):
        if not OCR_AVAILABLE:
            raise ImportError("OCR requires: pip install pytesseract Pillow")

    def extract_text_from_images(self, html: str, base_url: str, max_images: int = 10) -> Dict[str, str]:
        """
        Extract text from images using OCR

        Args:
            html: Raw HTML
            base_url: Base URL for resolving relative image URLs
            max_images: Maximum number of images to process

        Returns:
            Dictionary mapping image URL -> extracted text
        """
        soup = BeautifulSoup(html, 'html.parser')
        image_texts = {}

        # Find all images
        images = soup.find_all('img', src=True)[:max_images]

        for img in images:
            img_url = img['src']

            # Convert relative to absolute URL
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = base_url.rstrip('/') + img_url
            elif not img_url.startswith('http'):
                continue

            # Skip tiny images (likely icons/tracking pixels)
            width = img.get('width', '0')
            height = img.get('height', '0')
            try:
                if int(width) < 50 or int(height) < 50:
                    continue
            except:
                pass

            # Download and OCR
            try:
                response = requests.get(img_url, timeout=5)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))

                    # Run OCR
                    text = pytesseract.image_to_string(image)

                    if text.strip():
                        image_texts[img_url] = text.strip()

            except Exception as e:
                print(f"OCR failed for {img_url}: {e}")

        return image_texts


class LLMParser:
    """
    TECHNIQUE 3: LLM as "Selector-less" Parser

    Use AI to parse HTML without fragile CSS selectors.
    Incredibly resilient to website changes!
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialize LLM parser

        Args:
            ollama_url: URL of local Ollama server
        """
        self.ollama_url = ollama_url

    def extract_with_llm(self, html_or_text: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Use LLM to extract structured data from HTML

        Args:
            html_or_text: Raw HTML or text content
            schema: Dictionary defining what to extract
                   e.g., {'course_title': 'The course title',
                          'course_code': 'The course code like MUS-101'}

        Returns:
            Extracted data as dictionary
        """
        # Build prompt
        field_descriptions = '\n'.join([
            f"- {key}: {description}"
            for key, description in schema.items()
        ])

        prompt = f"""Extract the following information from this HTML/text and return ONLY valid JSON:

Fields to extract:
{field_descriptions}

Content:
{html_or_text[:5000]}  # Limit to first 5000 chars

Return your answer as a JSON object with these exact keys: {list(schema.keys())}
"""

        try:
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3:8b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')

                # Try to extract JSON from response
                # LLMs sometimes wrap JSON in markdown code blocks
                json_match = re.search(r'\{.+\}', generated_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())

        except Exception as e:
            print(f"LLM extraction failed: {e}")

        return {}


class AdvancedContentExtractor:
    """
    High-level orchestrator for all advanced extraction techniques
    """

    def __init__(self, use_ocr: bool = False, use_llm: bool = False):
        """
        Initialize advanced extractor

        Args:
            use_ocr: Enable OCR extraction (requires pytesseract)
            use_llm: Enable LLM extraction (requires local Ollama)
        """
        self.api_engineer = APIReverseEngineer()
        self.embedded_extractor = EmbeddedDataExtractor()
        self.data_attr_extractor = DataAttributeExtractor()

        self.ocr_extractor = OCRExtractor() if use_ocr and OCR_AVAILABLE else None
        self.llm_parser = LLMParser() if use_llm else None

    def extract_all(self, html: str, url: str) -> ExtractedData:
        """
        Run ALL advanced extraction techniques

        Args:
            html: Raw HTML
            url: Page URL

        Returns:
            ExtractedData with all extracted information
        """
        result = ExtractedData()

        print(f"\n[Advanced Extraction] Processing: {url}")

        # 1. API Reverse Engineering
        print("  [1/5] Detecting API endpoints...")
        result.api_endpoints = self.api_engineer.detect_api_endpoints(html, url)
        if result.api_endpoints:
            print(f"    ✓ Found {len(result.api_endpoints)} API endpoints")
            # Try to fetch first endpoint
            if result.api_endpoints:
                api_data = self.api_engineer.fetch_api_data(result.api_endpoints[0])
                if api_data:
                    result.api_data = api_data
                    print(f"    ✓ Fetched data from API")

        # 2. Embedded Data Extraction
        print("  [2/5] Extracting embedded JSON...")
        result.embedded_json = self.embedded_extractor.extract_embedded_json(html)
        if result.embedded_json:
            print(f"    ✓ Found {len(result.embedded_json)} embedded JSON objects")

        # 3. Data Attributes
        print("  [3/5] Extracting data attributes...")
        result.data_attributes = self.data_attr_extractor.extract_data_attributes(html)
        if result.data_attributes:
            print(f"    ✓ Extracted {len(result.data_attributes)} elements with data attributes")

        # 4. OCR (if enabled)
        if self.ocr_extractor:
            print("  [4/5] Running OCR on images...")
            result.image_text = self.ocr_extractor.extract_text_from_images(html, url)
            if result.image_text:
                print(f"    ✓ Extracted text from {len(result.image_text)} images")
        else:
            print("  [4/5] OCR disabled")

        # 5. LLM Parsing (if enabled)
        if self.llm_parser:
            print("  [5/5] Running LLM extraction...")
            # Define schema based on content type
            schema = {
                'title': 'The main title or heading',
                'category': 'The category or type of content',
                'key_info': 'Any important information like prices, dates, or codes'
            }
            result.llm_extracted = self.llm_parser.extract_with_llm(html, schema)
            if result.llm_extracted:
                print(f"    ✓ LLM extracted {len(result.llm_extracted)} fields")
        else:
            print("  [5/5] LLM parsing disabled")

        print("  ✓ Advanced extraction complete\n")

        return result


def demo():
    """Demonstrate advanced extraction techniques"""
    print("Advanced Content Extraction Demo")

    # Example HTML with various data sources
    example_html = """
    <html>
    <head>
        <script type="application/ld+json">
        {
            "@type": "Course",
            "name": "Introduction to Music Theory",
            "courseCode": "MUS-101"
        }
        </script>
        <script>
            window.__INITIAL_STATE__ = {
                "course": {
                    "id": 12345,
                    "title": "Music Theory 101",
                    "professor": "Dr. Jane Smith",
                    "credits": 3
                }
            };

            fetch('/api/v1/courses/12345').then(r => r.json());
        </script>
    </head>
    <body>
        <div class="course-card" data-course-id="12345" data-price="$599" data-level="beginner">
            <h1>Music Theory Fundamentals</h1>
            <p>Learn the basics of music theory</p>
        </div>
    </body>
    </html>
    """

    # Run extraction
    extractor = AdvancedContentExtractor(use_ocr=False, use_llm=False)
    result = extractor.extract_all(example_html, "https://example.com/courses/12345")

    print("\nExtraction Results")

    print(f"\nAPI Endpoints: {result.api_endpoints}")
    print(f"\nEmbedded JSON: {len(result.embedded_json)} objects found")
    if result.embedded_json:
        print(json.dumps(result.embedded_json[0], indent=2))

    print(f"\nData Attributes: {len(result.data_attributes)} elements found")
    if result.data_attributes:
        for key, value in list(result.data_attributes.items())[:1]:
            print(json.dumps(value, indent=2))


if __name__ == '__main__':
    demo()
