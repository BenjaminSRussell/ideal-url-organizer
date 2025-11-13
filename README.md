# URL Organizer - Production Web Content Intelligence Platform

A production-ready, expert-level system for comprehensive URL and web content analysis. Goes beyond URL structure to analyze actual page content using modern techniques including web crawling, semantic analysis, machine learning, and advanced data extraction.

## Features

### **NO REGEX for URL Parsing** - The Golden Rule
- Uses proper URL parsing libraries (`urllib.parse` in Python, native `URL` class in Node.js)
- Handles all edge cases correctly
- Robust and standards-compliant

### **25+ Organization Methods**

#### Structure-Based Analysis (Methods 1-21)

1. **By Domain** - Group URLs by hostname
2. **By Crawl Depth** - Organize by crawl depth levels
3. **By Subdomain** - Separate by subdomain (archives, catalog, etc.)
4. **By Path Structure** - Group by first path segment
5. **By Query Parameters** - Organize by query parameter signatures
6. **By Parent Domain** - Group by parent URL domain
7. **By TLD** - Organize by top-level domain (.edu, .com, etc.)
8. **By Protocol** - Separate HTTP vs HTTPS
9. **By Port** - Group by port number
10. **By Path Depth** - Organize by number of path segments
11. **By File Extension** - Group by file type (.php, .html, etc.)
12. **By Content Type** - Organize by MIME type
13. **Hierarchical Tree** - Build parent-child tree structure
14. **By Discovery Time** - Group by when URLs were discovered
15. **By Crawl Status** - Separate crawled vs not crawled
16. **Canonical Deduplication** - Find duplicate URLs
17. **By Resource Type** - Categorize by resource (courses, programs, etc.)
18. **By URL Length** - Group by URL length categories
19. **Network Graph** - Create relationship graph
20. **By Parameter Patterns** - Analyze specific parameters (catoid, poid, etc.)
21. **Domain-Depth Matrix** - 2D analysis of domains × depths

#### Content-Based Analysis (Methods 22-25)

22. **By HTTP Status** - Group by status codes (200, 301, 404, 500) for link rot detection
23. **By Schema.org Type** - Organize by structured data types (Course, Person, Event, Organization)
24. **By Page Authority** - Rank by PageRank importance (cornerstone, hub, authority, leaf pages)
25. **By Semantic Similarity** - Cluster by meaning using text embeddings (machine learning)

### **Web Crawling & Content Extraction**
- HTTP status codes and redirect tracking
- Page titles, meta descriptions, headings
- Full text content extraction
- Schema.org/JSON-LD structured data (THE GOLDMINE!)
- Outbound link analysis (internal vs external)
- Response time tracking

### **Advanced Extraction Techniques**
1. **API Reverse Engineering** - Detect hidden JSON endpoints
2. **Embedded Data Extraction** - Extract hydration state from JavaScript
3. **Data Attribute Extraction** - Get machine-readable data-* attributes
4. **OCR** - Extract text from images using Tesseract
5. **LLM Parsing** - Resilient AI-based extraction with Ollama

### **Semantic Analysis (Machine Learning)**
- **Text Embeddings** - 384-dimensional vectors for semantic similarity
- **Named Entity Recognition** - Extract people, organizations, locations
- **Topic Modeling** - Auto-discover content themes with LDA
- **Similarity Clustering** - Group content by meaning, not keywords

### **Link Graph Analysis**
- **PageRank** - Identify most important pages (what Google uses)
- **HITS Algorithm** - Find hubs and authorities
- **Centrality Metrics** - In-degree, out-degree, betweenness
- **Page Type Classification** - Cornerstone, hub, authority, leaf, orphan

### **Production Features**
- Date-based logging system (logs/YYYY-MM-DD/)
- Component-specific logs (crawler, parser, organizer, analyzer)
- Failure tracking and analysis
- Comprehensive production test suite
- Error handling with minimal CLI interference

### **Data Quality Analysis**
- Comprehensive data quality reports
- Identifies strengths and weaknesses
- Provides actionable recommendations
- Analyzes completeness, relationships, temporal patterns

### **Visualizations**
- Depth distribution charts
- Domain distribution charts
- Protocol usage pie charts
- URL length histograms
- Crawl status visualization
- Network graphs
- Keyword similarity heatmaps (filter the dataset by keyword such as “heat” and show pairwise TF-IDF similarity)

### **Multi-Language Support**
- **Python** - Main implementation
- **Node.js** - URL cleaning and parsing example
- **Go** - Ready for URL parsing extensions

## Quick Start

### Installation

```bash
# Clone the repository
cd ideal-url-organizer

# Basic installation (URL analysis only)
pip install pyyaml requests beautifulsoup4 lxml networkx

# Full installation with expert features (recommended)
pip install -r requirements.txt

# Download NER model for semantic analysis
python -m spacy download en_core_web_sm

# Optional: Install Tesseract for OCR
# macOS: brew install tesseract
# Linux: sudo apt install tesseract-ocr

# Optional: Install Ollama for LLM-based parsing
# Download from ollama.ai, then: ollama pull llama3:8b
```

