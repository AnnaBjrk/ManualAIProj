import os
import fitz  # PyMuPDF
from langdetect import detect, DetectorFactory, LangDetectException
import re
import fitz  # PyMuPDF's import name
import pymupdf4llm
from langdetect import detect
from langdetect import DetectorFactory
import pathlib
# Load from a file path


class DocPreProcessLLM:
    def __init__(self, pdf_url="dummy_images/samsung_tv_multi_lang.pdf"):
        self.pdf_url = pdf_url
        self.markup_all_text = create_markup_text()  # lines in a list
        self.markup_all_headlines =
        self.markup_selected_language =


def print_md_text(self):
    print(md_text)


# Or load from bytes (e.g., from S3)
# pdf_bytes = s3_client.get_object(Bucket='my-bucket', Key='document.pdf')['Body'].read()
# doc = fitz.open(stream=pdf_bytes, filetype="pdf")


def create_markup_text(self):

    # Load the PDF document
    pdf_path = "your_document.pdf"
    doc = fitz.open(pdf_path)

    # Convert to markdown
    markdown_text = pymupdf4llm.to_markdown(doc)

    # Store in your class variable
    self.md_text = markdown_text

    # Now you can split into lines if needed
    text_lines = self.md_text.split('\n')


# Set seed for reproducible language detection results
DetectorFactory.seed = 0


def extract_language_content(self):
    """
    Extract content in the target language and preserve page markers
    """

    # Initialize variables
    language_blocks = []
    current_block = []
    in_target_language = False
    target_language1 = 'sv'
    target_language2 = "en"
    min_block_size = 200

    # Process each line
    line_index = 0
    while line_index < len(self.markup_all_text):
        # Get a window of text for analysis
        window_end = min(line_index + 20, len(self.markup_all_text))
        window = '\n'.join(self.markup_all_text[line_index:window_end])

        # Detect language
        try:
            lang = detect(window)
            # If we found our target language
            if lang == target_language1:
                if not in_target_language1:
                    # If we're starting a new target language block
                    in_target_language = True
                    current_block = []

                # Add all lines in the window to the current block
                for i in range(line_index, window_end):
                    if i < len(lines):  # Ensure we don't go out of bounds
                        current_block.append(lines[i])
                        line_pages[len(language_blocks) +
                                   len(current_block) - 1] = page_numbers[i]

                line_index = window_end
            else:
                # Not target language
                if in_target_language:
                    # If we were in target language, check if this is truly the end
                    next_window_start = line_index + 1
                    next_window_end = min(next_window_start + 20, len(lines))
                    if next_window_end > next_window_start:
                        next_window = '\n'.join(
                            lines[next_window_start:next_window_end])
                        if len(next_window.strip()) >= min_block_size:
                            try:
                                next_lang = detect(next_window)
                                if next_lang != target_language:
                                    # Confirmed end of target language section
                                    language_blocks.extend(current_block)
                                    current_block = []
                                    in_target_language = False
                                else:
                                    # False alarm, continue in target language
                                    current_block.append(lines[line_index])
                                    line_pages[len(
                                        language_blocks) + len(current_block) - 1] = page_numbers[line_index]
                            except LangDetectException:
                                # If detection fails, assume we're still in target language
                                current_block.append(lines[line_index])
                                line_pages[len(
                                    language_blocks) + len(current_block) - 1] = page_numbers[line_index]
                        else:
                            # Next window too small, keep current line
                            current_block.append(lines[line_index])
                            line_pages[len(
                                language_blocks) + len(current_block) - 1] = page_numbers[line_index]
                    else:
                        # No next window, keep current line
                        current_block.append(lines[line_index])
                        line_pages[len(
                            language_blocks) + len(current_block) - 1] = page_numbers[line_index]

                line_index += 1

        except LangDetectException:
            # If language detection fails, keep the line in the current block if we're in target language
            if in_target_language:
                current_block.append(lines[line_index])
                line_pages[len(language_blocks) +
                           len(current_block) - 1] = page_numbers[line_index]
            line_index += 1

    # Add the last block if it's in the target language
    if in_target_language and current_block:
        language_blocks.extend(current_block)

    # Combine all target language blocks
    extracted_text = '\n'.join(language_blocks)

    # Make sure page separators are properly formatted
    extracted_text = re.sub(r'(\n-{5,}\n)', r'\n\n\1\n\n', extracted_text)

    # Add explicit page numbers at each separator if desired
    if False:  # Set to True if you want explicit page numbers
        result_lines = extracted_text.split('\n')
        for i in range(len(result_lines)):
            if re.match(r'^\s*-{5,}\s*$', result_lines[i]):
                page_num = line_pages.get(i, 0)
                result_lines[i] = f"{result_lines[i]}\n[Page {page_num}]"
        extracted_text = '\n'.join(result_lines)

    return extracted_text


