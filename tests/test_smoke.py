def test_imports():
    import seoworkbench
    from seoworkbench.api.main import app
    assert hasattr(app, "openapi")

