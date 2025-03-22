# I’m going to put most of my endpoints in a file called [general.py](http://general.py) in the folder endpoints -
# you can call it whatever you want, depending on what the routes in this file should focus on, if there is a focus.

# - We create a variable called router, you could call it something else
# - We add some tags and a prefix for all the URLs part of this router, e.g
# in this case below, all the endpoints will always start with /dashboard, e.g `/dashboard/company`

# här ligger våra endpoints/path operators

from app.security import get_current_user
from app.api.v1.core.models import Users, UserFileDisplays, Manuals, Brands, DeviceTypes
from app.api.v1.core.schemas import RegisterForm, LoginForm
from app.api.v1.core.services import check_for_partial_match, check_for_perfect_match, validate_content_in_image
from app.db_setup import get_db, get_s3_client
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status, Form, File, UploadFile
from sqlalchemy import func, delete, insert, select, update, or_
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.security import get_current_user, get_admin_or_partner_user
from app.settings import Settings
from typing import Annotated

from app.api.v1.core.models import Users, UserFileDisplays, Manuals
from app.db_setup import get_db
from app.security import get_current_user, get_admin_or_partner_user
from uuid import UUID


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
                Brands.name.label("brand"),  # Changed from brand_name to brand
                # Changed from device_type_name to device_type
                DeviceTypes.type.label("device_type"),
                Manuals.modelnumber,
                Manuals.modelname,
                Manuals.id,
            )
            .join(Manuals, UserFileDisplays.file_id == Manuals.id)
            .join(Brands, Manuals.brand_id == Brands.id)  # Join using brand_id
            # Join using device_type_id
            .join(DeviceTypes, Manuals.device_type_id == DeviceTypes.id)
            .where(
                UserFileDisplays.user_id == current_user.id,  # Filter for current user's manuals
                # Only show manuals not marked for removal
                UserFileDisplays.remove_from_view == False,
                Manuals.status != "deleted"  # Only show manuals that aren't deleted
            )
            .order_by(Brands.name, DeviceTypes.type)
        )

        user_manuals = db.execute(stmt).all()

        # Format the results
        result = []
        for manual in user_manuals:
            result.append({
                "users_own_naming": manual.users_own_naming,
                "brand": manual.brand,  # Keep field name as brand to match frontend expectations
                "device_type": manual.device_type,  # Keep field name as device_type
                "model_numbers": manual.modelnumber,
                "file_id": manual.id,
            })

        return {"manuals": result}

    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}"
        )


