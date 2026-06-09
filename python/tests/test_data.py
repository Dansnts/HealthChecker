from data import add_result, get_result


def test_add_result():
    add_result("https://example.com", "2026-06-07T00:00:00Z", 54.34, "200")

    results = get_result()

    assert "https://example.com" in results
    assert results["https://example.com"][0]["status_code"] == "200"
    assert results["https://example.com"][0]["response_time_ms"] == 54.34


def test_get_result_empty():
    assert get_result() == {}


def test_deque_bounded_at_100():
    url = "https://example.com"
    for i in range(110):
        add_result(url, "2026-06-07T00:00:00Z", 1.0, "200")

    assert len(get_result()[url]) == 100
