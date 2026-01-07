"""
Material Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.connection import get_db
from app.database.models import Material, User
from app.core.dependencies import get_current_active_user
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse

router = APIRouter()

@router.get("", response_model=List[MaterialResponse])
async def list_materials(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    material_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    low_stock_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List materials"""
    query = db.query(Material).filter(
        Material.company_id == current_user.company_id,
        Material.deleted_at.is_(None)
    )
    
    if search:
        query = query.filter(
            or_(
                Material.material_name.ilike(f"%{search}%"),
                Material.material_code.ilike(f"%{search}%"),
                Material.description.ilike(f"%{search}%")
            )
        )
    
    if category:
        query = query.filter(Material.category == category)
    
    if material_type:
        query = query.filter(Material.material_type == material_type)
    
    if status_filter:
        query = query.filter(Material.status == status_filter)
    
    if low_stock_only:
        query = query.filter(Material.current_stock <= Material.reorder_point)
    
    materials = query.offset((page - 1) * limit).limit(limit).all()
    
    return [
        MaterialResponse(
            id=str(m.id),
            company_id=str(m.company_id),
            material_code=m.material_code,
            material_name=m.material_name,
            description=m.description,
            category=m.category,
            subcategory=m.subcategory,
            material_type=m.material_type,
            unit_of_measure=m.unit_of_measure,
            weight=m.weight,
            dimensions=m.dimensions,
            specifications=m.specifications,
            current_stock=m.current_stock,
            reorder_point=m.reorder_point,
            reorder_quantity=m.reorder_quantity,
            safety_stock=m.safety_stock,
            max_stock=m.max_stock,
            standard_cost=m.standard_cost,
            average_cost=m.average_cost,
            last_purchase_price=m.last_purchase_price,
            preferred_supplier_id=str(m.preferred_supplier_id) if m.preferred_supplier_id else None,
            status=m.status,
            is_active=m.is_active,
            abc_category=m.abc_category,
            turnover_rate=m.turnover_rate,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in materials
    ]

@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get material by ID"""
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.company_id == current_user.company_id,
        Material.deleted_at.is_(None)
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    return MaterialResponse(
        id=str(material.id),
        company_id=str(material.company_id),
        material_code=material.material_code,
        material_name=material.material_name,
        description=material.description,
        category=material.category,
        subcategory=material.subcategory,
        material_type=material.material_type,
        unit_of_measure=material.unit_of_measure,
        weight=material.weight,
        dimensions=material.dimensions,
        specifications=material.specifications,
        current_stock=material.current_stock,
        reorder_point=material.reorder_point,
        reorder_quantity=material.reorder_quantity,
        safety_stock=material.safety_stock,
        max_stock=material.max_stock,
        standard_cost=material.standard_cost,
        average_cost=material.average_cost,
        last_purchase_price=material.last_purchase_price,
        preferred_supplier_id=str(material.preferred_supplier_id) if material.preferred_supplier_id else None,
        status=material.status,
        is_active=material.is_active,
        abc_category=material.abc_category,
        turnover_rate=material.turnover_rate,
        created_at=material.created_at,
        updated_at=material.updated_at,
    )

@router.post("", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    material_data: MaterialCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new material"""
    # Check if material code already exists
    existing = db.query(Material).filter(
        Material.company_id == current_user.company_id,
        Material.material_code == material_data.material_code,
        Material.deleted_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Material code already exists")
    
    material_dict = material_data.model_dump()
    if material_dict.get("preferred_supplier_id"):
        material_dict["preferred_supplier_id"] = uuid.UUID(material_dict["preferred_supplier_id"])
    
    import uuid
    material = Material(
        company_id=current_user.company_id,
        **material_dict
    )
    
    db.add(material)
    db.commit()
    db.refresh(material)
    
    return MaterialResponse(
        id=str(material.id),
        company_id=str(material.company_id),
        **material_data.model_dump(),
        current_stock=0,
        average_cost=None,
        last_purchase_price=None,
        status="active",
        is_active=True,
        abc_category=None,
        turnover_rate=None,
        created_at=material.created_at,
        updated_at=material.updated_at,
    )

@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: str,
    material_data: MaterialUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update material"""
    import uuid
    
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.company_id == current_user.company_id,
        Material.deleted_at.is_(None)
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    update_data = material_data.model_dump(exclude_unset=True)
    if "preferred_supplier_id" in update_data and update_data["preferred_supplier_id"]:
        update_data["preferred_supplier_id"] = uuid.UUID(update_data["preferred_supplier_id"])
    
    for field, value in update_data.items():
        setattr(material, field, value)
    
    db.commit()
    db.refresh(material)
    
    return MaterialResponse(
        id=str(material.id),
        company_id=str(material.company_id),
        material_code=material.material_code,
        material_name=material.material_name,
        description=material.description,
        category=material.category,
        subcategory=material.subcategory,
        material_type=material.material_type,
        unit_of_measure=material.unit_of_measure,
        weight=material.weight,
        dimensions=material.dimensions,
        specifications=material.specifications,
        current_stock=material.current_stock,
        reorder_point=material.reorder_point,
        reorder_quantity=material.reorder_quantity,
        safety_stock=material.safety_stock,
        max_stock=material.max_stock,
        standard_cost=material.standard_cost,
        average_cost=material.average_cost,
        last_purchase_price=material.last_purchase_price,
        preferred_supplier_id=str(material.preferred_supplier_id) if material.preferred_supplier_id else None,
        status=material.status,
        is_active=material.is_active,
        abc_category=material.abc_category,
        turnover_rate=material.turnover_rate,
        created_at=material.created_at,
        updated_at=material.updated_at,
    )

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete material (soft delete)"""
    from datetime import datetime
    
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.company_id == current_user.company_id,
        Material.deleted_at.is_(None)
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material.deleted_at = datetime.utcnow()
    db.commit()
    
    return None