@router.post("/unmark_manual_deleted/{manual_id}", status_code=200)
def unmark_manual_deleted(
    manual_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restores a manual that was previously marked as deleted by setting its status back to 'active'.
    Only accessible by admin users."""

    # Check if user is an admin
    if not current_user.is_partner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required."
        )

    try:
        # Check if manual exists using SQLAlchemy 2.0 style
        stmt = select(Manuals).where(Manuals.id == manual_id)
        result = db.execute(stmt)
        manual = result.scalar_one_or_none()

        if not manual:
            raise HTTPException(status_code=404, detail="Manual not found")

        # Update manual status back to active
        update_stmt = (
            update(Manuals)
            .where(Manuals.id == manual_id)
            .values(status="active")
        )

        db.execute(update_stmt)
        db.commit()

        return {"status": "success", "message": "Manual restored successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error restoring manual: {str(e)}")


# OK partner function
@router.get("/list_user_uploaded_manuals", status_code=200)
def list_user_uploaded_manuals(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """An endpoint that returns all manuals uploaded by the current user."""
    try:
        # Query to get all manuals uploaded by the current user
        stmt = (
            select(
                Manuals.id,
                Brands.name.label("brand_name"),
                DeviceTypes.type.label("device_type_name"),
                Manuals.modelnumber,
                Manuals.modelname,
                Manuals.status
            )
            .where(
                Manuals.user_id == current_user.id,
                Manuals.status != "deleted"
            )

            .join(Brands, Manuals.brand_id == Brands.id)  # Join using brand_id
            # Join using device_type_id
            .join(DeviceTypes, Manuals.device_type_id == DeviceTypes.id)
            .where(Manuals.status != "deleted")
            # Add this line to filter by current user
            .where(Manuals.user_id == current_user.id)
            .order_by(Brands.name, DeviceTypes.type)
        )

        result = db.execute(stmt).all()

        # Format the results
        manuals_list = []
        for manual in result:
            manuals_list.append({
                "id": manual.id,
                "brand": manual.brand_name,  # Rename this field
                "device_type": manual.device_type_name,
                "modelnumber": manual.modelnumber,
                "modelname": manual.modelname,
                "status": manual.status
            })

        return {"manuals": manuals_list}

    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")


@router.post("/list_all_manuals", status_code=200)  # ta bort?? for partners
def list_all_manuals(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """An endpoint that returns all manuals with a count of how many users have tagged each manual.
    Only accessible by admin or partner users."""

    # Check if user is an admin or partner
    if not (current_user.is_admin or current_user.is_partner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin or partner access required."
        )

    try:
        # Get all manuals with user count using a subquery
        subquery = (
            select(
                UserFileDisplays.file_id,
                func.count(UserFileDisplays.user_id).label("user_count")
            )
            .where(UserFileDisplays.remove_from_view == False)
            .group_by(UserFileDisplays.file_id)
            .subquery()
        )

        # Main query to join with the subquery
        stmt = (
            select(
                Manuals.id,
                Brands.name.label("brand_name"),
                DeviceTypes.type.label("device_type_name"),
                Manuals.modelnumber,
                Manuals.modelname,
                Manuals.status,
                func.coalesce(subquery.c.user_count, 0).label("user_count")
            )
            .join(Brands, Manuals.brand_id == Brands.id)  # Join using brand_id
            # Join using device_type_id
            .join(DeviceTypes, Manuals.device_type_id == DeviceTypes.id)
            .outerjoin(subquery, Manuals.id == subquery.c.file_id)
            .where(Manuals.status != "deleted")
            # Add this line to filter by current user
            .where(Manuals.user_id == current_user.id)
            .order_by(Brands.name, DeviceTypes.type)
        )

        result = db.execute(stmt).all()

        # Format the results
        manuals_list = []
        for manual in result:
            manuals_list.append({
                "id": manual.id,
                "brand": manual.brand_name,  # Rename this field
                "device_type": manual.device_type_name,  # Rename this field
                "modelnumber": manual.modelnumber,
                "modelname": manual.modelname,
                "status": manual.status,
                "user_count": manual.user_count
            })

        return {"manuals": manuals_list}

    except SQLAlchemyError as e:
        print(f"PostgreSQL error {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")


@router.post("/mark_manual_deleted/{manual_id}", status_code=200)
def mark_manual_deleted(
    manual_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks a manual as deleted by setting its status to 'deleted'.
    Only accessible by admin users."""

    # Check if user is an admin
    if not current_user.is_partner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required."
        )

    try:
        # Check if manual exists using SQLAlchemy 2.0 style
        stmt = select(Manuals).where(Manuals.id == manual_id)
        result = db.execute(stmt)
        manual = result.scalar_one_or_none()

        if not manual:
            raise HTTPException(status_code=404, detail="Manual not found")

        # Update manual status to deleted
        update_stmt = (
            update(Manuals)
            .where(Manuals.id == manual_id)
            .values(status="deleted")
        )

        db.execute(update_stmt)
        db.commit()

        return {"status": "success", "message": "Manual marked as deleted"}

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating manual: {str(e)}")


