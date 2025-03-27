# I’m going to put most of my endpoints in a file called [general.py](http://general.py) in the folder endpoints -
# you can call it whatever you want, depending on what the routes in this file should focus on, if there is a focus.

# - We create a variable called router, you could call it something else
# - We add some tags and a prefix for all the URLs part of this router, e.g
# in this case below, all the endpoints will always start with /dashboard, e.g `/dashboard/company`

# här ligger våra endpoints/path operators

from app.security import get_current_user
from app.api.v1.core.models import Users, UserFileDisplays, Manuals, Brands, DeviceTypes
from app.api.v1.core.schemas import LoginForm, DeleteManualRequest, DeleteManualResponse
from app.api.v1.core.services import check_for_partial_match, check_for_perfect_match, validate_content_in_image
from app.api.v1.core.services_upload import get_manual_url_for_download

from app.db_setup import get_db, get_s3_client
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, Body
from sqlalchemy import func, delete, insert, select, update, distinct
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.security import get_current_user
from app.settings import settings

from app.api.v1.core.models import Users, UserFileDisplays, Manuals
from app.db_setup import get_db, get_s3_client
from app.security import get_current_user
from uuid import UUID
import boto3
from typing import Dict, Any

router = APIRouter(tags=["gen"], prefix="/gen")


@router.get("/dashboard/statistics", response_model=Dict[str, Any])
def get_dashboard_statistics(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for partner users.
    Returns counts of users who selected manuals, uploaded manuals, total selections,
    and most popular manuals.
    """
    # Check if user is a partner
    if not current_user.is_partner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only partner users can access this endpoint"
        )

    # Get manuals uploaded by the partner
    manuals_stmt = select(func.count()).select_from(Manuals).where(
        Manuals.user_id == current_user.id,
        Manuals.deleted == False,
        Manuals.status == "completed"
    )
    manuals_uploaded_count = db.scalar(manuals_stmt) or 0

    # Get the number of users who selected partner's manuals
    users_stmt = select(
        func.count(distinct(UserFileDisplays.user_id))
    ).join(
        Manuals, UserFileDisplays.file_id == Manuals.id
    ).where(
        Manuals.user_id == current_user.id,
        UserFileDisplays.remove_from_view == False
    )
    users_selected_count = db.scalar(users_stmt) or 0

    # Get total number of selections of partner's manuals
    selections_stmt = select(
        func.count(UserFileDisplays.id)
    ).join(
        Manuals, UserFileDisplays.file_id == Manuals.id
    ).where(
        Manuals.user_id == current_user.id,
        UserFileDisplays.remove_from_view == False
    )
    total_selections_count = db.scalar(selections_stmt) or 0

    # Get most popular manuals (by number of selections)
    popular_stmt = select(
        Manuals.id,
        Brands.name.label("brand"),
        Manuals.modelname,
        DeviceTypes.type.label("device_type"),
        func.count(UserFileDisplays.id).label("selection_count")
    ).join(
        UserFileDisplays, Manuals.id == UserFileDisplays.file_id
    ).join(
        Brands, Manuals.brand_id == Brands.id
    ).join(
        DeviceTypes, Manuals.device_type_id == DeviceTypes.id
    ).where(
        Manuals.user_id == current_user.id,
        UserFileDisplays.remove_from_view == False
    ).group_by(
        Manuals.id,
        Brands.name,
        Manuals.modelname,
        DeviceTypes.type
    ).order_by(
        func.count(UserFileDisplays.id).desc()
    ).limit(10)

    most_popular_manuals_result = db.execute(popular_stmt).all()

    most_popular_manuals = [
        {
            "id": str(manual.id),
            "brand": manual.brand,
            "modelname": manual.modelname,
            "device_type": manual.device_type,
            "selection_count": manual.selection_count
        }
        for manual in most_popular_manuals_result
    ]

    return {
        "users_selected_count": users_selected_count,
        "manuals_uploaded_count": manuals_uploaded_count,
        "total_selections_count": total_selections_count,
        "most_popular_manuals": most_popular_manuals
    }


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


@router.delete("/delete_user_manual_favourite")
def delete_user_manual(
    file_id: str,  # Query parameter
    hard_delete: bool = False,  # Optional query parameter with default value
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete a manual entry from the user's collection

    This endpoint will either mark the entry as removed from view
    or completely delete it from the database
    """
    # Ensure the user is authenticated
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # Check if the manual exists and belongs to the current user
    from sqlalchemy import select
    stmt = select(UserFileDisplays).where(
        UserFileDisplays.file_id == file_id,  # Use the query parameter
        UserFileDisplays.user_id == current_user.id
    )
    result = db.execute(stmt)
    user_manual = result.scalar_one_or_none()

    if not user_manual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manual not found or doesn't belong to current user"
        )

    if hard_delete:
        # Complete deletion from database
        db.delete(user_manual)
    else:
        # Soft deletion (mark as removed from view)
        user_manual.remove_from_view = True
        db.add(user_manual)

    db.commit()

    return {"success": True, "message": "Manual successfully removed"}


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


@router.get("/get_download_url/{file_id}")
def get_download_url(
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Returns a download URL for the specified file in the format {"downloadUrl": download_url} """
    try:
        # Make sure to pass all required parameters to the function
        url = get_manual_url_for_download(
            file_id=file_id,
            current_user=current_user,
            db=db
        )
        return url
    except Exception as e:
        # Log the error
        print(f"Error getting download URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get download URL: {str(e)}"
        )


@router.get("/list_all_brands")
def list_all_brands(db: Session = Depends(get_db)):
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
def list_all_device_types(db: Session = Depends(get_db)):
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


@router.post("/search/words_only")
def search_for_manual(
    brand_id: str,
    device_type_id: str,
    modelnumber: str = "",  # Optional parameter with default value
    modelname: str = "",    # Optional parameter with default value
    db: Session = Depends(get_db),
):
    """Takes in parameters brand_id, and device_type - from dropdowns in frontend. together with
    search queries for either model number or model name. 
    returns: a dictionary of a list of dictionaries - whith perfect or partial matches. The manual dictionary includes
    {
            "brand_id": manual.brand_id,
            "device_type_id": manual.device_type_id,
            "model_numbers": manual.modelnumber,
            "modelname": manual.modelname,
            "file_id": manual.id,
            "match": f"partial match ({similarity:.2f})",
        }
    """
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
def search_for_manual(
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
    image_temp = image.file.read()
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
