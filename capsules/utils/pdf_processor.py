# - *- coding: utf-8 -
import logging
import pathlib
import shutil
from typing import Optional, Tuple
import os

import pymupdf4llm

try:
    import pymupdf as fitz  # PyMuPDF
    from pymupdf import Document
except ImportError:
    fitz = None
    Document = None

try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)


class PdfProcessor:
    """
    PDF格式医疗检测报告文件预处理器，要求能够完整，准确解析PDF格式检测报告内容，包含文本，表格等页面结构信息
    """

    def __init__(self):
        """
        初始化PDF处理器
        """
        if fitz is None:
            raise ImportError("PyMuPDF (fitz) is required for PDF processing. Please install it with 'pip install PyMuPDF'")

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        从PDF文件中提取纯文本内容

        Args:
            pdf_path: PDF文件路径

        Returns:
            str: 提取的文本内容，转换为Markdown格式

        Raises:
            FileNotFoundError: 当PDF文件不存在时
            Exception: 其他处理异常
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            # 打开PDF文档
            doc: Document = fitz.open(pdf_path)

            # 提取所有页面的文本
            text_content = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text").encode("utf-8")
                if text.strip():
                    text_content.append(text.strip())

            doc.close()

            # 将文本内容合并为Markdown格式
            return "\n\n".join(text_content)

        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return None

    def extract_markdown(self, pdf_path: str) -> Optional[str]:
        """
        从PDF文件中提取内容并转换为Markdown格式，保持原有结构

        Args:
            pdf_path: PDF文件路径

        Returns:
            str: Markdown格式的内容

        Raises:
            FileNotFoundError: 当PDF文件不存在时
            Exception: 其他处理异常
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            # 打开PDF文档
            doc: Document = fitz.open(pdf_path)
            markdown_content = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # 获取页面的blocks（文本块和图像等）
                blocks = page.get_text("dict")["blocks"]

                for block in blocks:
                    if "lines" in block:  # 文本块
                        block_text = self._process_text_block(block)
                        if block_text.strip():
                            markdown_content.append(block_text)
                    elif "image" in block:  # 图像块
                        # 对于医疗报告，图像通常很重要，但这里我们只添加占位符
                        markdown_content.append("\n![image](image_placeholder.png)\n")

            doc.close()

            return "\n\n".join(markdown_content)

        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return None

    def _process_text_block(self, block: dict) -> str:
        """
        处理文本块，转换为适当的Markdown格式

        Args:
            block: 文本块字典

        Returns:
            str: 格式化后的文本
        """
        try:
            lines = []
            for line in block["lines"]:
                line_text = ""
                for span in line["spans"]:
                    line_text += span["text"]

                if line_text.strip():
                    lines.append(line_text.strip())

            block_text = " ".join(lines)

            # 根据文本特征判断是否为标题
            if self._is_title(block_text):
                return f"## {block_text}"
            else:
                return block_text

        except Exception as e:
            logger.error(f"Error processing text block: {str(e)}")
            return ""

    def _is_title(self, text: str) -> bool:
        """
        判断文本是否可能是标题

        Args:
            text: 待判断的文本

        Returns:
            bool: 是否为标题
        """
        # 简单的标题判断逻辑
        # 标题通常较短，且可能包含特定关键词
        title_keywords = ["报告", "检查", "项目", "结果", "姓名", "性别", "年龄", "科室", "诊断"]

        if len(text) > 50:  # 标题通常不会太长
            return False

        # 检查是否包含标题关键词
        for keyword in title_keywords:
            if keyword in text:
                return True

        return False

    def extract_tables(self, pdf_path: str) -> Optional[list]:
        """
        从PDF中提取表格数据

        Args:
            pdf_path: PDF文件路径

        Returns:
            list: 表格数据列表，每个表格为一个列表的列表

        Raises:
            FileNotFoundError: 当PDF文件不存在时
            Exception: 其他处理异常
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            if pd is None:
                raise ImportError("pandas is required for table extraction. Please install it with 'pip install pandas'")

            # 打开PDF文档
            doc: Document = fitz.open(pdf_path)
            tables = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # 使用PyMuPDF提取表格
                page_tables = page.find_tables()
                for table in page_tables:
                    # 将表格转换为列表的列表
                    table_data = table.extract()
                    if table_data:
                        tables.append(table_data)

            doc.close()

            return tables

        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            raise
        except ImportError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Error extracting tables from PDF {pdf_path}: {str(e)}")
            return None

    def process_medical_report(self, pdf_path: str) -> Optional[str]:
        """
        处理医疗检测报告，将其转换为结构化的Markdown格式

        Args:
            pdf_path: PDF文件路径

        Returns:
            str: 结构化的Markdown格式报告

        Raises:
            FileNotFoundError: 当PDF文件不存在时
            Exception: 其他处理异常
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            # 打开PDF文档
            doc: Document = fitz.open(pdf_path)
            logger.info(f"Document metadata: {doc.metadata}")
            markdown_sections = []

            # 添加标题
            filename = os.path.basename(pdf_path)
            markdown_sections.append(f"# 医疗检测报告: {filename}\n")

            # 处理每一页
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                markdown_sections.append(f"## 第 {page_num + 1} 页\n")

                # 提取文本内容
                text_dict = page.get_text("dict")
                blocks = text_dict["blocks"]

                for block in blocks:
                    if "lines" in block:  # 文本块
                        block_text = self._process_text_block(block)
                        if block_text.strip():
                            markdown_sections.append(block_text)
                    elif "image" in block:  # 图像块
                        markdown_sections.append("\n![医学图像](image_placeholder.png)\n")

                # 提取表格
                page_tables = page.find_tables()
                if page_tables.tables:
                    markdown_sections.append("\n### 表格数据\n")
                    for i, table in enumerate(page_tables):
                        table_data = table.extract()
                        if table_data:
                            markdown_sections.append(self._table_to_markdown(table_data, f"表{i+1}"))

            doc.close()

            return "\n\n".join(markdown_sections)

        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Error processing medical report {pdf_path}: {str(e)}")
            return None

    def _table_to_markdown(self, table_data: list, table_name: str = "") -> str:
        """
        将表格数据转换为Markdown格式

        Args:
            table_data: 表格数据（列表的列表）
            table_name: 表格名称

        Returns:
            str: Markdown格式的表格
        """
        try:
            if not table_data:
                return ""

            # 创建Markdown表格
            markdown_table = []

            if table_name:
                markdown_table.append(f"**{table_name}**\n")

            # 添加表头
            if table_data[0]:  # 确保有数据
                # 添加列标题分隔行
                header = "| " + " | ".join([str(cell) if cell is not None else "" for cell in table_data[0]]) + " |"
                separator = "|" + "|".join([" --- " for _ in table_data[0]]) + "|"

                markdown_table.append(header)
                markdown_table.append(separator)

                # 添加数据行
                for row in table_data[1:]:
                    if row:  # 确保行有数据
                        row_str = "| " + " | ".join([str(cell) if cell is not None else "" for cell in row]) + " |"
                        markdown_table.append(row_str)

            return "\n".join(markdown_table)

        except Exception as e:
            logger.error(f"Error converting table to markdown: {str(e)}")
            return ""

    @staticmethod
    def extract_content_for_markdown(pdf_path: str, write_images: bool = False, embed_images: bool = False) -> str:
        """
        从PDF中提取所有内容并将其转换为MD格式，包含图片类型内容r
        """
        tmp_dir = "./tmp"
        try:
            md_content = pymupdf4llm.to_markdown(pdf_path, image_path=tmp_dir, write_images= write_images, embed_images= embed_images)
            logger.info(f"Converted PDF to markdown successfully.")
            # 遍历临时目录下的文件，并交给LLM视觉处理模型提取图片内容
            if write_images:
                for filename in os.listdir(tmp_dir):
                    md_content += _vision_process(os.path.join(tmp_dir, filename))
            return md_content
        except Exception as e:
            logger.error(f"Error converting PDF to markdown: {str(e)}")
            return ""
        finally:
            if os.path.exists(tmp_dir):
                # 删除临时目录下的文件，但是保留临时目录
                for filename in os.listdir(tmp_dir):
                    file_path = os.path.join(tmp_dir, filename)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {str(e)}")

def _vision_process(param):
   pass

if __name__ == "__main__":
    pdf_path = "E:/血常规-血常规报告单解读-详细版.pdf"
    pdf_path = "E:/刘巨峰-体检报告.pdf"
    # pdf_processor = PdfProcessor()
    # markdown_report = pdf_processor.process_medical_report(pdf_path)
    # # 将结果写入markdown文本
    # markdown_path = "output.md"
    # with open(markdown_path, "w", encoding="utf-8") as f:
    #     f.write(markdown_report)
    #     logger.info(f"Medical report saved to {markdown_path}")

    md_text = pymupdf4llm.to_markdown(pdf_path, write_images= True, embed_images= True)
    pathlib.Path("output.md").write_text(md_text, encoding="utf-8")
