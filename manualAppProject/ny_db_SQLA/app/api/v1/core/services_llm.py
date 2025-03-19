import os
import fitz  # PyMuPDF
from langdetect import DetectorFactory
import re
import fitz  # PyMuPDF's import name
import pymupdf4llm
from langdetect import detect_langs
from langdetect import DetectorFactory
from exceptions import LanguageError
# Load from a file path


class DocPreProcessLLM:
    def __init__(self, pdf_url="dummy_images/samsung_tv_multi_lang.pdf"):
        self.pdf_url = pdf_url
        self.markup_all_text = self.create_markup_text()  # lines in a list
        self.markup_all_headlines = self.generate_toc(self.markup_all_text)
        self.markup_one_lang_text = self.extract_language_content()
        self.language_used = str  # language en or sv
        # stores all headlines from self.markup_one_lang_text
        self.markup_headlines_one_lang = self.generate_toc(
            self.markup_one_lang_text)
        # stores all headlines in llms choosen prio order
        self.prioritized_headlines = []
        self.markup_headlines_llm_prio_order = []

        # self.markup_selected_language =

    def print_md_text(self, md_text):
        print(md_text)

    # Or load from bytes (e.g., from S3)
    # pdf_bytes = s3_client.get_object(Bucket='my-bucket', Key='document.pdf')['Body'].read()
    # doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    def create_markup_text(self):

        # Load the PDF document
        # pdf_path = "your_document.pdf"
        doc = fitz.open(self.pdf_url)

        # Convert to markdown
        markdown_text = pymupdf4llm.to_markdown(doc)

        # Store in your class variable

        # Now you can split into lines if needed
        text_lines = self.markdown_text.split('\n')

        return text_lines

    # Set seed for reproducible language detection results
    DetectorFactory.seed = 0

    def extract_language_content(self):
        """
        Extract content in the target language either english or swedish.The method  detect_langs() is used -it returns a 
        an object displaying detected language and probability, the probability is accesed by lang.prob and the language with lang.lang
        Variables are the full table of content list self.markup_all_headlines
        heading_entry = {
                        "heading": heading_text,
                        "level": f"h{level_num}",
                        "position": pos_in_doc,
                        "line": line_index
                    }

        creates a list lang_result = [line_start, line_end, language, prediction_score]
        Pulls out the part of the manual that is in swedish - if that not exists the part in english is choosen.
        if none of the languages are choosen

        Raises:
          language error if neither swedish or english is present in the document
        """
        lang_result = []
        for headline_no in len(self.markup_all_headlines):
            line_start = self.markup_all_headlines[headline_no]["line"]
            line_end = self.markup_all_headlines[headline_no+1]["line"]-1
            text_to_check = "\n".join(
                self.markup_all_headlines[line_start:line_end])
            lang_check = detect_langs(text_to_check)
            lang_result.append(
                [line_start, line_end, lang_check.lang, lang_check.prob])

        for analys in lang_result:
            if analys[2] == "sv":
                for line in self.markup_all_headlines[line_start:line_end]:
                    self.markup_one_lang_text.append(line)
                    self.language_used = "sv"
            elif analys[2] == "en":
                for line in self.markup_all_headlines[line_start:line_end]:
                    self.markup_one_lang_text.append(line)
                    self.language_used = "en"
            else:
                raise LanguageError

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

    def count_markdown_headings(markdown_text):
        """
        Count the number of headings at each level (# through ######) in a markdown document.

        Parameters:
            markdown_text (str): The markdown text to analyze

        Returning: A dictionary with keys 'h1' through 'h6' and their counts
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

        Parameters: markdown_text (str): The markdown text to analyze

        Returns: The total number of words in the document
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

    def generate_toc(self, markup_text, max_level="h6"):
        """
        Generate a table of contents for a markdown document up to a specified heading level. Defalut max_level is h6, 

        Args:
            markdown_text (str): The markdown text to analyze
            max_level (str): The maximum heading level to include ('h1', 'h2', 'h3', 'h4', 'h5', or 'h6')

        Returns:
            list: A list of dictionaries with heading text, level of heading, position in text and line index. [{"heading": "My Title", "level": "h1", "position": 5, "line 45"}]
            the order of the list shows the order the headlines appears in the document.

        """

        # Validate max_level input
        valid_levels = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
        if max_level not in valid_levels:
            raise ValueError(f"max_level must be one of {valid_levels}")

        # Convert the heading level string to a numeric value
        max_level_num = int(max_level[1])

        # Split the text into lines

        # Initialize the table of contents and the position counter
        toc = []
        pos_in_doc = 0
        # Regular expression to match headings
        # Group 1: the heading level (number of #)
        # Group 2: the heading text
        heading_pattern = re.compile(r'^(\#{1,6})\s+(.+)$')

        # Process each line
        for line in markup_text:
            match = heading_pattern.match(line.strip())
            if match:
                level_markers = match.group(1)  # Get the # symbols
                level_num = len(level_markers)  # Count the number of # symbols

                # Only include headings up to the specified max level
                if level_num <= max_level_num:
                    heading_text = match.group(2).strip()
                    pos_in_doc += 1
                    line_index = self.markup_all_text.index(line)
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

    def calculate_headline_level(self):
        """Calculates the headline level the document should be divided by.
        uses instance variables and returns the headline level"""
        heading_count = self.count_markdown_headings(
            self.markup_headlines_one_lang)
        count_words = self.count_words(self.markup_one_lang_text)
        total_headlines = 0
        order = ["h1", "h2", "h3", "h4", "h5", "h6"]
        for headline in order:
            total_headlines = total_headlines + heading_count[headline]
            block_size = count_words/total_headlines
            if block_size < 2000:
                return headline

    def fetch_doc_part_for_llm_query(self, heading_entry):
        """Fetches the part of the markup document that is under the headline in the dictionary and create
        a string
        Returns the string"""
        start_line = heading_entry["line"]
        position = heading_entry["position"]
        end_position = len(self.markup_headlines_one_lang)
        if (position + 1) <= end_position:
            next_headline = self.markup_headlines_one_lang[position+1]
            # the function below needs the endline + 1 so we present the number of the next healine
            end_line_for_join = next_headline["line"]

        else:
            end_line_for_join = len(self.markup_one_lang_text) + 1

        text_section_for_query = '\n'.join(
            self.markup_headlines_one_lang[start_line:end_line_for_join])

        return text_section_for_query
