"""
Notion API Client Wrapper
Provides methods for OAuth authentication and database operations.
"""

import logging
from typing import List, Dict, Optional, Any
from notion_client import Client, APIResponseError

logger = logging.getLogger(__name__)


class NotionClientError(Exception):
    """Base exception for Notion client errors"""
    pass


class NotionAuthError(NotionClientError):
    """Exception for authentication errors"""
    pass


class NotionAPIError(NotionClientError):
    """Exception for API operation errors"""
    pass


class NotionClient:
    """
    Wrapper for Notion API operations.
    Handles OAuth token management and provides methods for database operations.
    """
    
    def __init__(self, access_token: str):
        """
        Initialize Notion client with access token.
        
        Args:
            access_token: Notion OAuth access token
        """
        self.access_token = access_token
        self.client = Client(auth=access_token)
        logger.info("Notion client initialized")
    
    def get_databases(self) -> List[Dict[str, Any]]:
        """
        List all databases accessible to the authenticated user.
        
        Returns:
            List of database objects with id, title, and properties
            
        Raises:
            NotionAPIError: If the API request fails
        """
        try:
            logger.info("Fetching user databases")
            response = self.client.search(filter={"property": "object", "value": "database"})
            
            databases = []
            for db in response.get("results", []):
                databases.append({
                    "id": db["id"],
                    "title": self._extract_title(db.get("title", [])),
                    "properties": db.get("properties", {})
                })
            
            logger.info(f"Retrieved {len(databases)} databases")
            return databases
            
        except APIResponseError as e:
            logger.error(f"Failed to fetch databases: {e}")
            raise NotionAPIError(f"Failed to fetch databases: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching databases: {e}")
            raise NotionAPIError(f"Unexpected error: {str(e)}")
    
    def get_database_schema(self, db_id: str) -> Dict[str, Any]:
        """
        Retrieve database schema/properties.
        
        Args:
            db_id: Notion database ID
            
        Returns:
            Dictionary containing database properties and their types
            
        Raises:
            NotionAPIError: If the API request fails
        """
        try:
            logger.info(f"Fetching schema for database {db_id}")
            database = self.client.databases.retrieve(database_id=db_id)
            
            schema = {
                "id": database["id"],
                "title": self._extract_title(database.get("title", [])),
                "properties": database.get("properties", {})
            }
            
            logger.info(f"Retrieved schema for database {db_id}")
            return schema
            
        except APIResponseError as e:
            logger.error(f"Failed to fetch database schema: {e}")
            raise NotionAPIError(f"Failed to fetch database schema: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching database schema: {e}")
            raise NotionAPIError(f"Unexpected error: {str(e)}")
    
    def query_database(
        self, 
        db_id: str, 
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query database with optional filters and sorts.
        
        Args:
            db_id: Notion database ID
            filter_conditions: Optional filter object
            sorts: Optional list of sort objects
            
        Returns:
            List of page objects matching the query
            
        Raises:
            NotionAPIError: If the API request fails
        """
        try:
            logger.info(f"Querying database {db_id}")
            
            query_params = {}
            if filter_conditions:
                query_params["filter"] = filter_conditions
            if sorts:
                query_params["sorts"] = sorts
            
            response = self.client.databases.query(
                database_id=db_id,
                **query_params
            )
            
            pages = response.get("results", [])
            logger.info(f"Query returned {len(pages)} pages")
            return pages
            
        except APIResponseError as e:
            logger.error(f"Failed to query database: {e}")
            raise NotionAPIError(f"Failed to query database: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error querying database: {e}")
            raise NotionAPIError(f"Unexpected error: {str(e)}")
    
    def create_page(self, db_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new page in a database.
        
        Args:
            db_id: Notion database ID
            properties: Page properties matching the database schema
            
        Returns:
            Created page object
            
        Raises:
            NotionAPIError: If the API request fails
        """
        try:
            logger.info(f"Creating page in database {db_id}")
            
            page = self.client.pages.create(
                parent={"database_id": db_id},
                properties=properties
            )
            
            logger.info(f"Created page {page['id']}")
            return page
            
        except APIResponseError as e:
            logger.error(f"Failed to create page: {e}")
            raise NotionAPIError(f"Failed to create page: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating page: {e}")
            raise NotionAPIError(f"Unexpected error: {str(e)}")
    
    def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing page's properties.
        
        Args:
            page_id: Notion page ID
            properties: Properties to update
            
        Returns:
            Updated page object
            
        Raises:
            NotionAPIError: If the API request fails
        """
        try:
            logger.info(f"Updating page {page_id}")
            
            page = self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            logger.info(f"Updated page {page_id}")
            return page
            
        except APIResponseError as e:
            logger.error(f"Failed to update page: {e}")
            raise NotionAPIError(f"Failed to update page: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating page: {e}")
            raise NotionAPIError(f"Unexpected error: {str(e)}")
    
    def _extract_title(self, title_array: List[Dict[str, Any]]) -> str:
        """
        Extract plain text from Notion title array.
        
        Args:
            title_array: Notion title array
            
        Returns:
            Plain text title
        """
        if not title_array:
            return ""
        
        return "".join([
            item.get("plain_text", "") 
            for item in title_array
        ])
    
    @staticmethod
    def refresh_token_if_needed(access_token: str) -> str:
        """
        Check if token needs refresh and refresh if necessary.
        Note: Notion OAuth tokens don't expire, but this method is here
        for future compatibility if Notion implements token refresh.
        
        Args:
            access_token: Current access token
            
        Returns:
            Valid access token (same as input for now)
        """
        # Notion OAuth tokens currently don't expire
        # This is a placeholder for future token refresh logic
        logger.debug("Token refresh check (Notion tokens don't expire)")
        return access_token