@router.get("/dashboard/statistics", status_code=200)
def get_dashboard_statistics(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """An endpoint that returns statistics for the partner dashboard:
    1. Number of users who have selected manuals uploaded by the current user
    2. Total number of manuals uploaded by the current user
    3. Total number of selections of the current user's manuals
    4. List of most popular manuals uploaded by the user (by selection count)
    """
    try:
        # Get all manuals uploaded by the current user
        stmt = (
            select(Manuals.id)
            .where(
                Manuals.user_id == current_user.id,
                Manuals.status != "deleted"
            )
        )
        user_manual_ids_result = db.execute(stmt)
        user_manual_ids = [row[0] for row in user_manual_ids_result.fetchall()]

        # If the user has no manuals, return empty stats
        if not user_manual_ids:
            return {
                "users_selected_count": 0,
                "manuals_uploaded_count": 0,
                "total_selections_count": 0,
                "most_popular_manuals": []
            }

        # Count total manuals uploaded by the user
        manuals_uploaded_count = len(user_manual_ids)

        # Count distinct users who have selected these manuals
        distinct_users_query = (
            select(func.count(func.distinct(UserFileDisplays.user_id)))
            .where(
                UserFileDisplays.file_id.in_(user_manual_ids),
                UserFileDisplays.remove_from_view == False
            )
        )
        users_selected_count_result = db.execute(distinct_users_query)
        users_selected_count = users_selected_count_result.scalar() or 0

        # Count total selections (not distinct users)
        total_selections_query = (
            select(func.count())
            .where(
                UserFileDisplays.file_id.in_(user_manual_ids),
                UserFileDisplays.remove_from_view == False
            )
        )
        total_selections_result = db.execute(total_selections_query)
        total_selections_count = total_selections_result.scalar() or 0

        # Get the top 5 most popular manuals (by selection count)
        popular_manuals_query = (
            select(
                Manuals.id,
                Brands.name.label("brand"),  # Get brand name from Brands table
                Manuals.modelnumber,
                Manuals.modelname,
                # Get device type from DeviceTypes table
                DeviceTypes.type.label("device_type"),
                func.count(UserFileDisplays.id).label("selection_count")
            )
            .join(
                UserFileDisplays,
                UserFileDisplays.file_id == Manuals.id
            )
            .join(
                Brands,
                Manuals.brand_id == Brands.id  # Join with Brands table
            )
            .join(
                DeviceTypes,
                Manuals.device_type_id == DeviceTypes.id  # Join with DeviceTypes table
            )
            .where(
                Manuals.user_id == current_user.id,
                Manuals.status != "deleted",
                UserFileDisplays.remove_from_view == False
            )
            .group_by(Manuals.id, Brands.name, DeviceTypes.type)
            .order_by(func.count(UserFileDisplays.id).desc())
            .limit(5)
        )

        popular_manuals_result = db.execute(popular_manuals_query)

        popular_manuals = []
        for row in popular_manuals_result.fetchall():
            popular_manuals.append({
                "id": row.id,
                "brand": row.brand,
                "modelnumber": row.modelnumber,
                "modelname": row.modelname,
                "device_type": row.device_type,
                "selection_count": row.selection_count
            })

        return {
            "users_selected_count": users_selected_count,
            "manuals_uploaded_count": manuals_uploaded_count,
            "total_selections_count": total_selections_count,
            "most_popular_manuals": popular_manuals
        }

    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}"
        )


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
    brand_id: str,
    device_type_id: str,
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
        result = check_for_perfect_match(
            search_words, device_type_id, brand_id, db)
        if not result:
            result = check_for_partial_match(
                search_words, device_type_id, brand_id, db)
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
    brand_id: str = Form(...),
    device_type_id: str = Form(...),
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
        result = check_for_perfect_match(
            search_words, device_type_id, brand_id, db)
        if not result:
            result = check_for_partial_match(
                search_words, device_type_id, brand_id, db)
            if not result:
                raise HTTPException(
                    status_code=404, detail="No manuals found")

        return {"manuals": result}  # Consistent return structure

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list_all_brands")
def list_all_brands(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """An endpoint that returns all brands listed in the brands table"""
    try:
        # Query to get all manuals uploaded by the current user
        stmt = (
            select(Brands)
        )

        result = db.execute(stmt).scalars().all()

        # Format the results
        brands_list = []
        if not result:
            return {"brands": []}
        else:

            for brand in result:
                brands_list.append({
                    "id": brand.id,
                    "name": brand.name,
                })

            return {"brands": brands_list}

    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")


@router.get("/list_all_device_types")
def list_all_device_types(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """An endpoint that returns all brands listed in the brands table"""
    try:
        # Query to get all manuals uploaded by the current user
        stmt = (
            select(DeviceTypes)
        )

        result = db.execute(stmt).scalars().all()

        # Format the results
        device_list = []
        if not result:
            return {"device_types": []}
        else:

            for device in result:
                device_list.append({
                    "id": device.id,
                    "type": device.type,
                })

            return {"device_types": device_list}

    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")