### Run All Methods

```bash
# Run complete analysis pipeline
python src/main.py --full

# Run all organization methods
python src/main.py --all

# Run specific method
python src/main.py --method method_01_by_domain

# Run data quality analysis
python src/main.py --analyze

# Generate visualizations
python src/main.py --visualize

# List all available methods
python src/main.py --list
```

### Run Tests

```bash
# Run test suite with sample data
python tests/test_all_methods.py

# Run production stress tests (find limits and weaknesses)
python tests/test_production.py
```

### Run Expert Features Demo

```bash
# Demonstrate all expert features
python demo_expert_features.py
```

### Node.js URL Cleaning

```bash
# Demo URL cleaning
node src/utils/url_cleaner.js demo

# Process JSONL file
node src/utils/url_cleaner.js process data/raw/urls.jsonl data/processed/cleaned.jsonl
```

## Project Structure

```
ideal-url-organizer/
config/
  global.yaml                      # Central configuration

data/
  raw/
    urls.jsonl                     # Input URL data
  processed/
    method_01_by_domain/           # 25+ organization methods
    method_02_by_depth/
    ...
    method_25_by_semantic_similarity/
  analysis/
    data_quality_report.json
    data_quality_report.md
  visualizations/
    charts/

logs/
  YYYY-MM-DD/                      # Date-based logs
    crawler.log
    parser.log
    organizer.log
    analyzer.log
    failures.log

src/
  core/
    config.py                      # Configuration loader
    url_parser.py                  # URL parser (NO REGEX!)
    data_loader.py                 # JSONL data loader
    web_crawler.py                 # HTTP crawler & content extraction
    advanced_extraction.py         # 5 advanced extraction techniques
    logger.py                      # Production logging system

  organizers/
    method_01_by_domain.py
    ...
    method_25_by_semantic_similarity.py  # 25 total methods

  analyzers/
    data_quality_analyzer.py       # Data quality analysis
    semantic_analyzer.py           # Text embeddings, NER, topic modeling
    link_graph_analyzer.py         # PageRank, HITS

  visualizers/
    chart_generator.py             # Charts and graphs

  utils/
    url_cleaner.js                 # Node.js URL cleaning

  main.py                          # Main orchestrator

tests/
  test_all_methods.py              # Comprehensive test suite
  test_production.py               # Production stress tests

scripts/
  remove_emojis.py                 # Utility scripts

demo_expert_features.py            # Expert features demo
requirements.txt                   # Python dependencies
README.md                          # This file
EXPERT_FEATURES.md                 # Detailed expert features guide
ADVANCED_EXTRACTION.md             # Advanced extraction techniques guide
```

## Expert Features Usage

### Web Crawling

```python
from src.core.web_crawler import WebCrawler

crawler = WebCrawler()
content = crawler.fetch("http://example.com")

print(f"Status: {content.status_code}")
print(f"Title: {content.title}")
print(f"Schema.org types: {content.schema_org_types}")
print(f"Text length: {content.text_length}")
```

### Advanced Extraction

```python
from src.core.advanced_extraction import AdvancedContentExtractor

extractor = AdvancedContentExtractor(use_ocr=True, use_llm=True)
result = extractor.extract_all(html, url)

# Check all 5 extraction methods
if result.api_endpoints:
    print(f"Found {len(result.api_endpoints)} API endpoints")
if result.embedded_json:
    print(f"Found {len(result.embedded_json)} embedded JSON objects")
if result.data_attributes:
    print(f"Found data attributes in {len(result.data_attributes)} elements")
```

### Semantic Analysis

```python
from src.analyzers.semantic_analyzer import SemanticAnalyzer

analyzer = SemanticAnalyzer()
analysis = analyzer.analyze(pages)

# Find similar pages
similar = analysis['similar_pages']['http://example.com/page1']

# Get named entities
entities = analysis['entities']
print(f"Found {len(entities['PERSON'])} people")
print(f"Found {len(entities['ORG'])} organizations")

# Get discovered topics
topics = analysis['topics']
```

### Link Graph Analysis

```python
from src.analyzers.link_graph_analyzer import LinkGraphAnalyzer

analyzer = LinkGraphAnalyzer()
analysis = analyzer.analyze(pages)

# Get most important pages
top_pages = analysis['pagerank']['top_10']

# Get hubs and authorities
hubs = analysis['hits']['top_hubs']
authorities = analysis['hits']['top_authorities']

# Identify page types
page_types = analysis['page_types']
cornerstone = page_types['cornerstone']
```

### Production Logging

```python
from src.core.logger import get_logger, safe_execute, log_errors

# Get logger instance
logger = get_logger(verbose=True)

# Use decorator for automatic error logging
@log_errors('crawler', 'fetch_page')
def fetch_page(url):
    response = requests.get(url)
    return response.text

# Use safe_execute for graceful error handling
result = safe_execute(
    risky_function,
    arg1, arg2,
    component='parser',
    operation='parse_url',
    default=None
)
```

## Configuration

All settings are in `config/global.yaml`:

