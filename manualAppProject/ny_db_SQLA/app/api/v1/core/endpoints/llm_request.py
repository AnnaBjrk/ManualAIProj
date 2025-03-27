# For llm request endpoints - needs to be worked on - create logic for two different
# queries one for user question and table of content and one for user question and text
from pydantic import BaseModel
from typing import List, Dict, Any
from app.api.v1.core.models import UserFileDisplays, Manuals, DeviceTypes, Brands
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import delete, insert, select, update, or_
from fastapi import APIRouter, Depends, HTTPException
from app.db_setup import get_db
from sqlalchemy.orm import Session, session
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.core.services_llm_connection import get_llm_answer
from app.api.v1.core.services_llm import DocPreProcessLLM
from app.api.v1.core.models import Manuals, UserFileDisplays, DeviceTypes, Users
from app.security import get_current_user
from app.api.v1.core.services_upload import get_manual_url_for_download
from app.api.v1.core.schemas import UserFileResponse

router = APIRouter(tags=["llm"], prefix="/llm")


# @router.post("/llm_request_full_text", status_code=201)
# def process_llm_query(
#     user_question: str,
#     file_id: str,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     """LLM endpoint with validated params"""
#     try:
#         # Get the manual URL
#         url_response = get_manual_url_for_download(
#             file_id=file_id,
#             current_user=current_user,
#             db=db
#         )

#         url = url_response["downloadUrl"]  # Extract the URL from the response

#         # Get the device type
#         stmt = (
#             select(DeviceTypes.type)
#             .join(Manuals, Manuals.device_type_id == DeviceTypes.id)
#             .where(Manuals.id == file_id)
#         )

#         # Execute the query and fetch the result
#         result = db.execute(stmt)
#         device = result.scalar_one_or_none()

#         if not device:
#             raise HTTPException(
#                 status_code=404, detail="Device type not found")

#         # Process the manual - specify that we're using a remote URL
#         choosen_manual = DocPreProcessLLM(url, is_remote_url=True)

#         # Since we don't know the exact structure, let's build a function that can handle various cases
#         def extract_text_from_object(obj):
#             if isinstance(obj, str):
#                 return obj
#             elif isinstance(obj, dict):
#                 # Try to get text from known fields
#                 for key in ['text', 'content', 'heading', 'value']:
#                     if key in obj and isinstance(obj[key], str):
#                         return obj[key]
#                 # If no suitable fields found, just use the string representation
#                 return str(obj)
#             else:
#                 # For any other type, convert to string
#                 return str(obj)

#         # Extract text from each item in the list
#         extracted_texts = [extract_text_from_object(
#             item) for item in choosen_manual.markup_one_lang_text]

#         # Join the extracted texts
#         text_content = '\n'.join(extracted_texts)

#         # If that fails, fallback to the original text
#         if not text_content:
#             text_content = '\n'.join(choosen_manual.markup_all_text)

#         question = f"A user has a question regarding a {device}. The question is: {user_question}. Does the attached manual answer the question? If it does please answer the question based on the information in the manual. If not answer: The answer can not be found"

#         llm_answer = get_llm_answer(text_content, question)
#         return llm_answer

#     except Exception as e:
#         # Log the actual error for debugging
#         print(f"Error in process_llm_query: {str(e)}")
#         raise HTTPException(
#             status_code=500, detail=f"Internal server error: {str(e)}")

# kör direkt på första filen utan språktvätt men får ett dict error
# @router.post("/llm_request_full_text", status_code=201)
# def process_llm_query(
#     user_question: str,
#     file_id: str,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     """LLM endpoint with validated params"""
#     try:
#         # Get the manual URL
#         url_response = get_manual_url_for_download(
#             file_id=file_id,
#             current_user=current_user,
#             db=db
#         )

#         url = url_response["downloadUrl"]  # Extract the URL from the response

#         # Get the device type
#         stmt = (
#             select(DeviceTypes.type)
#             .join(Manuals, Manuals.device_type_id == DeviceTypes.id)
#             .where(Manuals.id == file_id)
#         )

#         # Execute the query and fetch the result
#         result = db.execute(stmt)
#         device = result.scalar_one_or_none()

#         if not device:
#             raise HTTPException(
#                 status_code=404, detail="Device type not found")

#         # Process the manual - specify that we're using a remote URL
#         choosen_manual = DocPreProcessLLM(url, is_remote_url=True)

#         # Get the actual raw text from markup_all_text
#         # Since we need the raw text content for the LLM, let's use the original markup text
#         text_content = '\n'.join(choosen_manual.markup_all_text)

