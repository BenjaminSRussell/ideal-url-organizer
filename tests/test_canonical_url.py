from src.core.url_parser import URLParser

TRACKERS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid']


def test_tracker_only_query_removed():
    p = URLParser(tracker_params=TRACKERS)
    assert p.get_canonical_url('https://a.edu/x?utm_source=fb') == 'https://a.edu/x'
    assert p.get_canonical_url('https://a.edu/x?utm_source=fb&fbclid=1#frag') == 'https://a.edu/x'


def test_encoded_slash_and_question_preserved():
    p = URLParser(tracker_params=TRACKERS)
    assert p.get_canonical_url('https://a.edu/a%2Fb') == 'https://a.edu/a%2Fb'
    assert p.get_canonical_url('https://a.edu/a%2Fb') != p.get_canonical_url('https://a.edu/a/b')
    assert '%3F' in p.get_canonical_url('https://a.edu/p%3Fq=1')


def test_space_stays_percent20_tilde_decodes():
    p = URLParser(tracker_params=TRACKERS)
    assert p.get_canonical_url('https://a.edu/my%20file.pdf') == 'https://a.edu/my%20file.pdf'
    assert p.get_canonical_url('https://a.edu/a%7Eb') == 'https://a.edu/a~b'


def test_ipv6_brackets_roundtrip():
    p = URLParser(tracker_params=TRACKERS)
    assert p.get_canonical_url('http://[::1]:8080/x') == 'http://[::1]:8080/x'
