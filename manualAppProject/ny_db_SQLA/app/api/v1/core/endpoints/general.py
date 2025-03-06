# I’m going to put most of my endpoints in a file called [general.py](http://general.py) in the folder endpoints -
# you can call it whatever you want, depending on what the routes in this file should focus on, if there is a focus.

# - We create a variable called router, you could call it something else
# - We add some tags and a prefix for all the URLs part of this router, e.g
# in this case below, all the endpoints will always start with /dashboard, e.g `/dashboard/company`

# här ligger våra endpoints/path operators

from app.api.v1.core.models import Users, UserFileDisplays, FileUpload
from app.api.v1.core.schemas import RegisterForm, LoginForm
from app.db_setup import get_db, get_s3_client
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.security import get_current_user
from app.settings import Settings

router = APIRouter(tags=["dashboard"], prefix="/dashboard")


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


@router.post("/list_user_manuals", status_code=201)
def list_user_manuals(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """An endpoint that takes the user token and returns records of all manuals that that user has choosen to display.
    each manual - brand, type of machine model number, user comment(from junction table) and file url as arrays in a Json"""

    # Query the user's file displays that aren't marked for removal - SQLAlchemy 2.0 style
    try:
        stmt = (
            select(
                UserFileDisplays.users_own_naming,
                FileUpload.brand,
                FileUpload.device_type,
                FileUpload.modelnumber_1,
                FileUpload.modelnumber_2,
                FileUpload.id,
            )
            .join(FileUpload, UserFileDisplays.file_id == FileUpload.id)
            .where(
                UserFileDisplays.user_id == current_user.id,
                UserFileDisplays.remove_from_view == False
            )
        )

        user_manuals = db.execute(stmt).all()

        # Format the results
        result = []
        for manual in user_manuals:
            result.append({
                "user_comment": manual.users_own_naming,
                "brand": manual.brand,
                "device_type": manual.device_type,
                "model_numbers": [manual.modelnumber_1, manual.modelnumber_2],
                "file_id": manual.id,
            })

        # Handle the case where no manuals are found/registered on the user
        if not result:
            raise HTTPException(
                status_code=404, detail="No manuals choosen")
        else:
            return {"manuals": result}

    except SQLAlchemyError as e:
        print(f"PostgreSQL error {e.pgcode} - {e}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")


# behöver kollas igenom
@router.get("/get-download-url/{file_id}")
async def get_download_url(
    file_id: int,
    db: Session = Depends(get_db),
    s3_client=Depends(get_s3_client),
    current_user=Depends(get_current_user)
):
    # Get file record from database
    file_upload = db.query(FileUpload).filter(
        FileUpload.id == file_id,
        FileUpload.user_id == current_user.id
    ).first()

    if not file_upload:
        raise HTTPException(status_code=404, detail="File not found")

    # Generate a presigned GET URL
    try:
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': Settings.S3_BUCKET,
                'Key': file_upload.s3_key
            },
            ExpiresIn=3600  # 1 hour expiration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"downloadUrl": download_url}
