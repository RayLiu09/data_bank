import glob
import logging
import os
from datetime import datetime
from pathlib import Path

import pdfplumber
from PIL.Image import Image
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PyPdfError
from pdf2image import convert_from_path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTFigure, LTRect, LTChar

from vectors.models.document import Document
from vectors.readers import BaseReader

logger: logging.Logger = logging.getLogger(__name__)


class PDFReader(BaseReader):
    """
    A reader for PDF files.
    """

    def __init__(self):
        super().__init__()
        self.name = "PdfReader"
        self.description = "A reader for digital PDF files."
        self.extensions = [".pdf", ".PDF"]

    def extract_table(self, pdf_file: str, page_num: int, table_num: int):
        pdf = pdfplumber.open(pdf_file)
        # Check sepcified page
        table_page = pdf.pages[page_num]
        table = table_page.extract_tables()[table_num]
        return table

    def table_converter(self, table):
        """
        Convert table to text.
        """
        table_text = ""
        # Loop each table row
        for row_num in range(len(table)):
            row = table[row_num]
            # Delete the Line Break
            cleaned_row = [
                item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for
                item in row]
            # Attention the character '|" and '|n'
            table_text += ('|' + '|'.join(cleaned_row) + '|' + '\n')
        # Remove the last line break
        table_text = table_text[:-1]
        return table_text

    def crop_image(self, element, pageObj, file_name: str):
        """
        Crop images from DPF pages.
        """
        # Get the coordinates of the crop image.
        [image_left, image_top, image_right, image_bottom] = [element.x0, element.y0, element.x1, element.y1]
        # Crop page using the coordinates.
        pageObj.mediabox.lower_left = (image_left, image_bottom)
        pageObj.mediabox.upper_right = (image_right, image_top)
        # Save to new PDF page after cropping.
        cropped_pdf_writer = PdfWriter()
        cropped_pdf_writer.add_page(pageObj)

        # Save the cropped image to a new PDF file.
        file_dir = f"{os.getenv('UPLOAD_DIR')}/cropped/{file_name}"
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        pdf_file = f"{file_dir}/_cropped_image_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        with open(pdf_file, "wb") as cropped_pdf_file:
            cropped_pdf_writer.write(cropped_pdf_file)
        return pdf_file

    def convert_pdf_to_image(self, input_file_path: str):
        images = convert_from_path(input_file_path)
        image = images[0]
        output_file_path = f"{os.getenv('UPLOAD_DIR')}/cropped/{Path(input_file_path).stem}.png"
        image.save(output_file_path, "PNG")
        return output_file_path

    def extract_text_from_image(self, image_path):
        # Read the IMAGE file from the image path
        img = Image.open(image_path)
        # Extract text from the image by OCR, such as pytesseract.image_to_string(img)
        text = ""

        return text

    def text_extract(self, element):
        """
        Extract text from the text line block.
        """
        line_text = element.get_text()

        # Deeply parse the text format information.
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Loop each character in the text line.
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Append character font-family
                        line_formats.append(character.fontname)
                        # Append character font-size
                        line_formats.append(character.size)

        # Find the unique font size and family.
        format_per_line = list(set(line_formats))

        return (line_text, format_per_line)

    def load_pdf(self, file_path: str, **kwargs) -> list[Document]:
        """
        Load PDF files using pdfminer, then loop each pages(LTPage) to parse the layout for content extraction

        Parameters:
            file_path(str): PDF file path;
            kwargs(dict): any other parameters
        Returns:
            list[Document]: a list of documents
        """
        if file_path is None or not Path(file_path).exists():
            logger.error(f"File {file_path} does not exist")
            return []
        pdfReader = PdfReader(file_path)
        if pdfReader is None:
            logger.error(f"Error loading PDF file {file_path}")
            return []
        # Cache the extracted text from each page.
        text_per_page = []
        try:
            for pagenum, page in enumerate(extract_pages(file_path)):
                # Initialize all variables below
                pageObj = pdfReader.pages[pagenum]
                page_text = []
                line_formats = []
                text_from_images = []
                text_from_tables = []
                page_content = []
                table_num = 0
                first_element = True
                table_extraction_flag = False
                # Open the PDF file.
                pdf = pdfplumber.open(file_path)
                # Find the page waiting for checking.
                page_tables = pdf.pages[pagenum].find_tables()

                # Find all elements in page
                page_elements = [(element.y1, element) for element in page._objs]
                # Sort all elements in page
                page_elements.sort(key=lambda x: x[0], reverse=True)

                # Loop each element in the page
                for i, component in enumerate(page_elements):
                    # Obtain the top location of the PDF file.
                    pos = component[0]
                    # Page layout element.
                    element = component[1]
                    # Check if the element is for text.
                    if isinstance(element, LTTextContainer):
                        # Check if text occurs in the table.
                        if table_extraction_flag == False:
                            # Extract text from the text line block.
                            (line_text, format_per_line) = self.text_extract(element)
                            # Append the text to the page.
                            page_text.append(line_text)
                            # Append line format
                            line_formats.append(format_per_line)
                            page_content.append(line_text)
                        else:
                            logger.info(f"Text {line_text} occurs in the table, and omit...")
                    # Check if the element is for image.
                    if isinstance(element, LTFigure):
                        #  Crop the figure from PDF
                        pdf_file = self.crop_image(element, pageObj)
                        output_image = self.convert_pdf_to_image(pdf_file)
                        # Extract text from image
                        image_text = self.extract_text_from_image(output_image)
                        text_from_images.append(image_text)
                        page_content.append(image_text)

                        # Add placeholder for image
                        page_text.append("[IMAGE]")
                        line_formats.append("[IMAGE]")

                        # remove the temp files
                        os.remove(pdf_file)
                        os.remove(output_image)

                    # Check if the element is for table.
                    if isinstance(element, LTRect):
                        # If the first element is a table, set the flag to True.
                        if first_element and (table_num + 1) < len(page_tables):
                            # Find the table boundary.
                            lower_side = page.bbox[3] - page_tables[table_num].bbox[3]
                            upper_side = element.y1
                            # Extract information from table.
                            table = self.extract_table(file_path, pagenum, table_num)
                            if table is not None:
                                # Convert table to string.
                                table_text = self.table_to_string(table)
                                # Append table to the page.
                                text_from_tables.append(table_text)
                                page_content.append(table_text)
                                # Setup the flag to avoid to open it again.
                                table_extraction_flag = True
                                first_element = False
                                # Append placeholder for table
                                page_text.append("[TABLE]")
                                line_formats.append("[TABLE]")

                            # Check if the table has been extracted from pages.
                            if element.y0 >= lower_side and element.y1 <= upper_side:
                                pass
                            elif not isinstance(page_elements[i + 1][1], LTRect):
                                table_extraction_flag = False
                                first_element = True
                                table_num += 1
                # Create dict key for page
                dict_key = f"Page_{str(pagenum)}"
                text_per_page[dict_key] = [page_text, line_formats, text_from_images, text_from_tables, page_content]
        except Exception as ex:
            logger.error(f"Error loading PDF file {file_path}: {ex}")
            return []

    def load(self, file_name: str, file_dir: str = None, **kwargs) -> list[Document]:
        """
        Load a PDF file and return a list of documents.
        @param file_name: the name of the file
        @param file_dir: the directory of the files.
        @param contents: the contents of the files.
        """
        if file_name is not None:
            return self.load_file(file_name, **kwargs)

        if file_dir is not None:
            data_dir = Path(file_dir)
            if data_dir.exists() and data_dir.is_dir():
                self.load_directory(data_dir, kwargs)

    def load_file(self, file_path: str, **kwargs) -> list[Document]:
        documents = []
        full_text = ""
        try:
            logger.info(f"Start loading {file_path}")
            path = Path(file_path)
            reader = PdfReader(path)

            for page in reader.pages:
                full_text += page.extract_text() + "\n\n"

            document = Document(
                name=path.name,
                ext=path.suffix,
                content=full_text,
                metadata=reader.metadata,
                timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            documents.append(document)
        except PyPdfError as e:
            logger.error(f"Error reading {str(file_path)}: {e}")

        logger.info(f"Complete loaded {str(file_path)}")
        return documents

    def load_directory(self, dir_path: Path, **kwargs) -> list[Document]:
        """Loads .pdf files from a directory and its subdirectories.

        @param dir_path : Path - Path to directory

        @returns list[Document] - List of documents
        """
        # Initialize an empty dictionary to store the file contents
        documents = []

        # Convert dir_path to string, in case it's a Path object
        dir_path_str = str(dir_path)

        # Loop through each file type
        for ext in self.extensions:
            # Use glob to find all the files in dir_path and its subdirectories matching the current file_type
            files = glob.glob(f"{dir_path_str}/**/*{ext}", recursive=True)

            # Loop through each file
            for file in files:
                logger.info(f"Reading {str(file)}")
                with open(file, encoding="utf-8"):
                    documents += self.load_file(file, kwargs)

        logger.info(f"Loaded {len(documents)} documents")
        return documents
