from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import database_models
from database import SessionLocal, engine
from models import Product as ProductSchema

# create tables
database_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- UI ROUTES ----------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(database_models.Product).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": products
    })


@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/create")
def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    product = database_models.Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity
    )
    db.add(product)
    db.commit()
    return RedirectResponse("/", status_code=302)


@app.get("/edit/{product_id}", response_class=HTMLResponse)
def edit_page(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    return templates.TemplateResponse("edit.html", {
        "request": request,
        "product": product
    })


@app.post("/update/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()

    product.name = name
    product.description = description
    product.price = price
    product.quantity = quantity

    db.commit()
    return RedirectResponse("/", status_code=302)


@app.get("/delete/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    db.delete(product)
    db.commit()
    return RedirectResponse("/", status_code=302)