# I’m going to put most of my endpoints in a file called [general.py](http://general.py) in the folder endpoints -
# you can call it whatever you want, depending on what the routes in this file should focus on, if there is a focus.

# - We create a variable called router, you could call it something else
# - We add some tags and a prefix for all the URLs part of this router, e.g
# in this case below, all the endpoints will always start with /dashboard, e.g `/dashboard/company`

# här ligger våra endpoints/path operators

from app.api.v1.core.models import Company, Users
from app.api.v1.core.schemas import CompanySchema, RegisterForm, LoginForm
from app.db_setup import get_db
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

router = APIRouter(tags=["dashboard"], prefix="/dashboard")


@router.get("/company", status_code=200)
def list_companies(db: Session = Depends(get_db)):
    programs = db.scalars(select(Company)).all()
    if not programs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No companies found"
        )
    return programs


@router.post("/company", status_code=201)
def add_company(company: CompanySchema, db: Session = Depends(get_db)):
    """
    Create a company, using a pydantic model for validation
    """
    try:
        db_company = Company(**company.model_dump())
        db.add(db_company)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Database")
    return db_company


@router.get("/company/{id}")
def company_detail(id: int, db: Session = Depends(get_db)):
    """
    Detail endpoint for company, all fields
    """
    result = db.scalars(
        select(Company)
        .where(Company.id == id)
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Company not found")
    return result


@router.delete("/company/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """
    Deletes a company based on an id
    """
    db_company = db.scalars(select(Company).where(
        Company.id == company_id)).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(db_company)
    db.commit()
    return {}


@router.post("/register", status_code=201)
def add_user(user: RegisterForm, db: Session = Depends(get_db)):
    """Adds a user, using pydantic model for validation"""
    try:
        db_user = Users(**user.model_dump())
        db.add(db_user)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Database")
    return db_user


@router.post("/validate_user", status_code=201)
def validate(login_form: LoginForm, db: Session = Depends(get_db)):
    """Checks if a user exists and returns id and first name, using pydantic model for validation"""
    try:
        result = db.scalars(
            select(Users)
            .where(Users.email == login_form.email)
        ).first()

        # Handle the case where no user is found
        if not result:
            raise HTTPException(
                status_code=404, detail="User not found")

        # Check password
        if login_form.password == result.password:
            return {"id": result.id, "first_name": result.first_name}
        else:
            raise HTTPException(
                status_code=401, detail="Password or email is not correct")

    except SQLAlchemyError as e:
        print(f"PostgreSQL error {e.pgcode} - {e}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")
