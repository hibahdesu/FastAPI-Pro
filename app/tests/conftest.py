from app.db.database import get_db
from unittest.mock import Mock

mock_session = Mock()

def get_mock_session():
    yield mock_session