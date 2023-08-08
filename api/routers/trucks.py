from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from queries.trucks import TruckQueries, TruckOut, TruckIn, TruckListOut
from psycopg.errors import ForeignKeyViolation

router = APIRouter()

@router.get("/api/trucks/{truck_id}", response_model=Optional[TruckOut])
def get_truck(
    truck_id: int,
    queries: TruckQueries = Depends(),
):
    record = queries.get_truck(truck_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No truck found with id {}".format(truck_id))
    else:
        return record

@router.delete("/api/trucks/{truck_id}", response_model=bool)
def delete_truck(
    truck_id: int, 
    queries: TruckQueries = Depends()
):
    queries.delete_truck(truck_id)
    return True

@router.get("/api/trucks", response_model=TruckListOut)
def get_trucks(
    queries: TruckQueries = Depends()
):
    # returning a JSON object is conventional -- preferred instead of returning 
    # a list due to historical # security reasons and flexibility
    return {"trucks": queries.get_trucks()}

@router.post("/api/trucks", response_model=TruckOut)
def create_truck(
    truck: TruckIn,    
    queries: TruckQueries = Depends(),
):
    try: 
        return queries.create_truck(truck)
    except ForeignKeyViolation as e:
        raise HTTPException(status_code=400, detail="Failed to create truck due to foreign key violation with owner")