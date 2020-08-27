from __future__ import annotations
from typing import Union, Dict, Any, List
import os, json

# Markdown Grammer
HEADING = "#"
ITALIC = "*"
BOLD = "**"

# Data Indicator
DOCUMENT = Dict[str, str]    # Raw dictionary value for document
PACKAGE = Dict[str, Union[str, Dict[str, str], Dict[str, Union[str, dict]]]]

DATA = Union[str, int]
CONTENT = List[Dict[str, DATA]]
PARSED = Union[CONTENT, ]


class MarkdownDocument:
    """
    Single markdown document type.
    {
        "filename": markdown file name,
        "content": markdown file content
    }
    """

    def __init__(self, document: DOCUMENT):
        self.document = document

    def get_content(self) -> str:
        return self.document["content"]

    def get_filename(self) -> str:
        return self.document["filename"]

    def __str__(self) -> str:
        return json.dumps(self.document, indent=4, ensure_ascii=False)


class MarkdownPacakge:
    """
    Markdown data will be parsed with these style :
    {
        "dirname" : directory name
        "docs" : {
            "filename":
        }
    }
    """
    def __init__(self, package: Dict[str, Any]):
        self.package = package

    def get_doc(self, dir: str) -> Union[MarkdownDocument, MarkdownPacakge]:
        dir_names = dir.split('/')
        target: dict = None
        for dir_name in dir_names:
            if target is None:
                target = self.package["docs"][dir_name]
            else:
                if target["type"] == "file":
                    break
                target = target["docs"][dir_name]

        if target["type"] == "file":
            return MarkdownDocument(document=target)
        elif target["type"] == "package":
            return MarkdownPacakge(package=target)
        else:
            raise ValueError("Unexpected data to parse as MarkdownDocument or MarkdownPackage!")

    def __str__(self) -> str:
        return json.dumps(self.package, indent=4, ensure_ascii=False)


def parse_doc(root: str, is_root: bool = True) -> Union[MarkdownPacakge, PACKAGE]:
    files = os.listdir(root)
    result: PACKAGE = {
        "type": "package",
        "dirname": root,
        "docs": {

        }
    }

    for file in files:
        if file.endswith(".md"):
            """
            Found file in root.
            """
            with open(f"{root}/{file}", mode="rt", encoding="utf-8") as document_file:
                result["docs"][file] = {
                    "type": "file",
                    "filename": file,
                    "content": document_file.read()
                }
        elif '.' not in file:
            """
            Found directory in root.
            """
            result["docs"][file] = parse_doc(f"{root}/{file}", is_root=False)

    if is_root:
        return MarkdownPacakge(package=result)
    else:
        return result


class MarkdownParser:
    """
    Parser for markdown document file.
    """
    def __init__(self):
        pass

    def parse_dir(self, file_dir: str, is_root: bool = True) -> Dict[str, PARSED]:
        files = os.listdir(file_dir)
        if is_root:
            result = {
                "root": file_dir,
                "type": "folder",
                "content": []
            }
        else:
            result = {
                "type": "folder"
            }
        for file in files:
            if file.endswith(".md"):
                result["content"].append(self.parse(file))
            elif '.' not in file:
                """
                Simple way to detect whether this is folder or file.
                Can misjudge folder as file, but since it can be ignored, I'll use this way.
                """
                result["content"].append(self.parse_dir(file, is_root=False))

        return result

    def parse(self, file_dir: str):
        with open(file=file_dir, mode="rt", encoding="ut-8") as document_file:
            result = {
                "type": "file",
                "filename": file_dir,
                "content": self._parse_markdown(file=document_file)
            }
            return result

    def _parse_markdown(self, file) -> Dict[str, Any]:
        """
        parse markdown file into

        :param file: file object which is readable, and text mode.
        :return: parsed, processed markdown data.
        """
        data: List[Dict[str, Any]] = []
        for line in file:
            line_datas: List[Dict[str, Any]]
            eat: str = ""
            for char in line:
                # Parse entire line : Heading
                # Heading parser
                if line.startswith(HEADING):
                    data.append(self._process_heading(line))

                # Parse consumed some chars only : Bold, Italic,
                # Bold parser
                elif eat.startswith(BOLD) and eat.endswith(BOLD):
                    data.append(self._process_bold(eat))

                # Nothing to parse. eat char and parse again.
                else:
                    eat += char

    def _process_heading(self, line: str) -> Dict[str, Any]:
        level: int = line.count(HEADING)
        return {
            "Type": "Heading",
            "content": line.replace(HEADING, ''),
            "Level": level
        }

    def _process_bold(self, line: str) -> Dict[str, Any]:
        return {
            "Type": "Bold",
            "content": line.replace(BOLD, '')
        }

    def _process_italic(self, line: str) -> Dict[str, Any]:
        return {
            "Type": "Italic",
            "content": line.replace(ITALIC, '')
        }









