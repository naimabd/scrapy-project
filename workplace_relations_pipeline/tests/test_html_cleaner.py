from workplace_relations_pipeline.transform.html_cleaner import extract_relevant_html


def test_extract_relevant_html_removes_layout_noise():
    html = b"""
    <html><body>
      <header>header</header>
      <nav>nav</nav>
      <main><h1>Title</h1><p>Important</p></main>
      <footer>footer</footer>
    </body></html>
    """
    out = extract_relevant_html(html).decode("utf-8").lower()
    assert "important" in out
    assert "<nav" not in out
    assert "<footer" not in out
