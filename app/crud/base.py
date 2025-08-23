# app/crud/base.py
from pynamodb.models import Model
from pynamodb.exceptions import DoesNotExist, PutError, UpdateError, DeleteError
from fastapi import HTTPException, status
import logging
from typing import Type, TypeVar, Generic, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TypeVar for PynamoDB Model
ModelType = TypeVar("ModelType", bound=Model)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, hash_key: Any, range_key: Any = None) -> Optional[ModelType]:
        """Fetch an item by its primary key."""
        try:
            # Check if the model has a range key
            if range_key:
                return self.model.get(hash_key, range_key=range_key)
            else:
                return self.model.get(hash_key)

        except DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching {self.model.Meta.table_name} with key ({hash_key}, {range_key}): {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    def get_multi(self, *args, **kwargs) -> List[ModelType]:
        """
        Fetch multiple items. This method should be implemented in subclasses
        with specific query logic (e.g., using a GSI or a more efficient scan).
        """
        raise NotImplementedError("This method should be overridden in subclasses with efficient query logic.")


    def create(self, obj_in_data: dict) -> ModelType:
        """Create a new item."""
        try:
            db_obj = self.model(**obj_in_data)
            db_obj.save()
            return db_obj
        except PutError as e:
            logger.error(f"Error creating item in {self.model.Meta.table_name}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create item")
        except Exception as e:
            logger.error(f"Unexpected error creating item in {self.model.Meta.table_name}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create item")

    def update(self, db_obj: ModelType, obj_in_data: dict) -> ModelType:
        """Update an existing item."""
        try:
            for key, value in obj_in_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db_obj.save()  # save() handles both create and update
            return db_obj
        except UpdateError as e:
            hash_key_val = getattr(db_obj, db_obj._hash_key_attribute().attr_name, "unknown")
            logger.error(f"Error updating item in {self.model.Meta.table_name} with key {hash_key_val}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update item")
        except Exception as e:
            logger.error(f"Unexpected error updating item in {self.model.Meta.table_name}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update item")

    def remove(self, db_obj: ModelType) -> ModelType:
        """Delete an item."""
        try:
            hash_key_val = getattr(db_obj, db_obj._hash_key_attribute().attr_name, "unknown")
            db_obj.delete()
            logger.info(f"Successfully deleted item from {self.model.Meta.table_name} with key {hash_key_val}")
            return db_obj
        except DeleteError as e:
            hash_key_val = getattr(db_obj, db_obj._hash_key_attribute().attr_name, "unknown")
            logger.error(f"Error deleting item from {self.model.Meta.table_name} with key {hash_key_val}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete item")
        except Exception as e:
            logger.error(f"Unexpected error deleting item in {self.model.Meta.table_name}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete item")
