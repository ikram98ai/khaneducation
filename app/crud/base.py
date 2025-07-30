# app/crud/base_pynamodb.py (or replace app/crud/base.py)
# from sqlalchemy.orm import Session # Remove
# from sqlalchemy.exc import SQLAlchemyError # Remove
from fastapi import HTTPException, status
import logging
# from .. import schemas # Keep if needed for type hints
# from typing import Type, TypeVar, Generic, List, Optional # Keep, adjust if needed
# from ..database import Base # Remove SQLAlchemy Base

# --- PynamoDB Imports ---
from pynamodb.models import Model
from pynamodb.exceptions import DoesNotExist, PutError, UpdateError, DeleteError
from typing import Type, TypeVar, Generic, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TypeVar for PynamoDB Model
ModelType = TypeVar("ModelType", bound=Model) # Bound to PynamoDB Model
# Keep schema TypeVars if needed
# CreateSchemaType = TypeVar("CreateSchemaType", bound=schemas.BaseModel)
# UpdateSchemaType = TypeVar("UpdateSchemaType", bound=schemas.BaseModel)

# --- Simplified CRUDBase for PynamoDB ---
# Note: PynamoDB handles saving/updating/deleting model instances directly.
# This base class becomes less necessary, but can provide common error handling/logging.
class CRUDBase(Generic[ModelType]): # Simplify generic signature
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, hash_key: Any, range_key: Any = None) -> Optional[ModelType]:
        """Fetch an item by its primary key."""
        try:
            if range_key is not None:
                return self.model.get(hash_key, range_key)
            else:
                return self.model.get(hash_key)
        except DoesNotExist:
            return None
        except Exception as e: # Catch other PynamoDB errors
            logger.error(f"Error fetching {self.model.Meta.table_name} with key ({hash_key}, {range_key}): {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    def get_multi(self, *args, **kwargs) -> List[ModelType]: # Pass through query args
        """Fetch multiple items. Pass query arguments directly to model.query or model.scan."""
        # Example: list(self.model.scan()) or list(self.model.query(hash_key, filter_condition=...))
        # This is highly dependent on your access patterns and model design.
        # Base class can't implement this generically well for PynamoDB.
        # It's often better to implement specific query methods in subclasses.
        raise NotImplementedError("Use specific query methods on the model or implement in subclass.")

    def create(self, obj_in_data: dict) -> ModelType: # Accept dict data
        """Create a new item."""
        try:
            db_obj = self.model(**obj_in_data)
            db_obj.save()
            return db_obj
        except PutError as e: # Specific PynamoDB error
            logger.error(f"Error creating {self.model.Meta.table_name}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create item")
        except Exception as e:
             logger.error(f"Unexpected error creating {self.model.Meta.table_name}: {e}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create item")

    def update(self, db_obj: ModelType, obj_in_data: dict) -> ModelType: # Pass the model instance and update data
        """Update an existing item."""
        try:
            # Update attributes on the model instance
            for key, value in obj_in_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db_obj.save() # PynamoDB save handles update
            return db_obj
        except UpdateError as e: # Specific PynamoDB error
            logger.error(f"Error updating {self.model.Meta.table_name} with key {getattr(db_obj, db_obj.attribute_values.get(db_obj._hash_key_attribute().attr_name, 'unknown'))}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update item")
        except Exception as e:
             logger.error(f"Unexpected error updating {self.model.Meta.table_name}: {e}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update item")

    def remove(self, db_obj: ModelType) -> ModelType: # Pass the model instance to delete
        """Delete an item."""
        try:
            db_obj.delete()
            return db_obj
        except DeleteError as e: # Specific PynamoDB error
            logger.error(f"Error deleting {self.model.Meta.table_name} with key {getattr(db_obj, db_obj.attribute_values.get(db_obj._hash_key_attribute().attr_name, 'unknown'))}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete item")
        except Exception as e:
             logger.error(f"Unexpected error deleting {self.model.Meta.table_name}: {e}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete item")
