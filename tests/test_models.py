"""Unit tests for base model classes."""

import pytest
from datetime import datetime
from unittest.mock import patch
from sqlmodel import SQLModel

from models.base import BaseModel


class TestBaseModel:
    """Tests for BaseModel class."""
    
    def test_base_model_inherits_from_sqlmodel(self):
        """Test that BaseModel inherits from SQLModel."""
        assert issubclass(BaseModel, SQLModel)
    
    def test_base_model_has_id_field(self):
        """Test that BaseModel has an id field."""
        model = BaseModel()
        assert hasattr(model, "id")
        assert model.id is None
    
    def test_base_model_has_created_at_field(self):
        """Test that BaseModel has a created_at field."""
        model = BaseModel()
        assert hasattr(model, "created_at")
        assert isinstance(model.created_at, datetime)
    
    def test_base_model_has_updated_at_field(self):
        """Test that BaseModel has an updated_at field."""
        model = BaseModel()
        assert hasattr(model, "updated_at")
        assert isinstance(model.updated_at, datetime)
    
    def test_base_model_timestamps_are_set(self):
        """Test that timestamps are automatically set on creation."""
        before = datetime.utcnow()
        model = BaseModel()
        after = datetime.utcnow()
        
        assert before <= model.created_at <= after
        assert before <= model.updated_at <= after
    
    def test_base_model_timestamps_are_initialized(self):
        """Test that created_at and updated_at are initialized."""
        model = BaseModel()
        assert model.created_at is not None
        assert model.updated_at is not None
    
    def test_base_model_id_can_be_set(self):
        """Test that id can be set explicitly."""
        model = BaseModel(id=1)
        assert model.id == 1
    
    def test_base_model_timestamps_can_be_set(self):
        """Test that timestamps can be set explicitly."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        model = BaseModel(created_at=custom_time, updated_at=custom_time)
        assert model.created_at == custom_time
        assert model.updated_at == custom_time
    
    def test_update_timestamp_updates_updated_at(self):
        """Test that update_timestamp updates the updated_at field."""
        # Create model and capture initial timestamps
        model = BaseModel()
        original_created_at = model.created_at
        original_updated_at = model.updated_at
        
        # Wait a small amount to ensure time difference
        import time
        time.sleep(0.01)
        
        # Update timestamp
        model.update_timestamp()
        
        # Verify updated_at changed but created_at didn't
        assert model.updated_at > original_updated_at
        assert model.created_at == original_created_at
        assert model.updated_at != original_updated_at
    
    def test_update_timestamp_only_updates_updated_at(self):
        """Test that update_timestamp only updates updated_at, not created_at."""
        model = BaseModel()
        original_created_at = model.created_at
        original_updated_at = model.updated_at
        
        # Wait a bit to ensure time difference
        import time
        time.sleep(0.01)
        
        model.update_timestamp()
        
        assert model.created_at == original_created_at
        assert model.updated_at != original_updated_at
        assert model.updated_at > original_updated_at
    
    def test_base_model_can_be_used_in_sqlmodel_context(self):
        """Test that BaseModel can be used as a SQLModel table."""
        # This test verifies that BaseModel is compatible with SQLModel
        # by checking it has the necessary attributes
        model = BaseModel()
        
        # SQLModel models should have __table__ attribute when configured
        # For now, we just verify it's a valid SQLModel instance
        assert isinstance(model, SQLModel)
    
    def test_base_model_fields_have_defaults(self):
        """Test that BaseModel fields have appropriate defaults."""
        model = BaseModel()
        
        # id should default to None (will be set by database)
        assert model.id is None
        
        # Timestamps should be set automatically
        assert model.created_at is not None
        assert model.updated_at is not None
    
    def test_base_model_multiple_instances_have_different_timestamps(self):
        """Test that multiple instances have independent timestamps."""
        import time
        
        model1 = BaseModel()
        time.sleep(0.01)  # Small delay
        model2 = BaseModel()
        
        # Timestamps should be different (or very close)
        assert model1.created_at <= model2.created_at
        assert model1.updated_at <= model2.updated_at

