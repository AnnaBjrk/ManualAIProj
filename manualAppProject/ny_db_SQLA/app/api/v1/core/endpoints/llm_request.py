
from app.api.v1.core.services_llm_connection import get_llm_answer, get_manual_upload_url
from app.api.v1.core.services_llm import DocPreProcessLLM
from app.security import get_current_user
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload
from app.db_setup import get_db, get_s3_client
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status, Form, File, UploadFile
from sqlalchemy import delete, insert, select, update, or_

router = APIRouter(tags=["llm"], prefix="/llm")


@router.post("/llm_request", status_code=201)
def get_llm_answer(user_question, file_id, Users=Depends(get_current_user), db: Session = Depends(get_db)):
    """An endpoint that takes a users question and a file_id for a manual and answers a question
    about that manual with the assistance of Mistral LLM"""
    pdf_url = get_manual_upload_url(file_id)
    get_llm_answer(retrieved_chunk, question)
    choosen_manual = DocPreProcessLLM(pdf_url)

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
