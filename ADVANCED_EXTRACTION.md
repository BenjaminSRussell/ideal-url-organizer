# Advanced Content Extraction Techniques

## The Problem with Basic HTML Parsing

**Basic scraping**: Download HTML → Parse with BeautifulSoup → Extract text with CSS selectors

**Problems**:
- Fragile (breaks when CSS classes change)
- Messy (extracting "$49.99" from text is unreliable)
- Incomplete (misses JavaScript-rendered content)
- Slow (parsing large HTML files)

**The solution**: Don't parse HTML at all! Get the clean, structured data directly.

---

## The 5 Expert Extraction Techniques

### 1. **API Reverse Engineering** (THE GOLDMINE!)

**What it is**: Find the hidden JSON API that the page itself uses to load data.

**Why it's better**:
- **Structured**: Clean JSON like `{"course_code": "MUS-101", "price": 599}`
- **Complete**: Often has MORE data than shown on the page
- **Fast**: Small JSON response vs large HTML file
- **Reliable**: APIs don't change as often as HTML

**How to find it**:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Load the page
5. Look for JSON responses

**Example**:
```
Page URL: https://catalog.hartford.edu/courses/MUS-101
API URL: https://catalog.hartford.edu/api/v1/courses/MUS-101

Response:
{
 "id": 12345,
 "code": "MUS-101",
 "title": "Introduction to Music Theory",
 "credits": 3,
 "professor": {
 "id": 789,
 "name": "Dr. Jane Smith"
 }
}
```

**Implementation**:
```python
from src.core.advanced_extraction import APIReverseEngineer

engineer = APIReverseEngineer()

# Auto-detect API endpoints from HTML
endpoints = engineer.detect_api_endpoints(html, base_url)

# Fetch clean JSON data
api_data = engineer.fetch_api_data(endpoints[0])
```

**What it detects**:
- `fetch('/api/courses')`
- `axios.get('/v1/data')`
- `$.ajax('/rest/products')`
- Any URL containing `/api/`, `/v1/`, `.json`, `/graphql`

---

### 2. **Embedded Data Extraction** (The Hydration State)

**What it is**: Modern sites embed JSON directly in `<script>` tags for fast page loading.

**Why it's better**:
- Same as API data - clean, structured JSON
- No extra HTTP request needed
- Often the COMPLETE page state

**Common patterns**:
```javascript
window.__INITIAL_STATE__ = {...};
window.__PRELOADED_STATE__ = {...};
window.__NEXT_DATA__ = {...}; // Next.js
window.__NUXT__ = {...}; // Nuxt.js
var data = {...};
```

**Example**:
```html
<script>
window.__INITIAL_STATE__ = {
 "course": {
 "id": 12345,
 "title": "Music Theory 101",
 "professor": "Dr. Jane Smith",
 "credits": 3,
 "price": 599
 },
 "reviews": [...],
 "related_courses": [...]
};
</script>
```

**Implementation**:
```python
from src.core.advanced_extraction import EmbeddedDataExtractor

extractor = EmbeddedDataExtractor()
embedded_json = extractor.extract_embedded_json(html)

# You now have ALL the page data as clean JSON!
course_data = embedded_json[0]['course']
```

**What it extracts**:
- Hydration state variables
- JSON-LD (Schema.org structured data)
- Next.js / Nuxt.js app state
- Any JavaScript object literals

---

### 3. **LLM-Based Parsing** (Selector-less Extraction)

**What it is**: Use AI to extract data using natural language instead of fragile CSS selectors.

**Why it's better**:
- **Resilient**: Works even after website redesign
- **No selectors**: Just describe what you want
- **Flexible**: Can extract anything you can describe

**The problem with selectors**:
```python
# This breaks when developer changes class names
price = soup.select('div.product > span.price-tag')[0].text
```

**The LLM solution**:
```python
from src.core.advanced_extraction import LLMParser

parser = LLMParser()

# Define what you want as plain English
schema = {
 'course_title': 'The course title',
 'course_code': 'The course code (like MUS-101)',
 'professor': 'The professor teaching the course',
 'price': 'The course price in dollars'
}

# LLM extracts it regardless of HTML structure
data = parser.extract_with_llm(html, schema)

# Returns:
{
 "course_title": "Introduction to Music Theory",
 "course_code": "MUS-101",
 "professor": "Dr. Jane Smith",
 "price": "$599"
}
```

**Setup** (local, free):
```bash
# Install Ollama (local LLM server)
brew install ollama # or download from ollama.ai

# Download a model
ollama pull llama3:8b

# Start server
ollama serve
```

