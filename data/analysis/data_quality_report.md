# Data Quality Analysis Report

## Overview

- **total_records**: 9
- **unique_urls**: 9
- **unique_normalized_urls**: 9
- **unique_domains**: 2
- **depth_range**: {'min': 2, 'max': 6, 'avg': 3.2222222222222223}

## Strengths

✓ All URLs have discovery timestamps

✓ All URLs have queue timestamps

✓ No duplicate URLs in dataset

✓ Consistent protocol usage across all URLs


## Weaknesses

✗ No URLs have been crawled yet (all crawled_at timestamps are null)

✗ Content-type data is 0.0% complete

✗ Title data is 0.0% complete

✗ Some URLs use insecure HTTP protocol


## Recommendations

→ Begin crawling queued URLs to populate response data

→ Extract page titles during crawling for better content analysis

→ Consider upgrading HTTP URLs to HTTPS where possible

