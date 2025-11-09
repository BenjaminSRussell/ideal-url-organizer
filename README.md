# URL Organizer - Comprehensive URL Data Analysis System

An incredibly organized, production-ready system for deep URL data analysis with 20+ organization methods, data quality analysis, and beautiful visualizations.

## 🌟 Features

### ✅ **NO REGEX for URL Parsing** - The Golden Rule
- Uses proper URL parsing libraries (`urllib.parse` in Python, native `URL` class in Node.js)
- Handles all edge cases correctly
- Robust and standards-compliant

### 📊 **21+ Organization Methods**

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

### 🔍 **Data Quality Analysis**
- Comprehensive data quality reports
- Identifies strengths and weaknesses
- Provides actionable recommendations
- Analyzes completeness, relationships, temporal patterns

### 📈 **Visualizations**
- Depth distribution charts
- Domain distribution charts
- Protocol usage pie charts
- URL length histograms
- Crawl status visualization
- Network graphs

### 🌐 **Multi-Language Support**
- **Python** - Main implementation
- **Node.js** - URL cleaning and parsing example
- **Go** - Ready for URL parsing extensions

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd ideal-url-organizer

# Install dependencies
pip install -r requirements.txt
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
```

### Node.js URL Cleaning

```bash
# Demo URL cleaning
node src/utils/url_cleaner.js demo

# Process JSONL file
node src/utils/url_cleaner.js process data/raw/urls.jsonl data/processed/cleaned.jsonl
```

## 📁 Project Structure

```
ideal-url-organizer/
├── config/
│   └── global.yaml                # Configuration file
├── data/
│   ├── raw/
│   │   └── urls.jsonl             # Input data
│   ├── processed/
│   │   ├── method_01_by_domain/   # Output from each method
│   │   ├── method_02_by_depth/
│   │   └── ...
│   ├── analysis/
│   │   ├── data_quality_report.json
│   │   └── data_quality_report.md
│   └── visualizations/
│       └── charts/
├── src/
│   ├── core/
│   │   ├── config.py              # Config loader
│   │   ├── url_parser.py          # URL parser (NO REGEX!)
│   │   └── data_loader.py         # Data loading
│   ├── organizers/
│   │   ├── method_01_by_domain.py
│   │   ├── method_02_by_depth.py
│   │   └── ... (21+ methods)
│   ├── analyzers/
│   │   └── data_quality_analyzer.py
│   ├── visualizers/
│   │   └── chart_generator.py
│   ├── utils/
│   │   └── url_cleaner.js         # Node.js implementation
│   └── main.py                     # Main orchestrator
├── tests/
│   └── test_all_methods.py        # Test suite
├── requirements.txt
└── README.md
```

## 🎯 Configuration

All settings are in `config/global.yaml`:

- **Tracker parameters** to remove (utm_*, fbclid, etc.)
- **Normalization rules** (lowercase, remove www, etc.)
- **Organization methods** to enable/disable
- **Visualization settings**
- **Output formats**

## 📊 Data Format

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

## 🔧 How URL Parsing Works (The Right Way!)

### ❌ **DON'T** use regex:
```python
# WRONG - Brittle and fails on edge cases
import re
match = re.search(r'https?://([^/]+)', url)
```

### ✅ **DO** use proper URL parsing:
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

## 📈 Sample Analysis Output

```
DATA QUALITY ANALYSIS
================================================================================

[Overview]
  Total records: 9
  Unique URLs: 9
  Unique domains: 3
  Depth range: 2-6

✓ STRENGTHS:
  • All URLs have discovery timestamps
  • All URLs have queue timestamps
  • No duplicate URLs in dataset

✗ WEAKNESSES:
  • No URLs have been crawled yet (all crawled_at timestamps are null)
  • Content-type data is 0.0% complete
  • Title data is 0.0% complete

→ RECOMMENDATIONS:
  • Begin crawling queued URLs to populate response data
  • Extract page titles during crawling for better content analysis
```

## 🧪 Testing

The test suite validates:
- Data loading from sample data
- URL parsing without regex
- URL cleaning and normalization
- All organization methods
- Data quality analysis

```bash
python tests/test_all_methods.py
```

## 🎨 Visualizations

Generated charts include:
- Depth distribution bar chart
- Domain distribution horizontal bar chart
- Protocol distribution pie chart (HTTP vs HTTPS)
- URL length histogram
- Crawl status pie chart

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Acknowledgments

Built with best practices:
- **NO REGEX for URL parsing** - Uses proper URL parsing libraries
- **Multi-language support** - Python, Node.js, Go
- **Comprehensive testing** - Validated with real data
- **Production-ready** - Clean code, proper error handling

## 🚀 Next Steps

1. Run the test suite: `python tests/test_all_methods.py`
2. Run full analysis: `python src/main.py --full`
3. Check output in `data/` directory
4. Modify `config/global.yaml` for your needs
5. Add your own organization methods in `src/organizers/`

---

**Remember:** Never use regex to parse URLs. Always use proper URL parsing libraries! 🎯