**Advantages**:
- Works with any website structure
- Can extract complex relationships
- No maintenance when site changes
- Understands context and semantics

---

### 4. **Computer Vision & OCR** (Extract from Images)

**What it is**: Use Optical Character Recognition to read text from images.

**Why you need it**:
Some data is ONLY in images:
- Marketing banners
- Infographics with key stats
- Charts and graphs
- Scanned documents/PDFs
- Screenshots

**Example use cases**:
- Event posters with dates/times
- Product images with specs overlaid
- Certificates/diplomas
- Historical documents

**Implementation**:
```python
from src.core.advanced_extraction import OCRExtractor

extractor = OCRExtractor()

# Extract text from all images on the page
image_texts = extractor.extract_text_from_images(html, base_url)

# Returns:
{
 "https://example.com/banner.jpg": "Summer Concert Series\nJuly 15-20, 2024\nTickets $25",
 "https://example.com/chart.png": "Revenue Growth: 35% YoY"
}
```

**Setup**:
```bash
# Install Tesseract OCR
brew install tesseract # macOS
sudo apt install tesseract-ocr # Linux

# Install Python wrapper
pip install pytesseract Pillow
```

**Advanced**: Cloud Vision APIs (Google, AWS, Azure) are more accurate but cost money.

---

### 5. **DOM Data Attributes** (Machine-Readable Metadata)

**What it is**: Extract `data-*` attributes that developers use for JavaScript.

