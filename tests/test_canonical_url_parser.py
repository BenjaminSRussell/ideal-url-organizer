"""Regression tests for URLParser.get_canonical_url (issue #10)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from core.url_parser import URLParser

TRACKERS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid', 'gclid', 'msclkid']


def test_strips_tracker_only_query():
    p = URLParser(TRACKERS)
    assert p.get_canonical_url('https://a.edu/x?utm_source=fb') == 'https://a.edu/x'


def test_strips_all_trackers_and_fragment():
    p = URLParser(TRACKERS)
    assert p.get_canonical_url('https://a.edu/x?utm_source=fb&fbclid=1#frag') == 'https://a.edu/x'


def test_keeps_encoded_slash_distinct():
    p = URLParser(TRACKERS)
    assert p.get_canonical_url('https://a.edu/a%2Fb') == 'https://a.edu/a%2Fb'


def test_keeps_encoded_question_in_path():
    p = URLParser(TRACKERS)
    assert p.get_canonical_url('https://a.edu/p%3Fq=1') == 'https://a.edu/p%3Fq=1'


def test_keeps_encoded_space():
    p = URLParser(TRACKERS)
    assert p.get_canonical_url('https://a.edu/my%20file.pdf') == 'https://a.edu/my%20file.pdf'


def test_preserves_ipv6_brackets():
    p = URLParser(TRACKERS)
    assert p.get_canonical_url('http://[::1]:8080/x') == 'http://[::1]:8080/x'


def test_keeps_non_tracker_params():
    p = URLParser(TRACKERS)
    out = p.get_canonical_url('https://a.edu/x?id=1&utm_source=fb')
    assert 'utm_source' not in out
    assert 'id=1' in out
