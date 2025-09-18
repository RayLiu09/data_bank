import copy
import logging

from docx import Document

logger: logging.getLogger(__name__)

async def build_kbgraph(path: str):
    logger.info(f"Start to extract KBGraph for file : {path}")
    final_rows = []
    try:
        doc = Document(path)
        rows = []
        level_1 = ""
        level_2 = ""
        level_3 = ""
        level_4 = ""
        content = ""

        for paragraph in doc.paragraphs:
            print(f"Paragraph style: {paragraph.style.name}, text: {paragraph.text}")

            if paragraph.style.name == "Heading 1":
                level_1 = paragraph.text
            if paragraph.style.name == "Heading 2":
                level_2 = paragraph.text
                level_3 = ""
            if paragraph.style.name == "Heading 3":
                level_3 = paragraph.text
                level_4 = ""
            if paragraph.style.name == "Heading 4":
                level_4 = paragraph.text
            if (paragraph.style.name == "Normal" or paragraph.style.name == "Body Text") and (level_3 != "" or level_4 != ""):
                content = paragraph.text
                if content != "":
                    rows.append(
                        {"level_1": level_1, "level_2": level_2, "level_3": level_3, "level_4": level_4,
                         "content": content})

        # logger.info(f"Original total rows: {len(rows)}")
        original_rows = copy.deepcopy(rows)
        for row in original_rows:
            if len(final_rows) == 0:
                final_rows.append(row)
                continue
            if row["level_4"] != "":
                if row["level_4"] != final_rows[len(final_rows) - 1]["level_4"]:
                    final_rows.append(row)
                else:
                    final_rows[len(final_rows) - 1]["content"] += "\n" + row["content"]
            else:
                if row["level_3"] != final_rows[len(final_rows) - 1]["level_3"]:
                    final_rows.append(row)
                else:
                    final_rows[len(final_rows) - 1]["content"] += "\n" + row["content"]
        # logger.info(f"Final total rows: {len(final_rows)}")
    except Exception as e:
        logger.error(f"Error when extract KBGraph for file : {path}, error: {e}")

    return final_rows