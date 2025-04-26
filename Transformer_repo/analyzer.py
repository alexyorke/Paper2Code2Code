## analyzer.py
import logging
from typing import Any, Dict, List

class Analyzer:
    """Analyzer processes the Planner's output (plan dictionary) and produces detailed file-level specifications.
    
    This module bridges high-level planning and low-level code generation by analyzing the overall plan,
    architecture design, and configuration details. It returns a list of dictionaries where each dictionary
    describes the functionality, expected inputs and outputs, and dependency relationships for a module.
    """

    def __init__(self, plan: Dict[str, Any]) -> None:
        """Initializes the Analyzer with the provided plan dictionary.

        Args:
            plan (Dict[str, Any]): Combined output from Planner, including overall plan,
                architecture design (with file_list, class diagram, sequence diagram), and configuration details.
        """
        self.plan = plan
        # Retrieve architecture design; use default if missing.
        self.architecture_design: Dict[str, Any] = self.plan.get("architecture_design", {})
        if not self.architecture_design:
            logging.warning("Architecture design missing in plan. Using default file list.")
            self.architecture_design["file_list"] = [
                "main.py",
                "paper_parser.py",
                "planner.py",
                "analyzer.py",
                "code_generator.py",
                "evaluation.py",
            ]
        self.file_list: List[str] = self.architecture_design.get("file_list", [])
        if not self.file_list:
            logging.warning("File list is empty in architecture design. Assigning default file list.")
            self.file_list = [
                "main.py",
                "paper_parser.py",
                "planner.py",
                "analyzer.py",
                "code_generator.py",
                "evaluation.py",
            ]

    def analyze_modules(self) -> List[Dict[str, Any]]:
        """Analyzes modules specified in the architecture design and creates file-level specifications.

        Iterates over the file list to extract each module's intended functionality, expected inputs,
        expected outputs, and dependency relationships. It cross-references known specifications based on
        the PaperCoder design and logs warnings for any unspecified modules.

        Returns:
            List[Dict[str, Any]]: A list where each element is a dictionary with the following keys:
                - file_name: str, name of the module file.
                - functionality: str, description of the module's role.
                - expected_inputs: List[str], description of the expected inputs.
                - expected_outputs: List[str], description of the outputs provided.
                - dependencies: List[str], list of modules that must precede this module.
        """
        analysis_list: List[Dict[str, Any]] = []
        
        # Predefined module specifications based on design and paper context.
        module_specs = {
            "paper_parser.py": {
                "functionality": (
                    "Parses the input paper JSON and produces a structured Paper object with fields: "
                    "paper_id, title, abstract, body_text, figures, and ref_entries."
                ),
                "expected_inputs": ["Raw paper JSON"],
                "expected_outputs": ["Structured Paper object (dict)"],
                "dependencies": []
            },
            "planner.py": {
                "functionality": (
                    "Generates an overall plan, architecture design (including file list, class diagram, "
                    "and sequence diagram), and configuration details from the structured Paper object."
                ),
                "expected_inputs": ["Structured Paper object (from paper_parser.py)"],
                "expected_outputs": [
                    "Overall plan dictionary",
                    "Architecture design dictionary (file_list, class diagram, sequence diagram)",
                    "Configuration details dictionary"
                ],
                "dependencies": ["paper_parser.py"]
            },
            "analyzer.py": {
                "functionality": (
                    "Analyzes the Planner's output to produce detailed file-level specifications, including module "
                    "responsibilities, input/output contracts, and inter-module dependency relations."
                ),
                "expected_inputs": ["Plan dictionary containing overall plan, architecture design, and configuration details"],
                "expected_outputs": ["List of file-level analysis dictionaries for each module"],
                "dependencies": ["planner.py"]
            },
            "code_generator.py": {
                "functionality": (
                    "Generates modular, dependency-aware code templates for each file based on the overall plan and "
                    "the detailed analysis produced by Analyzer."
                ),
                "expected_inputs": ["Overall plan dictionary", "Detailed file-level analysis from Analyzer"],
                "expected_outputs": ["Dictionary of generated code files (filename : code string)"],
                "dependencies": ["planner.py", "analyzer.py"]
            },
            "evaluation.py": {
                "functionality": (
                    "Evaluates the generated code repository using reference-based and reference-free metrics as defined "
                    "in the experimental setup."
                ),
                "expected_inputs": ["Generated repository (from code_generator.py)"],
                "expected_outputs": ["Evaluation metrics dictionary"],
                "dependencies": ["code_generator.py"]
            },
            "main.py": {
                "functionality": (
                    "Orchestrates the entire pipeline by sequentially invoking the parsing, planning, analysis, code generation, "
                    "and evaluation modules."
                ),
                "expected_inputs": ["Configuration details and outputs from all modules"],
                "expected_outputs": ["Final code repository and evaluation metrics"],
                "dependencies": [
                    "paper_parser.py", "planner.py", "analyzer.py", "code_generator.py", "evaluation.py"
                ]
            },
        }

        # Iterate over the file list to construct analysis for each module.
        for file_name in self.file_list:
            spec = module_specs.get(file_name)
            if spec is None:
                logging.warning("No predefined specification for %s. Using default values.", file_name)
                spec = {
                    "functionality": "No specific functionality defined.",
                    "expected_inputs": [],
                    "expected_outputs": [],
                    "dependencies": []
                }
            analysis = {
                "file_name": file_name,
                "functionality": spec["functionality"],
                "expected_inputs": spec["expected_inputs"],
                "expected_outputs": spec["expected_outputs"],
                "dependencies": spec["dependencies"]
            }
            analysis_list.append(analysis)

        logging.info("Module analysis completed successfully with %d modules analyzed.", len(analysis_list))
        return analysis_list

# Standalone testing of the Analyzer module
if __name__ == "__main__":
    import json

    # Sample plan dictionary combining overall plan, architecture design, and mock configuration.
    sample_plan = {
        "overall_plan": {
            "implementation_goal": "Reproduce experiments as described.",
            "methodology_overview": "Multi-stage pipeline for code generation.",
            "experimental_setup": "Utilize n=8 sampling; evaluation model: o3-mini-high."
        },
        "architecture_design": {
            "file_list": [
                "main.py",
                "paper_parser.py",
                "planner.py",
                "analyzer.py",
                "code_generator.py",
                "evaluation.py"
            ],
            "class_diagram": "classDiagram ...",
            "sequence_diagram": "sequenceDiagram ..."
        },
        "config": {
            "training": {
                "learning_rate": "0.001",
                "batch_size": "32",
                "epochs": "10"
            },
            "evaluation": {
                "n_way_sampling": 8,
                "evaluation_model": "o3-mini-high"
            }
        }
    }

    analyzer = Analyzer(sample_plan)
    analysis_output = analyzer.analyze_modules()
    print(json.dumps(analysis_output, indent=2))