def clean_up_markdown(text):
    """
    Clean up the extracted markdown to make it more readable
    """
    # Remove multiple consecutive empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Ensure headers have proper spacing
    text = re.sub(r'(\n#+)([^ ])', r'\1 \2', text)

    # Fix broken headers (e.g., ###Header)
    text = re.sub(r'(#+)([^ #])', r'\1 \2', text)

    return text


def process_pdf_directly(pdf_path, target_language='sv'):
    """
    Process a PDF file directly, maintaining page numbers
    """
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Process each page and detect language
    extracted_content = []
    page_markers = []

    for page_num, page in enumerate(doc):
        # Extract text from the page
        text = page.get_text()

        # Skip if page is too short
        if len(text.strip()) < 100:
            continue

        # Detect language
        try:
            lang = detect(text)
            if lang == target_language:
                # Convert to markdown
                page_md = pymupdf4llm.to_markdown(doc, [page_num])
                extracted_content.append(page_md)
                page_markers.append(f"\n\n-----\n[Page {page_num + 1}]\n\n")
        except LangDetectException:
            continue

    # Combine all pages with markers
    result = ""
    for i, content in enumerate(extracted_content):
        if i > 0:
            result += page_markers[i-1]
        result += content

    return result


def count_markdown_headings(markdown_text):
    """
    Count the number of headings at each level (# through ######) in a markdown document.

    Args:
        markdown_text (str): The markdown text to analyze

    Returns:
        dict: A dictionary with keys 'h1' through 'h6' and their counts
    """
    # Initialize counts for each heading level
    heading_counts = {
        'h1': 0,  # #
        'h2': 0,  # ##
        'h3': 0,  # ###
        'h4': 0,  # ####
        'h5': 0,  # #####
        'h6': 0   # ######
    }

    # Split the text into lines
    lines = markdown_text.split('\n')

    # Regular expressions to match headings at different levels
    # The pattern matches headings at the start of a line with optional space after the hashtags
    h1_pattern = re.compile(r'^\s*# +')
    h2_pattern = re.compile(r'^\s*## +')
    h3_pattern = re.compile(r'^\s*### +')
    h4_pattern = re.compile(r'^\s*#### +')
    h5_pattern = re.compile(r'^\s*##### +')
    h6_pattern = re.compile(r'^\s*###### +')

    # Check each line for headings
    for line in lines:
        if h6_pattern.match(line):
            heading_counts['h6'] += 1
        elif h5_pattern.match(line):
            heading_counts['h5'] += 1
        elif h4_pattern.match(line):
            heading_counts['h4'] += 1
        elif h3_pattern.match(line):
            heading_counts['h3'] += 1
        elif h2_pattern.match(line):
            heading_counts['h2'] += 1
        elif h1_pattern.match(line):
            heading_counts['h1'] += 1

    return heading_counts


def count_words(markdown_text):
    """
    Count the number of words in a markdown document.

    Args:
        markdown_text (str): The markdown text to analyze

    Returns:
        int: The total number of words in the document
    """
    # Remove code blocks
    text_without_code = re.sub(
        r'```.*?```', '', markdown_text, flags=re.DOTALL)

    # Remove inline code
    text_without_inline_code = re.sub(r'`.*?`', '', text_without_code)

    # Remove HTML tags
    text_without_html = re.sub(r'<.*?>', '', text_without_inline_code)

    # Remove URLs
    cleaned_text = re.sub(r'https?://\S+', '', text_without_html)

    # Split by whitespace and count words
    words = re.findall(r'\b\w+\b', cleaned_text)
    return len(words)


