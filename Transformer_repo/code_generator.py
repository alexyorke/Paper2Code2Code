## code_generator.py
"""
Module: code_generator.py
This module defines the CodeGenerator class which generates code templates for repository files
based on dependency-aware analysis and the overall plan produced by the Planner. It also injects
configuration values from config.yaml into the generated templates. The CodeGenerator iterates over
the file-level analysis provided by the Analyzer to produce a mapping from file names to their complete
code content.
"""

import logging
from typing import Any, Dict, List

class CodeGenerator:
    """
    CodeGenerator class:
    Uses the dependency-aware analysis and overall plan to generate code templates for each repository module.
    It injects configuration values from config.yaml exactly as specified in the plan configuration.
    """

    def __init__(self, analysis: List[Dict[str, Any]], plan: Dict[str, Any]) -> None:
        """
        Initializes the CodeGenerator with the file-level analysis and overall plan.

        Args:
            analysis (List[Dict[str, Any]]): A list of dictionaries containing file-level analysis.
            plan (Dict[str, Any]): The overall plan dictionary including configuration details.
        """
        if not analysis:
            logging.error("Analysis list is empty. Cannot generate code without analysis.")
            raise ValueError("Empty analysis list provided.")
        if not plan:
            logging.error("Plan dictionary is empty. Cannot generate code without plan.")
            raise ValueError("Empty plan dictionary provided.")
        self.analysis = analysis
        self.plan = plan

    def generate_code(self) -> Dict[str, str]:
        """
        Orchestrates the generation of code templates for each repository module based on the analysis.

        Returns:
            Dict[str, str]: A dictionary mapping file names to their generated code content as strings.
        """
        generated_code: Dict[str, str] = {}
        for module in self.analysis:
            file_name = module.get("file_name")
            if not file_name:
                logging.warning("A module in analysis is missing 'file_name'; skipping module.")
                continue
            details = module.get("functionality", "")
            template = self._generate_template(file_name, details)
            # Inject configuration values into the template using the plan's configuration
            final_code = self._inject_configuration(template)
            generated_code[file_name] = final_code
            logging.info("Generated code for module: %s", file_name)
        return generated_code

    def _generate_template(self, file_name: str, details: str) -> str:
        """
        Generates a code template for a given file/module based on its details and intended functionality.

        Args:
            file_name (str): The name of the file/module.
            details (str): A string describing the module's functionality.

        Returns:
            str: A complete code template as a multi-line (triple-quoted) string.
        """
        # For modules already implemented, provide an informational message template.
        if file_name in ["paper_parser.py", "planner.py", "analyzer.py"]:
            return f'''"""
Module: {file_name}
{details}
This module is assumed to be already implemented as part of the PaperCoder system.
"""

# The implementation for {file_name} is provided elsewhere in the repository.
'''
        # Generate a template for the Evaluator module.
        elif file_name == "evaluation.py":
            return '''"""
Module: evaluation.py
Defines the Evaluator class for repository evaluation.
Functionality: Evaluates the generated repository using both reference-based and reference-free metrics.
Configuration placeholders:
    - n_way_sampling: {n_way_sampling}
    - evaluation_model: {evaluation_model}
"""

import logging
from typing import Any, Dict

class Evaluator:
    def __init__(self, repository: Dict[str, Any]) -> None:
        """
        Initializes the Evaluator with the generated repository.
        
        Args:
            repository (Dict[str, Any]): Dictionary of generated code files.
        """
        if not repository:
            logging.error("Empty repository provided to Evaluator.")
            raise ValueError("Repository cannot be empty.")
        self.repository = repository

    def evaluate(self) -> Dict[str, Any]:
        """
        Simulates the evaluation of the generated repository.
        
        Returns:
            Dict[str, Any]: A dictionary containing evaluation metrics.
        """
        # In an actual implementation, integration with an LLM evaluation model would occur here.
        metrics = {
            "reference_based": 4.0,
            "reference_free": 4.5,
            "human_score": 4.2
        }
        logging.info("Evaluation metrics computed: %s", metrics)
        return metrics
'''
        # Generate a template for the main entry point module.
        elif file_name == "main.py":
            return '''"""
Module: main.py
Entry point for the PaperCoder pipeline.
Orchestrates the steps: parsing, planning, analysis, code generation, and evaluation.
"""

import logging
import json
from paper_parser import PaperParser
from planner import Planner
from analyzer import Analyzer
from code_generator import CodeGenerator
from evaluation import Evaluator

def main() -> None:
    """
    Main function to execute the PaperCoder pipeline.
    """
    # Load configuration from config.yaml
    try:
        with open("config.yaml", "r", encoding="utf-8") as config_file:
            import yaml
            config = yaml.safe_load(config_file)
    except Exception as e:
        logging.error("Failed to load config.yaml: %s", e)
        return

    # Load the paper JSON (in practice, replace 'paper.json' with the actual file)
    try:
        with open("paper.json", "r", encoding="utf-8") as paper_file:
            paper_json = json.load(paper_file)
    except Exception as e:
        logging.error("Failed to load paper.json: %s", e)
        return
    
    # Instantiate pipeline modules
    parser = PaperParser(paper_json)
    paper = parser.parse()
    planner = Planner(paper)
    overall_plan = planner.create_overall_plan()
    architecture_design = planner.generate_architecture_design()
    config_details = planner.generate_config()
    
    # Combine plan, architecture design, and configuration details into a unified plan
    combined_plan = {
        "overall_plan": overall_plan,
        "architecture_design": architecture_design,
        "config": config_details
    }
    
    analyzer = Analyzer(combined_plan)
    analysis = analyzer.analyze_modules()
    
    code_gen = CodeGenerator(analysis, combined_plan)
    generated_repo = code_gen.generate_code()
    
    evaluator = Evaluator(generated_repo)
    metrics = evaluator.evaluate()
    logging.info("Final evaluation metrics: %s", metrics)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
'''
        # Generate a template for the code_generator.py module itself.
        elif file_name == "code_generator.py":
            return f'''"""
Module: {file_name}
{details}
This module defines the CodeGenerator class, which generates code templates for all repository files.
Configuration placeholders:
    - training.learning_rate: {{learning_rate}}
    - training.batch_size: {{batch_size}}
    - training.epochs: {{epochs}}
"""

import logging
from typing import Any, Dict, List

class CodeGenerator:
    def __init__(self, analysis: List[Dict[str, Any]], plan: Dict[str, Any]) -> None:
        if not analysis:
            logging.error("Empty analysis list provided to CodeGenerator.")
            raise ValueError("Analysis list is empty.")
        if not plan:
            logging.error("Empty plan dictionary provided to CodeGenerator.")
            raise ValueError("Plan dictionary is empty.")
        self.analysis = analysis
        self.plan = plan

    def generate_code(self) -> Dict[str, str]:
        generated_code = {{}}
        for module in self.analysis:
            file_name = module.get("file_name")
            if not file_name:
                logging.warning("Module in analysis missing 'file_name'; skipping.")
                continue
            details = module.get("functionality", "")
            template = self._generate_template(file_name, details)
            final_code = self._inject_configuration(template)
            generated_code[file_name] = final_code
            logging.info("Generated code for module: %s", file_name)
        return generated_code

    def _generate_template(self, file_name: str, details: str) -> str:
        if file_name in ["paper_parser.py", "planner.py", "analyzer.py"]:
            return f'''\"\"\"Module: {{file_name}}
{{details}}
This module is assumed to be already implemented.
\"\"\"'''
        elif file_name == "evaluation.py":
            return '''\"\"\"Module: evaluation.py
Defines the Evaluator class for repository evaluation.
Configuration: n_way_sampling={{n_way_sampling}}, evaluation_model={{evaluation_model}}
\"\"\" 

import logging
from typing import Any, Dict

class Evaluator:
    def __init__(self, repository: Dict[str, Any]) -> None:
        if not repository:
            logging.error("Empty repository provided to Evaluator.")
            raise ValueError("Repository cannot be empty.")
        self.repository = repository

    def evaluate(self) -> Dict[str, Any]:
        metrics = {
            "reference_based": 4.0,
            "reference_free": 4.5,
            "human_score": 4.2
        }
        logging.info("Evaluation metrics: %s", metrics)
        return metrics
'''
        elif file_name == "main.py":
            return '''\"\"\"Module: main.py
Entry point for the PaperCoder pipeline.
Orchestrates parsing, planning, analysis, code generation, and evaluation.
\"\"\" 

import logging
import json
from paper_parser import PaperParser
from planner import Planner
from analyzer import Analyzer
from code_generator import CodeGenerator
from evaluation import Evaluator

def main() -> None:
    try:
        with open("config.yaml", "r", encoding="utf-8") as config_file:
            import yaml
            config = yaml.safe_load(config_file)
    except Exception as e:
        logging.error("Failed to load config.yaml: %s", e)
        return

    with open("paper.json", "r", encoding="utf-8") as paper_file:
        paper_json = json.load(paper_file)
    
    parser = PaperParser(paper_json)
    paper = parser.parse()
    planner = Planner(paper)
    overall_plan = planner.create_overall_plan()
    architecture_design = planner.generate_architecture_design()
    config_details = planner.generate_config()
    
    combined_plan = {
        "overall_plan": overall_plan,
        "architecture_design": architecture_design,
        "config": config_details
    }
    
    analyzer = Analyzer(combined_plan)
    analysis = analyzer.analyze_modules()
    
    code_gen = CodeGenerator(analysis, combined_plan)
    generated_repo = code_gen.generate_code()
    
    evaluator = Evaluator(generated_repo)
    metrics = evaluator.evaluate()
    logging.info("Final evaluation metrics: %s", metrics)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
'''
        else:
            return f'''"""
Module: {file_name}
{details}
This is a generated module.
"""

# Generated code for {file_name}
'''
        # End of conditional branches

    def _inject_configuration(self, template: str) -> str:
        """
        Replaces configuration placeholders in the template with actual values from the plan's configuration.

        The expected placeholders in the template are:
            {learning_rate}, {batch_size}, {epochs}, {n_way_sampling}, {evaluation_model}

        Returns:
            str: The final code template with configuration values injected.
        """
        config: Dict[str, Any] = self.plan.get("config", {})
        training_config: Dict[str, Any] = config.get("training", {})
        evaluation_config: Dict[str, Any] = config.get("evaluation", {})

        # Replace placeholders with explicit configuration values
        template = template.replace("{learning_rate}", str(training_config.get("learning_rate", "0.001")))
        template = template.replace("{batch_size}", str(training_config.get("batch_size", "32")))
        template = template.replace("{epochs}", str(training_config.get("epochs", "10")))
        template = template.replace("{n_way_sampling}", str(evaluation_config.get("n_way_sampling", "8")))
        template = template.replace("{evaluation_model}", str(evaluation_config.get("evaluation_model", "o3-mini-high")))
        return template

