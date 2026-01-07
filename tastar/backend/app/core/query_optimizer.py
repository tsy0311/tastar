"""
Database Query Optimization Utilities
Provides utilities for optimizing database queries with eager loading, batching, and indexing hints
"""
from sqlalchemy.orm import joinedload, selectinload, subqueryload, Session
from sqlalchemy import select, func, Index
from typing import List, Optional, Type, Any
from app.core.logging import logger
from app.database.models import Base

def eager_load_relationships(query, relationships: List[str]):
    """
    Add eager loading for relationships to avoid N+1 queries
    
    Args:
        query: SQLAlchemy query object
        relationships: List of relationship names to eager load
    """
    for rel in relationships:
        try:
            query = query.options(joinedload(rel))
        except Exception as e:
            logger.warning(f"Could not eager load relationship {rel}: {e}")
    return query

def batch_query(
    db: Session,
    model: Type[Base],
    filters: dict,
    batch_size: int = 1000,
    order_by: Optional[str] = None
):
    """
    Query in batches to avoid loading too much data at once
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        filters: Dictionary of filters
        batch_size: Number of records per batch
        order_by: Column name to order by
    """
    query = db.query(model)
    
    # Apply filters
    for key, value in filters.items():
        if hasattr(model, key):
            query = query.filter(getattr(model, key) == value)
    
    # Apply ordering
    if order_by and hasattr(model, order_by):
        query = query.order_by(getattr(model, order_by))
    
    # Get total count
    total = query.count()
    
    # Yield batches
    offset = 0
    while offset < total:
        batch = query.offset(offset).limit(batch_size).all()
        yield batch
        offset += batch_size
        if len(batch) < batch_size:
            break

def optimize_list_query(
    query,
    page: int = 1,
    limit: int = 50,
    order_by: Optional[str] = None,
    eager_load: Optional[List[str]] = None
):
    """
    Optimize list queries with pagination, ordering, and eager loading
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        limit: Records per page
        order_by: Column name to order by
        eager_load: List of relationships to eager load
    """
    # Add eager loading
    if eager_load:
        query = eager_load_relationships(query, eager_load)
    
    # Add ordering
    if order_by:
        if order_by.startswith('-'):
            # Descending order
            col_name = order_by[1:]
            if hasattr(query.column_descriptions[0]['entity'], col_name):
                query = query.order_by(getattr(query.column_descriptions[0]['entity'], col_name).desc())
        else:
            # Ascending order
            if hasattr(query.column_descriptions[0]['entity'], order_by):
                query = query.order_by(getattr(query.column_descriptions[0]['entity'], order_by))
    
    # Add pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    return query

def get_query_stats(query) -> dict:
    """
    Get statistics about a query (useful for debugging)
    
    Args:
        query: SQLAlchemy query object
    """
    try:
        compiled = query.statement.compile(compile_kwargs={"literal_binds": True})
        return {
            'sql': str(compiled),
            'params': compiled.params
        }
    except Exception as e:
        logger.warning(f"Could not get query stats: {e}")
        return {'error': str(e)}

def create_index_if_not_exists(
    db: Session,
    table_name: str,
    columns: List[str],
    index_name: Optional[str] = None
):
    """
    Create database index if it doesn't exist
    
    Args:
        db: Database session
        table_name: Name of the table
        columns: List of column names
        index_name: Optional custom index name
    """
    if not index_name:
        index_name = f"idx_{table_name}_{'_'.join(columns)}"
    
    try:
        # Check if index exists
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        indexes = inspector.get_indexes(table_name)
        
        if any(idx['name'] == index_name for idx in indexes):
            logger.info(f"Index {index_name} already exists")
            return
        
        # Create index
        from sqlalchemy import text
        columns_str = ', '.join(columns)
        sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
        db.execute(text(sql))
        db.commit()
        logger.info(f"Created index {index_name} on {table_name}")
        
    except Exception as e:
        logger.warning(f"Could not create index {index_name}: {e}")
        db.rollback()


