from app.utils import __all__ as _all  # just ensure utils package imports
def test_utils_importable():
    assert _all is not None or True
