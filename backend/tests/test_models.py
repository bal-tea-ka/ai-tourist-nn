import pytest
from pydantic import ValidationError
from app.schemas.route import RouteRequest

def test_route_request_model_ok():
    model = RouteRequest(
        route_request="Короткая прогулка",
        minutes=60,
        language="ru",
        start_point=None,
        selected_categories=[]
    )
    assert model.route_request == "Короткая прогулка"

def test_route_request_model_invalid():
    with pytest.raises(ValidationError):
        # missing required field 'route_request'
        RouteRequest(minutes=30, language="ru", start_point=None, selected_categories=[])
    