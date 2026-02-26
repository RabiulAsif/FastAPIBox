from fastapi import FastAPI, HTTPException, Query
from fastapi import FastAPI, HTTPException, Query, Path
from service.products import get_all_products
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"}

# #Dynamic routing
# @app.get("/products")
# def get_products():
#     return get_all_products()

@app.get("/products")
def list_products(
    name: str = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search by name (Case insensitive)"
    ),
    sorted_by_price: bool = Query(default=False, description="Sorted by price"),
    order: str = Query(
        default="asc", description="Sort when sorted_by_price=true (asc,desc)"
    )
):
    products = get_all_products()

    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]

    if not products:
        raise HTTPException(
            status_code=404, detail=f"No product found matching name={name}"

        )
    
    if sorted_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)

    return {"total": len(products), "items": products}
    
@app.get("/products/{product_id}")
def get_product_id(
    product_id: str = Path(
    ..., min_length=36, 
    max_length=36, 
    description= "ID of the products",
    example="0005a4ea-ce3f-4dd7-bee0-f4ccc70fea6a"
    )
):
    products=get_all_products()
    for product in products:
        if product["id"]== product_id:
            return product
        raise HTTPException(status_code=404, detail="Page not found!")    