
from mistralai import Mistral
from app.settings import settings


# fixa så att denna funkar med båda endpoints både den som hämtar manualen direkt och den som kör en
# llm fråga


# def get_manual_upload_url(file_id: int, db, s3_client, current_user):
#     """takes the parameter file_id, Returns: a download url to the s3 bucket
#     In parameter file_id. Returns the upload url_from the S3 Bucket"""
#     # Get file record from database
#     file_upload = db.query(Manuals).filter(
#         Manuals.id == file_id
#     ).first()

#     if not file_upload:
#         raise HTTPException(status_code=404, detail="File not found")

#     # Generate a presigned GET URL
#     try:
#         download_url = s3_client.generate_presigned_url(
#             'get_object',
#             Params={
#                 'Bucket': settings.S3_BUCKET,
#                 'Key': file_upload.s3_key
#             },
#             ExpiresIn=3600  # 1 hour expiration
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     return {"downloadUrl": download_url}


def create_prompt(retrieved_chunk, question):
    prompt = f"""
    Context information is below.
    ---------------------
    {retrieved_chunk}
    ---------------------
    Given the context information and not prior knowledge, answer the query.
    Query: {question}
    Answer:
    """
    return prompt


def run_mistral(client, user_message, model):
    messages = [
        {
            "role": "user", "content": user_message
        }
    ]
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=messages
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_llm_answer(retrieved_chunk, question):
    api_key = settings.MISTRAL_API_KEY
    # api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)
    prompt = create_prompt(retrieved_chunk, question)
    mistral_answer = run_mistral(client, prompt, model)
    return mistral_answer

# osäker vad detta är....
# chat_response = client.chat.complete(
#     model=model,
#     messages=[
#         {
#             "role": "user",
#             "content": "What is the best French cheese?",
#         },
#     ]
# )
# print(chat_response.choices[0].message.content)


# för att köra


# skapa en funktion to tar in användarens fråga samt texten från manualen
# skapa också en funktion som tar in användarens fråga samt toc och frågar om att ranka sektioner
