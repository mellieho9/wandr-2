"""
Unit tests for Notion OAuth implementation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from clients.notion_client import NotionClient, NotionAPIError


class TestNotionClient:
    """Test cases for NotionClient"""
    
    def test_client_initialization(self):
        """Test that client initializes with access token"""
        token = "test_token_123"
        client = NotionClient(token)
        
        assert client.access_token == token
        assert client.client is not None
    
    @patch('clients.notion_client.Client')
    def test_get_databases_success(self, mock_client_class):
        """Test successful database retrieval"""
        # Mock the Notion client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock response
        mock_client.search.return_value = {
            "results": [
                {
                    "id": "db1",
                    "title": [{"plain_text": "Test DB"}],
                    "properties": {"Name": {"type": "title"}}
                }
            ]
        }
        
        client = NotionClient("test_token")
        databases = client.get_databases()
        
        assert len(databases) == 1
        assert databases[0]["id"] == "db1"
        assert databases[0]["title"] == "Test DB"
    
    @patch('clients.notion_client.Client')
    def test_get_database_schema_success(self, mock_client_class):
        """Test successful schema retrieval"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_client.databases.retrieve.return_value = {
            "id": "db1",
            "title": [{"plain_text": "Test DB"}],
            "properties": {
                "Name": {"type": "title"},
                "Tags": {"type": "multi_select"}
            }
        }
        
        client = NotionClient("test_token")
        schema = client.get_database_schema("db1")
        
        assert schema["id"] == "db1"
        assert schema["title"] == "Test DB"
        assert "Name" in schema["properties"]
        assert "Tags" in schema["properties"]
    
    @patch('clients.notion_client.Client')
    def test_create_page_success(self, mock_client_class):
        """Test successful page creation"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_client.pages.create.return_value = {
            "id": "page1",
            "properties": {}
        }
        
        client = NotionClient("test_token")
        properties = {"Name": {"title": [{"text": {"content": "Test"}}]}}
        page = client.create_page("db1", properties)
        
        assert page["id"] == "page1"
        mock_client.pages.create.assert_called_once()
    
    def test_extract_title_with_content(self):
        """Test title extraction from Notion title array"""
        client = NotionClient("test_token")
        
        title_array = [
            {"plain_text": "Hello "},
            {"plain_text": "World"}
        ]
        
        result = client._extract_title(title_array)
        assert result == "Hello World"
    
    def test_extract_title_empty(self):
        """Test title extraction with empty array"""
        client = NotionClient("test_token")
        result = client._extract_title([])
        assert result == ""


class TestOAuthEndpoints:
    """Test cases for OAuth endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        from app import app
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_notion_login_redirects(self, client):
        """Test that login endpoint redirects to Notion"""
        response = client.get('/auth/notion/login')
        assert response.status_code == 302  # Redirect
        assert 'notion.com' in response.location
        assert 'client_id' in response.location
        assert 'state' in response.location
    
    def test_callback_missing_code(self, client):
        """Test callback with missing code parameter"""
        response = client.get('/auth/notion/callback')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_callback_invalid_state(self, client):
        """Test callback with invalid state"""
        response = client.get('/auth/notion/callback?code=test&state=invalid')
        assert response.status_code == 400
        data = response.get_json()
        assert 'state' in data['error'].lower()
