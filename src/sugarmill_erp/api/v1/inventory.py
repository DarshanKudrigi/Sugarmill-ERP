import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from sugarmill_erp.core.database import get_db
from sugarmill_erp.crud.inventory import inventory_crud
from sugarmill_erp.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)

router = APIRouter(prefix="/inventory", tags=["Inventory Items"])


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_in: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemResponse:
    existing = await inventory_crud.get_by_code(db, code=item_in.item_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Inventory item with code '{item_in.item_code}' already exists.",
        )
    item = await inventory_crud.create(db, obj_in=item_in)
    return item


@router.get("/", response_model=list[InventoryItemResponse])
async def get_all_inventory_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max number of records to return"),
    db: AsyncSession = Depends(get_db),
) -> list[InventoryItemResponse]:
    items = await inventory_crud.get_multi(db, skip=skip, limit=limit)
    return items


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item_by_id(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemResponse:
    item = await inventory_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID '{item_id}' not found.",
        )
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: uuid.UUID,
    item_in: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemResponse:
    item = await inventory_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID '{item_id}' not found.",
        )
    if item_in.item_code and item_in.item_code != item.item_code:
        existing = await inventory_crud.get_by_code(db, code=item_in.item_code)
        if existing and existing.id != item_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Inventory item with code '{item_in.item_code}' already exists.",
            )
    updated_item = await inventory_crud.update(db, db_obj=item, obj_in=item_in)
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    item = await inventory_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID '{item_id}' not found.",
        )
    await inventory_crud.remove(db, id=item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

