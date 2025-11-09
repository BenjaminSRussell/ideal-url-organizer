#!/usr/bin/env python3
"""
Demo: Expert-Level Content-Based Analysis

This demonstrates the BIG MISSING PIECE that was added:
1. Web crawling and content extraction
2. Text embeddings for semantic similarity
3. Named Entity Recognition
4. Topic modeling
5. PageRank/HITS link analysis
6. Content-based organization methods
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.web_crawler import WebCrawler, ContentExtractor
from src.analyzers.semantic_analyzer import SemanticAnalyzer, EMBEDDINGS_AVAILABLE, NER_AVAILABLE, TOPIC_MODELING_AVAILABLE
from src.analyzers.link_graph_analyzer import LinkGraphAnalyzer, NETWORKX_AVAILABLE
from src.core.data_loader import DataLoader


def demo_web_crawling():
    """Demo: Web crawling and content extraction"""
    print("\n" + "="*80)
    print("DEMO 1: WEB CRAWLING & CONTENT EXTRACTION")
    print("="*80)
    print("\nThe BIG MISSING PIECE - Actually fetch page content!")

    # Load URLs from sample data
    loader = DataLoader()
    records = loader.load()

    print(f"\nFetching content from {len(records)} URLs...")
    print("(This will actually make HTTP requests)")

    # Create crawler
    crawler = WebCrawler(delay_between_requests=0.5)  # Be polite!

    # Fetch first 3 URLs as demo
    pages = []
    for idx, record in enumerate(records[:3], 1):
        print(f"\n[{idx}/3] Fetching: {record.url}")

        content = crawler.fetch(record.url)
        if content:
            pages.append(content)

            print(f"  ✓ Status Code: {content.status_code}")
            print(f"  ✓ Final URL: {content.final_url}")
            print(f"  ✓ Response Time: {content.response_time_ms}ms")

            if content.redirect_chain:
                print(f"  ✓ Redirects: {len(content.redirect_chain)}")

            print(f"  ✓ Title: {content.title}")
            print(f"  ✓ Text Length: {content.text_length} characters")

            if content.h1_tags:
                print(f"  ✓ H1 Tags: {len(content.h1_tags)}")

            print(f"  ✓ Internal Links: {len(content.internal_links)}")
            print(f"  ✓ External Links: {len(content.external_links)}")

            if content.schema_org_types:
                print(f"  ✓ Schema.org Types: {', '.join(content.schema_org_types)}")
        else:
            print(f"  ✗ Failed to fetch")

    print(f"\n✓ Successfully fetched {len(pages)} pages")
    return pages


def demo_semantic_analysis(pages):
    """Demo: Semantic analysis with embeddings, NER, and topic modeling"""
    print("\n" + "="*80)
    print("DEMO 2: EXPERT-LEVEL SEMANTIC ANALYSIS")
    print("="*80)

    if not pages:
        print("No pages to analyze. Run demo_web_crawling() first.")
        return

    analyzer = SemanticAnalyzer()

    print("\nAvailable features:")
    print(f"  • Text Embeddings: {'✓ Available' if EMBEDDINGS_AVAILABLE else '✗ Not installed'}")
    print(f"  • Named Entity Recognition: {'✓ Available' if NER_AVAILABLE else '✗ Not installed'}")
    print(f"  • Topic Modeling: {'✓ Available' if TOPIC_MODELING_AVAILABLE else '✗ Not installed'}")

    if not any([EMBEDDINGS_AVAILABLE, NER_AVAILABLE, TOPIC_MODELING_AVAILABLE]):
        print("\nInstall expert features:")
        print("  pip install sentence-transformers spacy scikit-learn")
        print("  python -m spacy download en_core_web_sm")
        return

    print("\n" + "-"*80)
    print("Running semantic analysis...")
    print("-"*80)

    analysis = analyzer.analyze(pages)

    print("\n✓ Semantic analysis complete!")
    print(f"  See results in: data/analysis/semantic/")


def demo_link_graph_analysis(pages):
    """Demo: PageRank and HITS link analysis"""
    print("\n" + "="*80)
    print("DEMO 3: LINK GRAPH ANALYSIS (PageRank & HITS)")
    print("="*80)

    if not NETWORKX_AVAILABLE:
        print("NetworkX not installed. Run: pip install networkx")
        return

    if not pages:
        print("No pages to analyze. Run demo_web_crawling() first.")
        return

    print("\nThis finds the most important/authoritative pages")
    print("Based on link structure (what Google uses!)")

    analyzer = LinkGraphAnalyzer()
    analysis = analyzer.analyze(pages)

    print("\n✓ Link graph analysis complete!")
    print(f"  See results in: data/analysis/link_graph/")


def demo_content_based_organization(pages):
    """Demo: New content-based organization methods"""
    print("\n" + "="*80)
    print("DEMO 4: CONTENT-BASED ORGANIZATION METHODS")
    print("="*80)

    if not pages:
        print("No pages to analyze. Run demo_web_crawling() first.")
        return

    print("\nNew organization methods using actual page content:")
    print("  • Method 22: By HTTP Status Code (reveals link rot)")
    print("  • Method 23: By Schema.org Type (semantic categories)")
    print("  • Method 24: By Page Authority (PageRank)")
    print("  • Method 25: By Semantic Similarity (meaning, not keywords!)")

    # Demo Method 22: HTTP Status
    from src.organizers.method_22_by_http_status import ByHTTPStatusOrganizer

    output_dir = Path(__file__).parent / 'data' / 'processed' / 'method_22_by_http_status'
    organizer = ByHTTPStatusOrganizer(output_dir)
    organizer.run(pages)

    # Demo Method 23: Schema.org
    from src.organizers.method_23_by_schema_org_type import BySchemaOrgTypeOrganizer

    output_dir = Path(__file__).parent / 'data' / 'processed' / 'method_23_by_schema_org_type'
    organizer = BySchemaOrgTypeOrganizer(output_dir)
    organizer.run(pages)

    print("\n✓ Content-based organization complete!")


def main():
    """Run all demos"""
    print("="*80)
    print("EXPERT-LEVEL URL ANALYSIS - COMPLETE DEMO")
    print("="*80)
    print("\nThis demonstrates ALL the expert features:")
    print("  1. Web crawling & content extraction")
    print("  2. Text embeddings (find similar pages by MEANING)")
    print("  3. Named Entity Recognition (extract people, orgs, locations)")
    print("  4. Topic modeling (auto-discover categories)")
    print("  5. PageRank/HITS (find important pages)")
    print("  6. Content-based organization (22-25 new methods)")

    try:
        # 1. Crawl pages
        pages = demo_web_crawling()

        if pages:
            # 2. Semantic analysis
            demo_semantic_analysis(pages)

            # 3. Link graph analysis
            demo_link_graph_analysis(pages)

            # 4. Content-based organization
            demo_content_based_organization(pages)

        print("\n" + "="*80)
        print("ALL DEMOS COMPLETE!")
        print("="*80)
        print("\nWhat you just saw:")
        print("  ✓ Actual web crawling (HTTP requests)")
        print("  ✓ Content extraction (title, text, links, structured data)")
        print("  ✓ Semantic similarity (vector embeddings)")
        print("  ✓ Entity recognition (NER)")
        print("  ✓ PageRank (like Google!)")
        print("  ✓ Content-based organization")

        print("\nThis is THE KEY to serious web content analysis!")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
