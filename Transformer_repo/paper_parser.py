## paper_parser.py
import json
import logging
from typing import Any, Dict, List

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PaperParser:
    """PaperParser class responsible for parsing a research paper provided in JSON format
    and extracting its structured components such as paper_id, title, abstract, body_text,
    figures, and reference entries.
    """

    def __init__(self, paper_json: Dict[str, Any]) -> None:
        """
        Initializes the PaperParser with the paper JSON.

        Args:
            paper_json (Dict[str, Any]): The JSON dictionary representing the research paper.

        Raises:
            ValueError: If the input JSON is missing required keys (e.g., "paper_id" or "title").
        """
        self.paper_json = paper_json
        if "paper_id" not in self.paper_json or "title" not in self.paper_json:
            logging.error("Paper JSON missing required fields: 'paper_id' and/or 'title'.")
            raise ValueError("Paper JSON must contain 'paper_id' and 'title' fields.")

    def _clean_text(self, text: str) -> str:
        """
        Cleans and normalizes a string by stripping leading and trailing whitespace.

        Args:
            text (str): The text string to be cleaned.

        Returns:
            str: The cleaned text.
        """
        return text.strip()

    def parse(self) -> Dict[str, Any]:
        """
        Parses the input paper JSON and extracts required components:
         - paper_id
         - title
         - abstract
         - body_text
         - figures (from back_matter)
         - reference entries (ref_entries)

        Returns:
            Dict[str, Any]: A structured Paper object as a dictionary containing all the extracted fields.
        """
        paper: Dict[str, Any] = {}

        # Extract paper_id and title
        paper["paper_id"] = self._clean_text(str(self.paper_json.get("paper_id", "")))
        paper["title"] = self._clean_text(str(self.paper_json.get("title", "")))

        # Extract abstract from either "abstract" key or within "pdf_parse"
        abstract_text = ""
        if "abstract" in self.paper_json and self.paper_json["abstract"]:
            if isinstance(self.paper_json["abstract"], list):
                segments: List[str] = []
                for item in self.paper_json["abstract"]:
                    if isinstance(item, dict):
                        segment = self._clean_text(item.get("text", ""))
                        if segment:
                            segments.append(segment)
                    elif isinstance(item, str):
                        segments.append(self._clean_text(item))
                abstract_text = " ".join(segments)
            elif isinstance(self.paper_json["abstract"], str):
                abstract_text = self._clean_text(self.paper_json["abstract"])
        elif "pdf_parse" in self.paper_json and "abstract" in self.paper_json["pdf_parse"]:
            pdf_abstract = self.paper_json["pdf_parse"]["abstract"]
            if isinstance(pdf_abstract, list):
                segments = [
                    self._clean_text(item.get("text", ""))
                    for item in pdf_abstract
                    if isinstance(item, dict) and item.get("text", "").strip()
                ]
                abstract_text = " ".join(segments)
            elif isinstance(pdf_abstract, str):
                abstract_text = self._clean_text(pdf_abstract)
        else:
            logging.warning("Abstract not found in the paper JSON.")

        paper["abstract"] = abstract_text

        # Extract body text from "body_text" key
        body_text = ""
        if "body_text" in self.paper_json and isinstance(self.paper_json["body_text"], list):
            segments: List[str] = []
            for item in self.paper_json["body_text"]:
                if isinstance(item, dict):
                    segment = self._clean_text(item.get("text", ""))
                    if segment:
                        segments.append(segment)
                elif isinstance(item, str):
                    segments.append(self._clean_text(item))
            body_text = "\n".join(segments)
        else:
            logging.warning("Body text not found in the paper JSON.")

        paper["body_text"] = body_text

        # Extract figures from "back_matter" if available
        figures: List[str] = []
        if "back_matter" in self.paper_json and isinstance(self.paper_json["back_matter"], list):
            for item in self.paper_json["back_matter"]:
                if isinstance(item, dict):
                    text = self._clean_text(item.get("text", ""))
                    if text:
                        figures.append(text)
                elif isinstance(item, str):
                    figures.append(self._clean_text(item))
        paper["figures"] = figures

        # Extract reference entries from "ref_entries" if available
        ref_entries: Dict[str, Any] = {}
        if "ref_entries" in self.paper_json and isinstance(self.paper_json["ref_entries"], dict):
            ref_entries = self.paper_json["ref_entries"]
        else:
            logging.info("Reference entries not found in the paper JSON.")
        paper["ref_entries"] = ref_entries

        return paper

# For standalone testing
if __name__ == "__main__":
    # Sample paper JSON for testing purposes
    sample_paper_json = {
        "paper_id": "1234",
        "title": "Sample Paper Title",
        "abstract": [{"text": "This is the abstract of the sample paper."}],
        "body_text": [
            {"text": "Introduction: This section introduces the paper."},
            {"text": "Method: This section explains the methodology."}
        ],
        "back_matter": [{"text": "Figure 1: Sample figure description."}],
        "ref_entries": {
            "REF1": {
                "text": "Reference 1 details.",
                "num": 1
            }
        }
    }
    
    try:
        parser = PaperParser(sample_paper_json)
        parsed_paper = parser.parse()
        print(json.dumps(parsed_paper, indent=2))
    except ValueError as ve:
        logging.error(f"Error parsing paper JSON: {ve}")
