import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Import the GCP class
from gcp import GCP


class TestResponseSchema(BaseModel):
    """Test response schema for testing"""
    message: str
    status: str


class ComplexResponseSchema(BaseModel):
    """More complex response schema for testing"""
    id: int
    name: str
    tags: List[str]
    metadata: Dict[str, Any]
    is_active: bool


class TestGCP:
    """Test class for GCP functionality"""
    
    @pytest.fixture
    def gcp_instance(self):
        """Fixture to create a GCP instance for testing"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'}):
            with patch('gcp.genai.Client') as mock_client:
                mock_client.return_value = Mock()
                return GCP()
    
    def test_gcp_initialization(self, gcp_instance):
        """Test GCP class initialization"""
        assert gcp_instance.tools == []
        assert gcp_instance.messages == []
        assert gcp_instance.response_schema is None
        assert gcp_instance.client is not None
    
    def test_config_without_schema(self, gcp_instance):
        """Test config method without response schema"""
        system_message = "You are a helpful assistant"
        gcp_instance.config(system_message)
        
        assert gcp_instance.system_message == system_message
        assert gcp_instance.model == "gemini-2.5-flash"
        assert gcp_instance.response_schema is None
        assert gcp_instance.config is not None
    
    def test_config_with_schema(self, gcp_instance):
        """Test config method with response schema"""
        system_message = "You are a helpful assistant"
        response_schema = TestResponseSchema
        
        gcp_instance.config(system_message, response_schema)
        
        assert gcp_instance.system_message == system_message
        assert gcp_instance.model == "gemini-2.5-flash"
        assert gcp_instance.response_schema == response_schema
        assert gcp_instance.config is not None
    
    def test_config_custom_model(self, gcp_instance):
        """Test config method with custom model"""
        system_message = "You are a helpful assistant"
        custom_model = "gemini-1.5-pro"
        
        gcp_instance.config(system_message, model=custom_model)
        
        assert gcp_instance.model == custom_model
    
    @pytest.mark.asyncio
    async def test_generate_stream(self, gcp_instance):
        """Test generate_stream method"""
        # Mock the client and its methods
        mock_chunk1 = Mock()
        mock_chunk1.text = "Hello"
        mock_chunk2 = Mock()
        mock_chunk2.text = " World"
        
        async def mock_stream():
            yield mock_chunk1
            yield mock_chunk2
        
        with patch.object(gcp_instance.client.aio.models, 'generate_content_stream') as mock_generate:
            mock_generate.return_value = mock_stream()
            
            # Configure the instance
            gcp_instance.config("You are a helpful assistant")
            
            # Test the stream generation
            text = "Test message"
            chunks = []
            async for chunk in gcp_instance.generate_stream(text):
                chunks.append(chunk)
            
            # Verify results
            assert len(chunks) == 2
            assert chunks[0] == "Hello"
            assert chunks[1] == " World"
            assert gcp_instance.response_text == "Hello World"
            assert len(gcp_instance.messages) == 2  # user message + model response
    
    @pytest.mark.asyncio
    async def test_clean_response_without_schema(self, gcp_instance):
        """Test clean_response method without schema"""
        gcp_instance.response_text = "Hello World"
        gcp_instance.response_schema = None
        
        result = await gcp_instance.clean_response()
        
        assert result == "Hello World"
    
    @pytest.mark.asyncio
    async def test_clean_response_with_schema(self, gcp_instance):
        """Test clean_response method with schema"""
        json_response = '{"message": "Hello", "status": "success"}'
        gcp_instance.response_text = json_response
        gcp_instance.response_schema = TestResponseSchema
        
        result = await gcp_instance.clean_response()
        
        assert isinstance(result, TestResponseSchema)
        assert result.message == "Hello"
        assert result.status == "success"
    
    @pytest.mark.asyncio
    async def test_clean_response_with_complex_schema(self, gcp_instance):
        """Test clean_response method with complex schema"""
        json_response = '''
        {
            "id": 123,
            "name": "Test Item",
            "tags": ["tag1", "tag2", "tag3"],
            "metadata": {"key1": "value1", "key2": 42},
            "is_active": true
        }
        '''
        gcp_instance.response_text = json_response
        gcp_instance.response_schema = ComplexResponseSchema
        
        result = await gcp_instance.clean_response()
        
        assert isinstance(result, ComplexResponseSchema)
        assert result.id == 123
        assert result.name == "Test Item"
        assert result.tags == ["tag1", "tag2", "tag3"]
        assert result.metadata == {"key1": "value1", "key2": 42}
        assert result.is_active is True
    
    @pytest.mark.asyncio
    async def test_clean_response_schema_validation_error(self, gcp_instance):
        """Test clean_response method with invalid JSON for schema"""
        invalid_json = '{"message": "Hello", "status": "success"'  # Missing closing brace
        gcp_instance.response_text = invalid_json
        gcp_instance.response_schema = TestResponseSchema
        
        with pytest.raises(Exception):  # Should raise validation error
            await gcp_instance.clean_response()
    
    @pytest.mark.asyncio
    async def test_clean_response_schema_missing_fields(self, gcp_instance):
        """Test clean_response method with missing required fields"""
        incomplete_json = '{"message": "Hello"}'  # Missing 'status' field
        gcp_instance.response_text = incomplete_json
        gcp_instance.response_schema = TestResponseSchema
        
        with pytest.raises(Exception):  # Should raise validation error
            await gcp_instance.clean_response()
    
    @pytest.mark.asyncio
    async def test_clean_response_schema_wrong_types(self, gcp_instance):
        """Test clean_response method with wrong data types"""
        wrong_types_json = '{"message": 123, "status": "success"}'  # message should be string
        gcp_instance.response_text = wrong_types_json
        gcp_instance.response_schema = TestResponseSchema
        
        with pytest.raises(Exception):  # Should raise validation error
            await gcp_instance.clean_response()
    
    @pytest.mark.asyncio
    async def test_clean_response_with_custom_text(self, gcp_instance):
        """Test clean_response method with custom text parameter"""
        custom_text = "Custom response"
        gcp_instance.response_text = "Original response"
        gcp_instance.response_schema = None
        
        result = await gcp_instance.clean_response(custom_text)
        
        assert result == custom_text
    
    def test_missing_api_key(self):
        """Test initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                # This should fail because the client expects an API key
                GCP()
    
    @pytest.mark.asyncio
    async def test_generate_stream_empty_response(self, gcp_instance):
        """Test generate_stream with empty response"""
        async def mock_empty_stream():
            if False:
                yield None
        
        with patch.object(gcp_instance.client.aio.models, 'generate_content_stream') as mock_generate:
            mock_generate.return_value = mock_empty_stream()
            
            gcp_instance.config("You are a helpful assistant")
            
            chunks = []
            async for chunk in gcp_instance.generate_stream("Test"):
                chunks.append(chunk)
            
            assert len(chunks) == 0
            assert gcp_instance.response_text == ""
            assert len(gcp_instance.messages) == 2  # Still adds user and empty model message
    
    @pytest.mark.asyncio
    async def test_end_to_end_with_schema(self, gcp_instance):
        """Test complete flow: config with schema -> generate stream -> clean response"""
        # Mock the stream response
        mock_chunk1 = Mock()
        mock_chunk1.text = '{"message": "Hello from AI", "status": "success"}'
        
        async def mock_stream():
            yield mock_chunk1
        
        with patch.object(gcp_instance.client.aio.models, 'generate_content_stream') as mock_generate:
            mock_generate.return_value = mock_stream()
            
            # Configure with schema
            gcp_instance.config("You are a helpful assistant", TestResponseSchema)
            
            # Generate stream
            chunks = []
            async for chunk in gcp_instance.generate_stream("Generate a response"):
                chunks.append(chunk)
            
            # Clean response with schema
            result = await gcp_instance.clean_response()
            
            # Verify the complete flow
            assert len(chunks) == 1
            assert chunks[0] == '{"message": "Hello from AI", "status": "success"}'
            assert gcp_instance.response_text == '{"message": "Hello from AI", "status": "success"}'
            assert isinstance(result, TestResponseSchema)
            assert result.message == "Hello from AI"
            assert result.status == "success"
            assert len(gcp_instance.messages) == 2
    
    @pytest.mark.asyncio
    async def test_end_to_end_with_complex_schema(self, gcp_instance):
        """Test complete flow with complex schema"""
        # Mock the stream response
        mock_chunk1 = Mock()
        mock_chunk1.text = '{"id": 456, "name": "Complex Item", "tags": ["test", "demo"], "metadata": {"version": "1.0"}, "is_active": false}'
        
        async def mock_stream():
            yield mock_chunk1
        
        with patch.object(gcp_instance.client.aio.models, 'generate_content_stream') as mock_generate:
            mock_generate.return_value = mock_stream()
            
            # Configure with complex schema
            gcp_instance.config("You are a helpful assistant", ComplexResponseSchema)
            
            # Generate stream
            chunks = []
            async for chunk in gcp_instance.generate_stream("Generate a complex response"):
                chunks.append(chunk)
            
            # Clean response with schema
            result = await gcp_instance.clean_response()
            
            # Verify the complete flow
            assert len(chunks) == 1
            assert isinstance(result, ComplexResponseSchema)
            assert result.id == 456
            assert result.name == "Complex Item"
            assert result.tags == ["test", "demo"]
            assert result.metadata == {"version": "1.0"}
            assert result.is_active is False
    
    @pytest.mark.asyncio
    async def test_config_with_schema_affects_generate_content_config(self, gcp_instance):
        """Test that config with schema properly sets up GenerateContentConfig"""
        system_message = "You are a helpful assistant"
        response_schema = TestResponseSchema
        
        gcp_instance.config(system_message, response_schema)
        
        # Verify the config is set up correctly for schema
        assert gcp_instance.config is not None
        assert gcp_instance.config.response_mime_type == "application/json"
        assert gcp_instance.config.response_schema == response_schema
    
    @pytest.mark.asyncio
    async def test_config_without_schema_affects_generate_content_config(self, gcp_instance):
        """Test that config without schema properly sets up GenerateContentConfig"""
        system_message = "You are a helpful assistant"
        
        gcp_instance.config(system_message)
        
        # Verify the config is set up correctly without schema
        assert gcp_instance.config is not None
        # When no schema is provided, response_mime_type and response_schema should be None
        assert gcp_instance.config.response_mime_type is None
        assert gcp_instance.config.response_schema is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