**Why it's better**:
- More **reliable** than parsing text
- More **structured** than HTML content
- More **stable** (doesn't change in redesigns)

**Example**:
```html
<div class="product"
 data-product-id="12345"
 data-sku="MUS-101-FALL"
 data-price-cents="59900"
 data-in-stock="true"
 data-category="music-theory">

 <h2>Introduction to Music Theory</h2>
 <span class="price">$599.00</span>
</div>
```

**Bad way** (parsing text):
```python
price_text = soup.select('.price')[0].text # "$599.00"
price = float(price_text.replace('$', '').replace(',', '')) # Fragile!
```

**Good way** (data attributes):
```python
from src.core.advanced_extraction import DataAttributeExtractor

extractor = DataAttributeExtractor()
data = extractor.extract_data_attributes(html)

# Returns clean, structured data:
{
 "product_0": {
 "attributes": {
 "data-product-id": "12345",
 "data-price-cents": "59900", # Already an integer!
 "data-in-stock": "true",
 "data-category": "music-theory"
 }
 }
}
```

**Common data attributes**:
- E-commerce: `data-product-id`, `data-price`, `data-sku`, `data-variant`
- Education: `data-course-id`, `data-semester`, `data-credits`
- Events: `data-event-id`, `data-date`, `data-venue`
- Analytics: `data-track-click`, `data-category`, `data-label`

---

## The Complete Extraction Pipeline

Use **all 5 techniques** together for maximum data coverage:

```python
from src.core.advanced_extraction import AdvancedContentExtractor

# Initialize with all features
extractor = AdvancedContentExtractor(
 use_ocr=True, # Enable image text extraction
 use_llm=True # Enable AI parsing
)

# Run complete extraction
result = extractor.extract_all(html, url)

# Now you have:
print(result.api_endpoints) # Hidden APIs found
print(result.api_data) # Clean JSON from API
print(result.embedded_json) # Hydration state data
print(result.data_attributes) # All data-* attributes
print(result.image_text) # Text from images (OCR)
print(result.llm_extracted) # AI-extracted fields
```

**Example output**:
```python
result.api_endpoints = [
 'https://catalog.hartford.edu/api/v1/courses/12345',
 'https://catalog.hartford.edu/api/v1/professors/789'
]

result.api_data = {
 "id": 12345,
 "code": "MUS-101",
 "title": "Introduction to Music Theory",
 "credits": 3
}

result.embedded_json = [
 {
 "course": {"id": 12345, "title": "Music Theory 101"},
 "professor": {"name": "Dr. Jane Smith"}
 }
]

result.data_attributes = {
 "course_0": {
 "attributes": {
 "data-course-id": "12345",
 "data-price": "599"
 }
 }
}

result.image_text = {
 "https://site.com/syllabus.jpg": "Course Syllabus\nSpring 2024"
}

result.llm_extracted = {
 "course_title": "Introduction to Music Theory",
 "professor": "Dr. Jane Smith",
 "price": "$599"
}
```

---

## Comparison: Before vs After

### Before (Basic HTML Parsing)
```python
soup = BeautifulSoup(html, 'html.parser')

# Fragile selectors
title = soup.select('div.course-info > h2.title')[0].text

# Messy text parsing
price_text = soup.select('span.price')[0].text # "$599.00"
price = float(price_text.replace('$', '').replace(',', ''))

# Missed JavaScript content
# Missed API data
# Missed embedded JSON
# Missed data attributes
```

### After (Advanced Extraction)
```python
extractor = AdvancedContentExtractor()
result = extractor.extract_all(html, url)

# Clean, structured data
course = result.api_data # or result.embedded_json[0]

title = course['title']
price = course['price'] # Already a number!
professor = course['professor']['name']
```

**Benefits**:
- 10x more reliable
- 10x faster to write
- 10x easier to maintain
- Gets MORE data
- Resilient to website changes

---

## Real-World Examples

### Example 1: University Course Catalog

**Traditional approach**:
```python
# Fragile, breaks on redesign
courses = soup.select('div.course-card')
for course in courses:
 title = course.select_one('h3.course-title').text
 code = course.select_one('span.code').text
 # Many more fragile selectors...
```

**Advanced approach**:
```python
# Option 1: API (best)
api_url = engineer.detect_api_endpoints(html, url)[0]
courses = engineer.fetch_api_data(api_url)['courses']

# Option 2: Embedded data
state = embedded_extractor.extract_embedded_json(html)[0]
courses = state['courses']

# Option 3: LLM (most resilient)
courses = llm_parser.extract_with_llm(html, {
 'courses': 'List all courses with title, code, and professor'
})
```

### Example 2: E-commerce Product

**Traditional approach**:
```python
# Parsing text is unreliable
price = soup.select('.price')[0].text # "$1,299.99"
stock = 'In Stock' in soup.get_text() # Fragile!
```

**Advanced approach**:
```python
# Data attributes (most reliable for e-commerce)
attrs = data_attr_extractor.extract_data_attributes(html)
product = attrs['product_0']['attributes']

price = int(product['data-price-cents']) / 100 # 129999 → 1299.99
in_stock = product['data-in-stock'] == 'true' # Boolean!
sku = product['data-sku']
```

### Example 3: News Article with Images

**Advanced approach**:
```python
# Extract embedded article data
article_data = embedded_extractor.extract_embedded_json(html)[0]

title = article_data['headline']
author = article_data['author']['name']
publish_date = article_data['datePublished']

# PLUS extract text from images/infographics
image_texts = ocr_extractor.extract_text_from_images(html, url)

# Now you have data that wasn't even in the HTML!
```

---

## Installation

```bash
# Basic (API + Embedded Data + Data Attributes)
pip install beautifulsoup4 requests

# OCR support
brew install tesseract # or apt install tesseract-ocr
pip install pytesseract Pillow

# LLM support (local, free)
# Install Ollama from ollama.ai
ollama pull llama3:8b
```

---

## Best Practices

### 1. **Try techniques in order**:
1. API Reverse Engineering (fastest, cleanest)
2. Embedded Data Extraction (fast, no extra request)
3. Data Attributes (reliable, structured)
4. LLM Parsing (resilient, flexible)
5. OCR (only for images)

### 2. **Cache API/embedded data**:
```python
# Once you find the API, save it
if api_data:
 save_to_cache(url, api_data)
 # Don't parse HTML next time!
```

### 3. **Validate extracted data**:
```python
# Always check if extraction worked
if not result.api_data and not result.embedded_json:
 # Fall back to traditional parsing
 fallback_parse(html)
```

### 4. **Use LLM for one-time extraction**:
LLMs are slow. Use them to:
- Discover the data structure once
- Then write code to extract it directly

---

## The Bottom Line

**Stop parsing HTML like it's 2010!**

Modern websites give you their data in **5 better ways**:

1. **APIs** - Clean JSON endpoints
2. **Embedded JSON** - Hydration state in `<script>` tags
3. **Data Attributes** - Machine-readable `data-*` fields
4. **Images** - OCR for visual content
5. **AI** - LLM parsing for anything

**This is how production scrapers work in 2025!**

Your system now has all 5 techniques implemented in `src/core/advanced_extraction.py`.

---

## Further Reading

- **API Reverse Engineering**: [Chrome DevTools Network Tab](https://developer.chrome.com/docs/devtools/network/)
- **JSON-LD**: [Schema.org Documentation](https://schema.org/)
- **Tesseract OCR**: [tesseract-ocr.github.io](https://tesseract-ocr.github.io/)
- **Ollama**: [ollama.ai](https://ollama.ai/)

---

**Remember**: The best data is the data you don't have to parse! 
