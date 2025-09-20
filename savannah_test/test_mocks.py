import os
import requests
from unittest.mock import Mock, patch

# Mock all HTTP requests during testing
def mock_requests_get(*args, **kwargs):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "test", "message": "Mocked response"}
    mock_response.text = "Mocked response"
    return mock_response

def mock_requests_post(*args, **kwargs):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "test", "message": "Mocked response"}
    mock_response.text = "Mocked response"
    return mock_response

# Apply mocks if in testing mode
if os.getenv('TESTING') == 'True':
    requests.get = mock_requests_get
    requests.post = mock_requests_post
    print("HTTP requests mocked for testing")