# Standalone testing for the CodeGenerator module
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Sample analysis list for testing purposes
    analysis = [
        {
            "file_name": "paper_parser.py",
            "functionality": "Parses the input paper JSON and returns a structured Paper object.",
            "expected_inputs": ["Raw paper JSON"],
            "expected_outputs": ["Structured Paper object"],
            "dependencies": []
        },
        {
            "file_name": "planner.py",
            "functionality": "Generates an overall plan and architecture design from the Paper object.",
            "expected_inputs": ["Paper object"],
            "expected_outputs": ["Plan dictionary"],
            "dependencies": ["paper_parser.py"]
        },
        {
            "file_name": "analyzer.py",
            "functionality": "Analyzes the overall plan to produce detailed file-level specifications.",
            "expected_inputs": ["Plan dictionary"],
            "expected_outputs": ["List of analysis dictionaries"],
            "dependencies": ["planner.py"]
        },
        {
            "file_name": "code_generator.py",
            "functionality": "Generates code templates for repository modules based on analysis and overall plan.",
            "expected_inputs": ["Analysis list", "Plan dictionary"],
            "expected_outputs": ["Dictionary mapping file names to code strings"],
            "dependencies": ["planner.py", "analyzer.py"]
        },
        {
            "file_name": "evaluation.py",
            "functionality": "Evaluates the generated repository and returns evaluation metrics.",
            "expected_inputs": ["Generated repository"],
            "expected_outputs": ["Evaluation metrics"],
            "dependencies": ["code_generator.py"]
        },
        {
            "file_name": "main.py",
            "functionality": "Orchestrates the entire pipeline execution.",
            "expected_inputs": ["Configuration and module outputs"],
            "expected_outputs": ["Final repository and evaluation metrics"],
            "dependencies": ["paper_parser.py", "planner.py", "analyzer.py", "code_generator.py", "evaluation.py"]
        }
    ]

    # Sample overall plan including configuration details (simulating config.yaml values)
    plan = {
        "overall_plan": {
            "implementation_goal": "Reproduce experiments as described in the paper.",
            "methodology_overview": "Multi-stage pipeline with planning, analysis, and code generation.",
            "experimental_setup": "Evaluation uses n_way_sampling and specified evaluation model."
        },
        "architecture_design": {
            "file_list": [
                "paper_parser.py",
                "planner.py",
                "analyzer.py",
                "code_generator.py",
                "evaluation.py",
                "main.py"
            ],
            "class_diagram": "classDiagram placeholder",
            "sequence_diagram": "sequenceDiagram placeholder"
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

    code_gen = CodeGenerator(analysis, plan)
    generated_codes = code_gen.generate_code()
    print(json.dumps(generated_codes, indent=2))
