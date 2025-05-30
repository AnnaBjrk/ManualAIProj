# OBS logiken för hur vi skickar in bilden behöver ev justeras
#
# This page contains a class DocPreProcess LLM.
# In preprocessing to an LLM there are several steps that needs to be taken with the
# provided manual pdf. This to ensure that the call to the llm more cost efficient and faster.
# First step is to convert the content to markup language - is done with pymupdf4llm.
# Next step is to ensure that if the manual is consisting of several language versions - only one
# language version will be sent to the llm.
# Next is to try to avoid sending the whole pdf to the llm. Rather slice it to smaler pieces - and
# then send the most relevant ones.
# Using the markup with ### ## # ##### we can identify headlines in the documents. We will also decide
# the length of the manual. We will slice the manual at the headline level that gives us slices of
# an average of 2000 words.
#
# When creating an object of this class the image is passed as an argument. Then some of the methods are run
# and their result is set at instance attributes.
# - a list of all textlines in markup format
# - a full table of content with all headlines listed
# - a version of the markup list in only one language (sv or eng)
# - a version of the table of content headline list for the one language document
#
# The rest of the operations needs to be administered by a main program
# - create table of content to send to llm
# - store table of content prioritized by llm
# - keep track of what parts has been read by the llm and what part to send next
# - fetch parts of the pepped markup dokument (to be sent to llm)
#
# the actuall call to the llm is handeled by methods in the services_llm_connection file

from langdetect import DetectorFactory
import re
import fitz  # PyMuPDF's import name
import pymupdf4llm
from langdetect import detect_langs
from langdetect import DetectorFactory
from app.exceptions import LanguageError
import io

# Or load from bytes (e.g., from S3)
# pdf_bytes = s3_client.get_object(Bucket='my-bucket', Key='document.pdf')['Body'].read()
# doc = fitz.open(stream=pdf_bytes, filetype="pdf")


class DocPreProcessLLM:
    def __init__(self,  pdf_url="dummy_images/samsung_tv_multi_lang.pdf", is_remote_url=False):
        self.pdf_url = pdf_url
        self.is_remote_url = is_remote_url
        self.markup_all_text = self.create_markup_text()  # lines in a list
        self.markup_all_headlines = self.generate_toc(self.markup_all_text)
        self.markup_one_lang_text = self.extract_language_content()  # a list of dictionaries
        self.language_used = str  # language en or sv
        # stores all headlines from self.markup_one_lang_text
        self.markup_headlines_one_lang = self.generate_toc(
            self.markup_one_lang_text)
        # stores all headlines in llms choosen prio order
        self.prioritized_headlines = []
        self.markup_headlines_llm_prio_order = []

        # self.markup_selected_language =

    def print_md_text(self, md_text):
        """Function that can be used to print out the mardup document"""
        print(md_text)

    def create_markup_text(self):
        """Creates a markup text of the image given as a parameter when instancing the object
        file Returns: a list of strings. one string for each row in the document."""

        try:
            # Load the PDF document
            if self.is_remote_url:
                # Handle remote URL
                import requests
                response = requests.get(self.pdf_url)
                if response.status_code != 200:
                    raise Exception(
                        f"Failed to download PDF: {response.status_code}")

                pdf_bytes = io.BytesIO(response.content)
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            else:
                # Handle local file
                doc = fitz.open(self.pdf_url)

            # Convert to markdown
            markdown_text_raw = pymupdf4llm.to_markdown(doc)
            markdown_text = self.clean_up_markdown(markdown_text_raw)

            # Store in your class variable
            self.markdown_text = markdown_text

            # Now you can split into lines if needed
            text_lines = self.markdown_text.split('\n')

            return text_lines
        except Exception as e:
            print(f"Error creating markup text: {str(e)}")
            raise

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

        # Set seed for reproducible language detection results
        # DetectorFactory.seed = 0

        markup_one_lang_text = []  # Initialize local variable
        lang_result = []

        for headline_no in range(len(self.markup_all_headlines)):
            line_start = self.markup_all_headlines[headline_no]["line"]
            line_end = self.markup_all_headlines[headline_no+1]["line"]-1
            text_to_check = "\n".join(
                self.markup_all_headlines[line_start:line_end])
            lang_check = detect_langs(text_to_check)
            if lang_check:  # Make sure the list isn't empty
                top_lang = lang_check[0]  # Get the most probable language
                lang_result.append(
                    [line_start, line_end, top_lang.lang, top_lang.prob])

        for analys in lang_result:
            if analys[2] == "sv":
                for line in self.markup_all_headlines[line_start:line_end]:
                    markup_one_lang_text.append(line)
                    self.language_used = "sv"
            elif analys[2] == "en":
                for line in self.markup_all_headlines[line_start:line_end]:
                    markup_one_lang_text.append(line)
                    self.language_used = "en"
            else:
                raise LanguageError

        return markup_one_lang_text  # Return the list

    def clean_up_markdown(self, text):
        """
        Clean up the extracted markdown to make it more readable. Support function for create_markup_text.
        """
        # Remove multiple consecutive empty lines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Ensure headers have proper spacing
        text = re.sub(r'(\n#+)([^ ])', r'\1 \2', text)

        # Fix broken headers (e.g., ###Header)
        text = re.sub(r'(#+)([^ #])', r'\1 \2', text)

        return text

    def count_markdown_headings(self, markdown_text):
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

    def count_words(self, markdown_text):
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
