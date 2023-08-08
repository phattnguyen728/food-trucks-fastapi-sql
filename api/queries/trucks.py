import os
from psycopg_pool import ConnectionPool
from typing import List, Literal
from pydantic import BaseModel
from queries.users import UserOut

pool = ConnectionPool(conninfo=os.environ["DATABASE_URL"])

Cuisines = Literal[
        "American",
        "Asian",
        "French",
        "Mediterranean",
        "Indian",
        "Italian",
        "Latin",
    ]

class TruckIn(BaseModel):
    name: str
    website: str
    category: Cuisines
    vegetarian_friendly: bool
    owner_id: int

class TruckOut(BaseModel):
    id: int
    name: str
    website: str
    category: Cuisines
    vegetarian_friendly: bool
    owner: UserOut

class TruckWithPriceOut(TruckOut):
    average_price: float | None

class TruckListOut(BaseModel):
    trucks: list[TruckWithPriceOut]

class TruckQueries:
    def get_trucks(self) -> List[TruckWithPriceOut]:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.id AS user_id, u.first, u.last,
                        u.avatar, u.email, u.username,
                        t.id AS truck_id, t.name,
                        t.website, t.category,
                        t.vegetarian_friendly,

                    AVG(tmi.price) as average_price

                    FROM users u
                    JOIN trucks t ON(u.id = t.owner_id)
                    LEFT OUTER JOIN truck_menu_items tmi ON (t.id = tmi.truck_id)

                    GROUP BY
                        u.id, u.first, u.last,
                        u.avatar, u.email, u.username,
                        t.id, t.name, t.website, t.category,
                        t.vegetarian_friendly

                    ORDER BY t.name
                        """,
                )

                trucks = []
                rows = cur.fetchall()
                for row in rows:
                    truck = self.truck_record_to_dict(row, cur.description)
                    trucks.append(truck)
                return trucks

    def get_truck(self, truck_id) -> TruckOut | None:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.id AS user_id, u.first, u.last,
                        u.avatar, u.email, u.username,
                        t.id AS truck_id, t.name,
                        t.website, t.category,
                        t.vegetarian_friendly
                    FROM users u
                    JOIN trucks t ON(u.id = t.owner_id)
                    WHERE t.id = %s
                    """,
                    [truck_id],
                )

                row = cur.fetchone()
                return self.truck_record_to_dict(row, cur.description)

    def delete_truck(self, truck_id) -> None:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM trucks
                    WHERE id = %s
                    """,
                    [truck_id],
                )

    def create_truck(self, truck) -> TruckOut | None:
        id = None
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO trucks (
                        name, website, category, vegetarian_friendly, owner_id
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    [
                        truck.name,
                        truck.website,
                        truck.category,
                        truck.vegetarian_friendly,
                        truck.owner_id,
                    ],
                )

                row = cur.fetchone()
                id = row[0]
        if id is not None:
            return self.get_truck(id)

    def truck_record_to_dict(self, row, description) -> TruckOut | None:
        truck = None
        if row is not None:
            truck = {}
            truck_fields = [
                "truck_id",
                "name",
                "website",
                "category",
                "vegetarian_friendly",
                "average_price",
            ]
            for i, column in enumerate(description):
                if column.name in truck_fields:
                    truck[column.name] = row[i]
            truck["id"] = truck["truck_id"]
            owner = {}
            owner_fields = [
                "user_id",
                "first",
                "last",
                "avatar",
                "email",
                "username",
            ]
            for i, column in enumerate(description):
                if column.name in owner_fields:
                    owner[column.name] = row[i]
            owner["id"] = owner["user_id"]

            truck["owner"] = owner

            if "average_price" in truck:
                return TruckWithPriceOut(**truck)
            else:
                return TruckOut(**truck)
