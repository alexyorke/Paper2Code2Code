# planner.py
import os
import logging
from typing import Any, Dict, List

try:
    import yaml
except ImportError as e:
    logging.error("PyYAML is required to load configuration. Please install it using 'pip install pyyaml'.")
    raise e

class Planner:
    """Planner class responsible for converting a structured Paper object into
    an overall plan, an architecture design, and configuration details.
    """

    def __init__(self, paper: Dict[str, Any]) -> None:
        """
        Initializes the Planner with a structured Paper object.

        Args:
            paper (Dict[str, Any]): The parsed research paper object containing fields
                                    such as title, abstract, body_text, etc.
        """
        self.paper = paper
        self.overall_plan: Dict[str, Any] = {}

    def create_overall_plan(self) -> Dict[str, Any]:
        """
        Analyzes the Paper object to extract high-level implementation details and constructs
        an overall plan document that outlines the implementation goals and the experimental setup.

        Returns:
            Dict[str, Any]: A dictionary representing the overall plan, with keys including:
                            'implementation_goal', 'methodology_overview', 'experimental_setup',
                            'ambiguous_details', and 'paper_summary'.
        """
        plan: Dict[str, Any] = {}
        title = self.paper.get("title", "Untitled Paper")
        abstract = self.paper.get("abstract", "")
        body_text = self.paper.get("body_text", "")

        # Define the high-level goals based on paper details
        plan["implementation_goal"] = (
            f"Reproduce the experiments and methodologies described in the paper titled '{title}'."
        )
        plan["methodology_overview"] = (
            "Components include data preprocessing, model training, evaluation, and architectural design "
            "with interdependent modules mirroring the multi-stage pipeline described in the paper."
        )
        plan["experimental_setup"] = (
            "Experimentation should follow a dependency-aware pipeline utilizing n=8 sampling for evaluation, "
            "and both reference-based and reference-free evaluation using the specified evaluation model."
        )

        # Flag ambiguous or insufficient details
        ambiguous: List[str] = []
        if not abstract:
            ambiguous.append("Abstract is missing or insufficient to extract methodology details.")
        if not body_text:
            ambiguous.append("Body text is missing; experimental procedures and detailed methods are unclear.")
        plan["ambiguous_details"] = ambiguous

        # Summarize key paper context
        plan["paper_summary"] = {
            "title": title,
            "abstract_excerpt": abstract[:200] + ("..." if len(abstract) > 200 else ""),
        }

        self.overall_plan = plan
        logging.info("Overall plan created successfully.")
        return plan

    def generate_architecture_design(self) -> Dict[str, Any]:
        """
        Generates the architecture design including a file list, UML class diagram, and a sequence diagram
        illustrating the call flow between modules.

        Returns:
            Dict[str, Any]: A dictionary with keys:
                            - 'file_list': List of repository file names.
                            - 'class_diagram': UML class diagram in mermaid syntax.
                            - 'sequence_diagram': Sequence diagram detailing module interactions.
        """
        architecture: Dict[str, Any] = {}

        # Define a concrete file list as per design
        file_list: List[str] = [
            "main.py",
            "paper_parser.py",
            "planner.py",
            "analyzer.py",
            "code_generator.py",
            "evaluation.py"
        ]
        architecture["file_list"] = file_list

        # Generate UML Class Diagram using mermaid syntax
        class_diagram = (
            "classDiagram\n"
            "    class Main {\n"
            "        +__init__(config: dict)\n"
            "        +run_pipeline()\n"
            "    }\n"
            "    class PaperParser {\n"
            "        +__init__(paper_json: dict)\n"
            "        +parse() -> dict\n"
            "    }\n"
            "    class Planner {\n"
            "        +__init__(paper: dict)\n"
            "        +create_overall_plan() -> dict\n"
            "        +generate_architecture_design() -> dict\n"
            "        +generate_config() -> dict\n"
            "    }\n"
            "    class Analyzer {\n"
            "        +__init__(plan: dict)\n"
            "        +analyze_modules() -> list\n"
            "    }\n"
            "    class CodeGenerator {\n"
            "        +__init__(analysis: list, plan: dict)\n"
            "        +generate_code() -> dict\n"
            "    }\n"
            "    class Evaluator {\n"
            "        +__init__(repository: dict)\n"
            "        +evaluate() -> dict\n"
            "    }\n"
            "    Main --> PaperParser\n"
            "    Main --> Planner\n"
            "    Main --> Analyzer\n"
            "    Main --> CodeGenerator\n"
            "    Main --> Evaluator\n"
        )
        architecture["class_diagram"] = class_diagram

        # Generate Sequence Diagram representing program call flow
        sequence_diagram = (
            "sequenceDiagram\n"
            "    participant M as Main\n"
            "    participant PP as PaperParser\n"
            "    participant PL as Planner\n"
            "    participant AN as Analyzer\n"
            "    participant CG as CodeGenerator\n"
            "    participant EV as Evaluator\n"
            "    M->>PP: load paper JSON and call parse()\n"
            "    PP-->>M: return structured Paper object\n"
            "    M->>PL: pass Paper object; call create_overall_plan()\n"
            "    PL-->>M: return overall plan\n"
            "    M->>PL: call generate_architecture_design()\n"
            "    PL-->>M: return architecture design with file list, class diagram, and sequence diagram\n"
            "    M->>PL: call generate_config()\n"
            "    PL-->>M: return configuration details\n"
        )
        architecture["sequence_diagram"] = sequence_diagram

        logging.info("Architecture design generated successfully.")
        return architecture

    def generate_config(self) -> Dict[str, Any]:
        """
        Loads the configuration from the 'config.yaml' file and constructs a configuration dictionary.
        This includes training parameters and evaluation settings.

        Returns:
            Dict[str, Any]: A configuration dictionary with keys 'training' and 'evaluation'.
        """
        config: Dict[str, Any] = {}
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

        try:
            with open(config_path, "r", encoding="utf-8") as file:
                loaded_config = yaml.safe_load(file)
                if not loaded_config:
                    logging.warning("Config file is empty. Using default configuration values.")
                    loaded_config = {}
        except Exception as e:
            logging.error(f"Failed to load configuration file: {e}")
            loaded_config = {}

        # Retrieve training and evaluation configurations from the loaded config, set defaults if necessary
        training_config = loaded_config.get("training", {})
        evaluation_config = loaded_config.get("evaluation", {})

        config["training"] = {
            "learning_rate": training_config.get("learning_rate", "0.001"),  # Default learning rate
            "batch_size": training_config.get("batch_size", "32"),            # Default batch size
            "epochs": training_config.get("epochs", "10")                     # Default number of epochs
        }

        config["evaluation"] = {
            "n_way_sampling": evaluation_config.get("n_way_sampling", 8),
            "evaluation_model": evaluation_config.get("evaluation_model", "o3-mini-high")
        }

        logging.info("Configuration generated successfully from config.yaml.")
        return config

# Standalone testing of the Planner module
if __name__ == "__main__":
    import json

    # Sample Paper object for testing purposes
    sample_paper = {
        "paper_id": "1234",
        "title": "Sample Paper Title",
        "abstract": "This is a sample abstract for the testing of the Planner module. It describes high-level methods.",
        "body_text": "This is a sample body text that elaborates on the methodology, experimental setup, and evaluation protocols."
    }

    planner_instance = Planner(sample_paper)
    overall_plan = planner_instance.create_overall_plan()
    architecture_design = planner_instance.generate_architecture_design()
    config_details = planner_instance.generate_config()

    print("Overall Plan:")
    print(json.dumps(overall_plan, indent=2))
    print("\nArchitecture Design:")
    print(json.dumps(architecture_design, indent=2))
    print("\nConfiguration Details:")
    print(json.dumps(config_details, indent=2))