- **Tracker parameters** to remove (utm_*, fbclid, etc.)
- **Normalization rules** (lowercase, remove www, etc.)
- **Organization methods** to enable/disable
- **Visualization settings**
- **Output formats**

## Data Format

Input data in JSONL format:

```json
{
 "schema_version": 1,
 "url": "http://catalog.hartford.edu/preview_program.php?catoid=20&poid=4445",
 "url_normalized": "http://catalog.hartford.edu/preview_program.php?catoid=20&poid=4445",
 "depth": 2,
 "parent_url": "https://hartford.edu/academics/",
 "fragments": [],
 "discovered_at": 1762713013,
 "queued_at": 1762713013,
 "crawled_at": null,
 "response_time_ms": null,
 "status_code": null,
 "content_type": null,
 "content_length": null,
 "title": null,
 "link_count": null
}
```

## How URL Parsing Works (The Right Way!)

### **DON'T** use regex:
```python
# WRONG - Brittle and fails on edge cases
import re
match = re.search(r'https?://([^/]+)', url)
```

### **DO** use proper URL parsing:
```python
# RIGHT - Robust and standards-compliant
from urllib.parse import urlparse
parsed = urlparse(url)
hostname = parsed.hostname
```

### Node.js Example:
```javascript
// The RIGHT way in Node.js
const url = new URL(messyURL);
url.searchParams.delete('utm_source');
const cleanURL = url.href;
```

## Sample Analysis Output

```
DATA QUALITY ANALYSIS
================================================================================

[Overview]
 Total records: 9
 Unique URLs: 9
 Unique domains: 3
 Depth range: 2-6

 STRENGTHS:
 • All URLs have discovery timestamps
 • All URLs have queue timestamps
 • No duplicate URLs in dataset

 WEAKNESSES:
 • No URLs have been crawled yet (all crawled_at timestamps are null)
 • Content-type data is 0.0% complete
 • Title data is 0.0% complete

→ RECOMMENDATIONS:
 • Begin crawling queued URLs to populate response data
 • Extract page titles during crawling for better content analysis
```

## Testing

The test suite validates:
- Data loading from sample data
- URL parsing without regex
- URL cleaning and normalization
- All organization methods
- Data quality analysis

```bash
python tests/test_all_methods.py
```

## Visualizations

Generated charts include:
- Depth distribution bar chart
- Domain distribution horizontal bar chart
- Protocol distribution pie chart (HTTP vs HTTPS)
- URL length histogram
- Crawl status pie chart
- Keyword similarity heatmap filtered by keyword

### Keyword Similarity Heatmaps
Targeted keyword similarity heatmaps are generated by `src/visualizers/keyword_similarity_heatmap.py`. The script filters the loaded URLs for the provided keyword, vectorizes the matching text, and saves a TF-IDF cosine-similarity heatmap under `data/visualizations/charts/keyword_similarity_heatmap_{keyword}.png`.

```bash
python src/visualizers/keyword_similarity_heatmap.py --keyword heat
```

## License

MIT License - Feel free to use and modify!

## Acknowledgments

Built with best practices:
- **NO REGEX for URL parsing** - Uses proper URL parsing libraries
- **Multi-language support** - Python, Node.js, Go
- **Comprehensive testing** - Validated with real data
- **Production-ready** - Clean code, proper error handling

## Real-World Use Cases

### University Website Analysis
- Find all courses by Schema.org type
- Extract faculty names using NER
- Group content by department using topic modeling
- Identify main department pages with PageRank
- Detect broken links with HTTP status tracking

### E-commerce Site Audit
- Group similar products using semantic similarity
- Find orphan products with low PageRank
- Detect redirect chains with HTTP tracking
- Auto-categorize products with topic modeling
- Extract product data from APIs and data attributes

### Content Management
- Find duplicate content with semantic similarity > 0.95
- Discover content themes with topic modeling
- Identify cornerstone content with high PageRank
- Find content gaps in semantic clusters
- Track content quality with status codes and text metrics

## Detailed Guides

For in-depth documentation, see:

- **EXPERT_FEATURES.md** - Complete guide to web crawling, semantic analysis, and link graph analysis
- **ADVANCED_EXTRACTION.md** - The 5 advanced extraction techniques explained in detail

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Download NER model: `python -m spacy download en_core_web_sm`
3. Run test suite: `python tests/test_all_methods.py`
4. Run production tests: `python tests/test_production.py`
5. Try expert features: `python demo_expert_features.py`
6. Run full analysis: `python src/main.py --full`
7. Explore results in `data/` and `logs/` directories
8. Customize `config/global.yaml` for your needs
9. Add custom organization methods in `src/organizers/`

## Key Principles

1. **Never use regex for URL parsing** - Always use proper libraries
2. **Extract APIs, don't parse HTML** - Get clean structured data
3. **Use Schema.org when available** - Websites tell you what they are
4. **Use AI for resilient parsing** - Works regardless of HTML structure
5. **Use ML for semantic understanding** - Find similarity by meaning
6. **Production-ready logging** - Track errors without CLI noise
7. **Comprehensive testing** - Find limits and weaknesses before production

---

**Built for production with modern web intelligence techniques - 2025** 
