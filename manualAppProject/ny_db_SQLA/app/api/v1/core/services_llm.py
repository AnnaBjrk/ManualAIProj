import fitz  # PyMuPDF's import name
import pymupdf4llm
from langdetect import detect
from langdetect import DetectorFactory
import pathlib
# Load from a file path
doc = fitz.open("dummy_images/samsung_tv_multi_lang.pdf")

# Or load from bytes (e.g., from S3)
# pdf_bytes = s3_client.get_object(Bucket='my-bucket', Key='document.pdf')['Body'].read()
# doc = fitz.open(stream=pdf_bytes, filetype="pdf")


md_text = pymupdf4llm.to_markdown(doc)
print(md_text)

pathlib.Path("manual_markup2.pdf").write_bytes(md_text.encode())
# before first language detection
DetectorFactory.seed = 0
