# I’m going to put most of my endpoints in a file called [general.py](http://general.py) in the folder endpoints -
# you can call it whatever you want, depending on what the routes in this file should focus on, if there is a focus.

# - We create a variable called router, you could call it something else
# - We add some tags and a prefix for all the URLs part of this router, e.g
# in this case below, all the endpoints will always start with /dashboard, e.g `/dashboard/company`

# här ligger våra endpoints/path operators

from app.api.v1.core.models import Users, UserFileDisplays, Manuals
from app.api.v1.core.schemas import RegisterForm, LoginForm
from app.api.v1.core.services import check_for_partial_match, check_for_perfect_match, validate_content_in_image
from app.db_setup import get_db, get_s3_client
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status, Form, File, UploadFile
from sqlalchemy import delete, insert, select, update, or_
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.security import get_current_user
from app.settings import Settings


router = APIRouter(tags=["gen"], prefix="/gen")


@router.post("/list_user_manuals", status_code=201)
def list_user_manuals(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """An endpoint that takes the user token and returns records of all manuals that that user has choosen to display.
    each manual - brand, type of machine model number, user comment(from junction table) and file url as arrays in a Json"""

    # Query the user's file displays that aren't marked for removal - SQLAlchemy 2.0 style
    try:
        stmt = (
            select(
                UserFileDisplays.users_own_naming,
                Manuals.brand,
                Manuals.device_type,
                Manuals.modelnumber,
                Manuals.modelname,
                Manuals.id,
            )
            .join(Manuals, UserFileDisplays.file_id == Manuals.id)
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
                "users_own_naming": manual.users_own_naming,
                "brand": manual.brand,
                "device_type": manual.device_type,
                "model_numbers": manual.modelnumber,
                "file_id": manual.id,
            })
        return {"manuals": result}
        # Handle the case where no manuals are found/registered on the user
        # ingen hantering av nollresulat
        # if not result:
        #     raise HTTPException(
        #         status_code=404, detail="No manuals choosen")
        # else:
        #     return {"manuals": result}

    except SQLAlchemyError as e:
        print(f"PostgreSQL error {e.pgcode} - {e}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")


#
#
@router.get("/get-download-url/{file_id}")
async def get_download_url(
    file_id: int,
    db: Session = Depends(get_db),
    s3_client=Depends(get_s3_client),
    current_user=Depends(get_current_user)
):
    """file_id läggs till urlen i endpointen, returnar en download url"""
    # Get file record from database
    file_upload = db.query(Manuals).filter(
        Manuals.id == file_id,
        Manuals.user_id == current_user.id
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


@router.post("/search/words_only")
async def search_for_manual(
    brand: str,
    device_type: str,
    modelnumber: str = "",  # Optional parameter with default value
    modelname: str = "",    # Optional parameter with default value
    db: Session = Depends(get_db),
):
    try:
        # Only add non-empty search words
        search_words = []
        if modelnumber and modelnumber.strip():
            search_words.append(modelnumber)
        if modelname and modelname.strip():
            search_words.append(modelname)

        if not search_words:
            raise HTTPException(
                status_code=400,
                detail="At least one of 'modelnumber' or 'modelname' must be provided"
            )
        result = check_for_perfect_match(search_words, device_type, brand, db)
        if not result:
            result = check_for_partial_match(
                search_words, device_type, brand, db)
            if not result:
                print("no semi match")
                raise HTTPException(
                    status_code=404, detail="No manuals found")

        return {"manuals": result}  # Consistent return structure

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/with_image")
async def search_for_manual(
    image: UploadFile = File(...),
    brand: str = Form(...),
    device_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """Searches with an uploaded image in the table Manuals by 
        input: image, modelnumber, modelname, brand, device_type, 
        returns: a list of dictionaries containing entries from the Manuals table 
        brand: match.brand,
        device_type: match.device_type,
        model_numbers: match.modelnumber,
        modelname: match.modelname,
        file_id: match.id,
        match: "perfect match,
        (the image is currently not stored in the S3, its passed directly to the functions)
        """
    image_temp = await image.read()
    search_words = validate_content_in_image(image_temp)

    try:
        result = check_for_perfect_match(search_words, device_type, brand, db)
        if not result:
            result = check_for_partial_match(
                search_words, device_type, brand, db)
            if not result:
                raise HTTPException(
                    status_code=404, detail="No manuals found")

        return {"manuals": result}  # Consistent return structure

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