#         question = f"A user has a question regarding a {device}. The question is: {user_question}. Does the attached manual answer the question? If it does please answer the question based on the information in the manual. If not answer: The answer can not be found"

#         llm_answer = get_llm_answer(text_content, question)
#         return llm_answer

#     except Exception as e:
#         # Log the actual error for debugging
#         print(f"Error in process_llm_query: {str(e)}")
#         raise HTTPException(
#             status_code=500, detail=f"Internal server error: {str(e)}")


# med språktvätt - TO DO kolla på hur allt byggs
# @router.post("/llm_request_full_text", status_code=201)
# def process_llm_query(
#     user_question: str,
#     file_id: str,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     """LLM endpoint with validated params"""
#     try:
#         # Get the manual URL
#         url_response = get_manual_url_for_download(
#             file_id=file_id,
#             current_user=current_user,
#             db=db
#         )

#         url = url_response["downloadUrl"]  # Extract the URL from the response

#         # Get the device type
#         stmt = (
#             select(DeviceTypes.type)
#             .join(Manuals, Manuals.device_type_id == DeviceTypes.id)
#             .where(Manuals.id == file_id)
#         )

#         # Execute the query and fetch the result
#         result = db.execute(stmt)
#         device = result.scalar_one_or_none()

#         if not device:
#             raise HTTPException(
#                 status_code=404, detail="Device type not found")

#         # Process the manual - specify that we're using a remote URL
#         choosen_manual = DocPreProcessLLM(url, is_remote_url=True)

#         # If markup_one_lang_text is a list of dictionaries, extract the text content
#         # This depends on the structure of your dictionaries
#         if choosen_manual.markup_one_lang_text and isinstance(choosen_manual.markup_one_lang_text[0], dict):
#             # Assuming each dictionary has a 'text' or similar field that contains the actual content
#             # Modify this based on your actual dictionary structure
#             if 'heading' in choosen_manual.markup_one_lang_text[0]:
#                 text_content = '\n'.join(
#                     [item['heading'] for item in choosen_manual.markup_one_lang_text])
#             else:
#                 # If there's no specific field, convert the whole dictionary to string
#                 text_content = '\n'.join(
#                     [str(item) for item in choosen_manual.markup_one_lang_text])
#         else:
#             # If it's already a list of strings
#             text_content = '\n'.join(choosen_manual.markup_one_lang_text)

#         question = f"A user has a question regarding a {device}. The question is: {user_question}. Does the attached manual answer the question? If it does please answer the question based on the information in the manual. If not answer: The answer can not be found"

#         llm_answer = get_llm_answer(text_content, question)
#         return llm_answer

#     except Exception as e:
#         # Log the actual error for debugging
#         print(f"Error in process_llm_query: {str(e)}")
#         raise HTTPException(
#             status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/llm_request_full_text", status_code=201)
def process_llm_query(
    user_question: str,
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """LLM endpoint with validated params"""
    try:
        # Get the manual URL
        url_response = get_manual_url_for_download(
            file_id=file_id,
            current_user=current_user,
            db=db
        )

        url = url_response["downloadUrl"]  # Extract the URL from the response

        # Get the device type
        stmt = (
            select(DeviceTypes.type)
            .join(Manuals, Manuals.device_type_id == DeviceTypes.id)
            .where(Manuals.id == file_id)
        )

        # Execute the query and fetch the result
        result = db.execute(stmt)
        device = result.scalar_one_or_none()

        if not device:
            raise HTTPException(
                status_code=404, detail="Device type not found")

        # Directly download and process the PDF without using DocPreProcessLLM
        import requests
        import fitz  # PyMuPDF
        import io
        import pymupdf4llm

        # Download the PDF
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download PDF: {response.status_code}")

        # Load the PDF
        pdf_bytes = io.BytesIO(response.content)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Convert directly to text
        text_content = pymupdf4llm.to_markdown(doc)

        question = f"En användare har en fråga om sin {device}. Frågan är: {user_question}. Finns svaret på frågan i den bifogade manualen? Om svaret är ja, svara på frågan baserat på informationen i manualen. Om inte, svara: Svaret finns inte i manualen"

        llm_answer = get_llm_answer(text_content, question)
        return llm_answer

    except Exception as e:
        # Log the actual error for debugging
        print(f"Error in process_llm_query: {str(e)}")
        # Include more detailed error information for troubleshooting
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


# router = APIRouter(tags=["uploads"], prefix="/uploads")