def generate_toc(markdown_text, max_level):
    """
    Generate a table of contents for a markdown document up to a specified heading level.

    Args:
        markdown_text (str): The markdown text to analyze
        max_level (str): The maximum heading level to include ('h1', 'h2', 'h3', 'h4', 'h5', or 'h6')

    Returns:
        list: A list of dictionaries with heading text and level, e.g. [{"heading": "My Title", "level": "h1"}]
        the order of the list shows the order the headlines appears in the document.
    """
    # Validate max_level input
    valid_levels = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
    if max_level not in valid_levels:
        raise ValueError(f"max_level must be one of {valid_levels}")

    # Convert the heading level string to a numeric value
    max_level_num = int(max_level[1])

    # Split the text into lines
    lines = markdown_text.split('\n')

    # Initialize the table of contents and the position counter
    toc = []
    pos_in_doc = 0
    # Regular expression to match headings
    # Group 1: the heading level (number of #)
    # Group 2: the heading text
    heading_pattern = re.compile(r'^(\#{1,6})\s+(.+)$')

    # Process each line
    for line in lines:
        match = heading_pattern.match(line.strip())
        if match:
            level_markers = match.group(1)  # Get the # symbols
            level_num = len(level_markers)  # Count the number of # symbols

            # Only include headings up to the specified max level
            if level_num <= max_level_num:
                heading_text = match.group(2).strip()
                pos_in_doc += 1
                line_index = lines.index(line)
                # Create a dictionary for this heading
                heading_entry = {
                    "heading": heading_text,
                    "level": f"h{level_num}",
                    "position": pos_in_doc,
                    "line": line_index
                }

                # Add to the table of contents
                toc.append(heading_entry)

    return toc


def fetch_doc_part_for_llm_query(heading_entry, markup_doc_list):
    """Fetches the part of the markup document that is under the headline in the dictionary and create
    a string
    Returns the string"""
    start_line = heading_entry[line]
    finnish_line = heading_entry
    text_section_for_query =


# Example usage
if __name__ == "__main__":
    sample_markdown = """
# Main Title

Some content here.

## Section 1

Content for section 1.

### Subsection 1.1

More detailed content.

## Section 2

Content for section 2.

### Subsection 2.1

#### Even deeper subsection

##### Very deep section
    """

    # Generate TOC up to h3 level
    toc_h3 = generate_toc(sample_markdown, "h3")
    print("TOC up to h3:")
    for item in toc_h3:
        print(f"{item['level']}: {item['heading']}")

    # Generate TOC up to h2 level
    toc_h2 = generate_toc(sample_markdown, "h2")
    print("\nTOC up to h2:")
    for item in toc_h2:
        print(f"{item['level']}: {item['heading']}")

# Example usage
if __name__ == "__main__":
    # Example with a file
    # with open('document.md', 'r', encoding='utf-8') as file:
    #     markdown_text = file.read()
    #     word_count = count_words(markdown_text)
    #     print(f"Total words: {word_count}")

    # Example with a string
    sample_text = """
    # Sample Document
    
    This is a simple **markdown** document with some text.
    It has multiple paragraphs and some formatting.
    
    ## Section
    
    - List item 1
    - List item 2
    
    ```
    Some code block content
    ```
    """

    word_count = count_words(sample_text)
    print(f"Total words: {word_count}")


# Example usage
if __name__ == "__main__":
    sample_text = """
    # Main Title
    Some text here
    
    ## Section 1
    More text
    
    ### Subsection 1.1
    Even more text
    
    ## Section 2
    
    #### Deeply nested section
    ##### Even deeper
    ###### Deepest level
    """

    results = count_markdown_headings(sample_text)
    print("Heading counts:")
    for level, count in results.items():
        print(f"{level}: {count}")


def main():
    # Get input file path from user or use default
    default_path = "paste.txt"
    file_path = input(
        f"Enter the path to your document (default: {default_path}): ") or default_path

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Get target language from user or use default
    target_language = input(
        "Enter the target language code (default: sv for Swedish): ") or "sv"

    # Determine if the file is a PDF or text
    is_pdf = file_path.lower().endswith('.pdf')

    if is_pdf:
        # Handle PDF - choose the approach
        use_direct_method = input(
            "Process PDF directly with page numbers? (y/n, default: y): ").lower() != 'n'

        if use_direct_method:
            try:
                extracted_content = process_pdf_directly(
                    file_path, target_language)
            except Exception as e:
                print(f"Error in direct PDF processing: {e}")
                print("Falling back to text extraction method...")
                use_direct_method = False

        if not use_direct_method:
            try:
                doc = fitz.open(file_path)
                text_content = pymupdf4llm.to_markdown(doc)
                extracted_content = extract_language_content(
                    text_content, target_language)
            except Exception as e:
                print(f"Error converting PDF: {e}")
                return
    else:
        # Handle text file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text_content = f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        except Exception as e:
            print(f"Error reading file: {e}")
            return

        # Extract the target language content
        print(f"Extracting {target_language} content...")
        extracted_content = extract_language_content(
            text_content, target_language)

    # Clean up the extracted content
    extracted_content = clean_up_markdown(extracted_content)

    # Create output filename
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}_{target_language}_extracted.md"

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(extracted_content)

    print(f"Extracted content saved to {output_file}")
    print(f"Extracted {len(extracted_content)} characters")


if __name__ == "__main__":
    main()


######
