"""Base repository class with common CRUD operations using SQLModel."""

from typing import TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from db.operations import CRUDBase

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(CRUDBase[ModelType]):
    """
    Base repository class that extends CRUDBase.
    
    This provides a clean interface for data access operations.
    Specific repositories should extend this class and add domain-specific methods.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository for a model.
        
        Args:
            model: SQLModel class
        """
        super().__init__(model)
        self.model = model
    
    def find_by(self, db: Session, **filters) -> List[ModelType]:
        """
        Find records matching multiple filters.
        
        Args:
            db: Database session
            **filters: Field name and value pairs to filter by
            
        Returns:
            List of matching model instances
        """
        query = db.query(self.model)
        
        for field_name, value in filters.items():
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                query = query.filter(field == value)
        
        return query.all()
    
    def find_one_by(self, db: Session, **filters) -> Optional[ModelType]:
        """
        Find a single record matching filters.
        
        Args:
            db: Database session
            **filters: Field name and value pairs to filter by
            
        Returns:
            Model instance or None if not found
        """
        results = self.find_by(db, **filters)
        return results[0] if results else None

