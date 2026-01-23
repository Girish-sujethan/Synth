"""Generic CRUD operations base class with SQLModel integration."""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class CRUDBase(Generic[ModelType]):
    """
    Base class for CRUD operations with SQLModel.
    
    Provides common database operations that can be extended by specific repositories.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD operations for a model.
        
        Args:
            model: SQLModel class
        """
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        return db.get(self.model, id)
    
    def get_by_field(
        self,
        db: Session,
        field_name: str,
        value: Any,
        first: bool = True
    ) -> Optional[ModelType] | List[ModelType]:
        """
        Get record(s) by a field value.
        
        Args:
            db: Database session
            field_name: Name of the field to filter by
            value: Value to match
            first: If True, return first match; if False, return all matches
            
        Returns:
            Model instance(s) or None/empty list if not found
        """
        field = getattr(self.model, field_name)
        query = db.query(self.model).filter(field == value)
        
        if first:
            return query.first()
        return query.all()
    
    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and optional filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional dictionary of field: value filters
            
        Returns:
            List of model instances
        """
        query = db.query(self.model)
        
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    query = query.filter(field == value)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: ModelType | Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Model instance or dictionary of attributes
            
        Returns:
            Created model instance
        """
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = obj_in
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: ModelType | Dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.
        
        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Model instance or dictionary of attributes to update
            
        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Update timestamp if method exists
        if hasattr(db_obj, "update_timestamp"):
            db_obj.update_timestamp()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Delete a record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Deleted model instance or None if not found
        """
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            db: Database session
            filters: Optional dictionary of field: value filters
            
        Returns:
            Number of matching records
        """
        query = db.query(self.model)
        
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    query = query.filter(field == value)
        
        return query.count()
    
    def exists(self, db: Session, id: int) -> bool:
        """
        Check if a record exists by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            True if record exists, False otherwise
        """
        return db.get(self.model, id) is not None

