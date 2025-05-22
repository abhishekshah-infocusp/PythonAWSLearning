import datetime
import random
import time
from typing import Annotated, Literal
from uuid import UUID
from fastapi import FastAPI, Query, Path, Body
from enum import Enum
from pydantic import AfterValidator, BaseModel, Field

class ModelName(str, Enum):
    model1 = "Model1"
    model2 = "Model2"
    model3 = "Model3"


class Item(BaseModel):
    name: str
    description: str | None = None  # Optional
    price: float
    tax: float | None = None  # Optional


app = FastAPI()

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

@app.get("/")
def root():
    print("Hello World in console")
    return "Hello World"


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, needy: str, skip: int = 0, limit: int | None = None):
#     return {"item_id": item_id, "needy":needy, "skip":skip, "limit":limit}


@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name is ModelName.model1:
        return {"model_name": model_name, "message": "This is Model 1"}

    if model_name.value == "Model2":
        return {
            "model_name": model_name,
            "message": "This is model 2 using comparision",
        }

    return {"model_name": model_name, "message": "This is from last rerurn stmt"}


@app.post("/items/{item_id}")
async def create_item(item: Item, item_id: int = 52):
    item_dict = item.dict()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return {"item_id": item_id, "item dict": item_dict}


@app.get("/items/query_with_anno")
async def read_items(q: Annotated[str | None, Query(max_length=5)] = None):
    return q


@app.get("/items/query_without_anno")
async def read_items1(q: str | None = Query(default="abhi", max_length=5)):
    return q


@app.get("/items/query1")
async def read_items2(q: Annotated[str, Query()] = "default_vall"):
    return q


@app.get("/items/query2")
async def read_items3(q: str = "default_val"):
    return q


@app.get("/items/query_multiplevals")
async def read_items4(q: Annotated[list[str] | None, Query(title="this is query title", alias="item-query", description="query description")] = None):
    return q


def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format')
    return id

@app.get("/items/query_custom_validator")
async def read_items6 (
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}


@app.get("/items/path/{item_id}")
async def read_items7(
    item_id: Annotated[int | None, Path(title="The ID of the item to get", gt = 5)],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

@app.get("/items/classFilterParams/")
async def read_items10(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/items/multiple_body/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[str|None, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

@app.put("/items/embed/{item_id}")
async def update_item12(
    item_id : int,
    item: Annotated[Item, Body(embed = True)]
):
    return {"item_id": item_id, "item": item}


class Item2(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="Description of Item", max_length=200
    )
    price: float = Field(gt=0, le=1000, description="price must be greater than zero")
    tax: float | None = None

@app.put("/items/field/{item_id}")
async def fun(
    item_id : int,
    item: Annotated[Item2, Body(embed=True)]
):
    return {"item_id": item_id, "item": item}
    
@app.put("/items/uniquedatatypes/{item_id}")
async def read_items545(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[datetime.timedelta, Body()],
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }

