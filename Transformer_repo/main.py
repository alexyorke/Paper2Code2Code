## main.py
"""
Module: main.py
Entry point for the PaperCoder pipeline.
Orchestrates the steps: paper parsing, planning, analysis, code generation, and evaluation.
This file strictly follows the provided design and configuration from config.yaml.
"""

import os
import sys
import json
import logging
import yaml

# Importing required modules as per the design.
from paper_parser import PaperParser
from planner import Planner
from analyzer import Analyzer
from code_generator import CodeGenerator
from evaluation import Evaluator

def load_configuration(config_path: str) -> dict:
    """
    Loads and validates configuration from config.yaml.
    Sets default values for missing keys.

    Args:
        config_path (str): Path to config.yaml file.

    Returns:
        dict: Configuration dictionary with training and evaluation settings.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
            if not config:
                logging.warning("Config file is empty. Using default configuration values.")
                config = {
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
            # Ensure required training keys exist.
            training_config = config.get("training", {})
            if "learning_rate" not in training_config:
                training_config["learning_rate"] = "0.001"
            if "batch_size" not in training_config:
                training_config["batch_size"] = "32"
            if "epochs" not in training_config:
                training_config["epochs"] = "10"
            config["training"] = training_config

            # Ensure required evaluation keys exist.
            evaluation_config = config.get("evaluation", {})
            if "n_way_sampling" not in evaluation_config:
                evaluation_config["n_way_sampling"] = 8
            if "evaluation_model" not in evaluation_config:
                evaluation_config["evaluation_model"] = "o3-mini-high"
            config["evaluation"] = evaluation_config

            return config
    except Exception as e:
        logging.error("Failed to load config file: %s", e)
        # Return default configuration if an error occurs.
        return {
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

def load_paper(paper_path: str) -> dict:
    """
    Loads the research paper JSON from the specified file path.

    Args:
        paper_path (str): Path to the paper JSON file.

    Returns:
        dict: Parsed JSON content of the paper.
    """
    try:
        with open(paper_path, "r", encoding="utf-8") as paper_file:
            paper_json = json.load(paper_file)
            return paper_json
    except Exception as e:
        logging.error("Failed to load paper JSON from %s: %s", paper_path, e)
        return {}

def run_pipeline() -> None:
    """
    Executes the full PaperCoder reproduction pipeline:
      1. Load configuration from config.yaml.
      2. Load and parse the paper JSON.
      3. Generate an overall plan and architecture design via Planner.
      4. Analyze the plan to produce file-level specifications using Analyzer.
      5. Generate code for each module using CodeGenerator.
      6. Evaluate the generated repository using Evaluator.
      7. Output the final evaluation metrics.
    """
    # Set up logging format.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 1. Configuration Initialization.
    config_file_path: str = os.path.join(os.path.dirname(__file__), "config.yaml")
    config: dict = load_configuration(config_file_path)
    logging.info("Configuration loaded successfully: %s", config)

    # 2. Input Paper Handling.
    paper_file_path: str = os.path.join(os.path.dirname(__file__), "paper.json")
    paper_json: dict = load_paper(paper_file_path)
    if not paper_json:
        logging.error("Paper JSON is empty or could not be loaded. Exiting pipeline.")
        sys.exit(1)
    logging.info("Paper JSON loaded successfully from %s", paper_file_path)

    # 3. Paper Parsing Stage.
    try:
        parser: PaperParser = PaperParser(paper_json)
        paper: dict = parser.parse()
        logging.info("Paper parsed successfully. Paper ID: %s, Title: %s",
                     paper.get("paper_id", "N/A"), paper.get("title", "N/A"))
    except Exception as e:
        logging.error("Error during paper parsing: %s", e)
        sys.exit(1)

    # 4. Planning Stage Execution.
    try:
        planner: Planner = Planner(paper)
        overall_plan: dict = planner.create_overall_plan()
        architecture_design: dict = planner.generate_architecture_design()
        config_details: dict = planner.generate_config()
        # Combine outputs into a comprehensive 'plan' dictionary.
        combined_plan: dict = {
            "overall_plan": overall_plan,
            "architecture_design": architecture_design,
            "config": config_details
        }
        logging.info("Planning stage completed successfully.")
    except Exception as e:
        logging.error("Error during planning stage: %s", e)
        sys.exit(1)

    # 5. Analysis Stage Execution.
    try:
        analyzer: Analyzer = Analyzer(combined_plan)
        analysis: list = analyzer.analyze_modules()
        if not analysis:
            logging.error("Analysis stage returned an empty analysis list.")
            sys.exit(1)
        logging.info("Analysis stage completed. Analyzed %d modules.", len(analysis))
    except Exception as e:
        logging.error("Error during analysis stage: %s", e)
        sys.exit(1)

    # 6. Code Generation Stage Execution.
    try:
        code_gen: CodeGenerator = CodeGenerator(analysis, combined_plan)
        generated_repo: dict = code_gen.generate_code()
        if not generated_repo:
            logging.error("Code generation failed; no repository files were generated.")
            sys.exit(1)
        logging.info("Code generation stage completed. Generated %d files.", len(generated_repo))
    except Exception as e:
        logging.error("Error during code generation stage: %s", e)
        sys.exit(1)

    # 7. Evaluation Stage Execution.
    try:
        evaluator: Evaluator = Evaluator(generated_repo, config)
        evaluation_metrics: dict = evaluator.evaluate()
        logging.info("Evaluation stage completed successfully. Metrics: %s", evaluation_metrics)
    except Exception as e:
        logging.error("Error during evaluation stage: %s", e)
        sys.exit(1)

    # 8. Output the Final Evaluation Metrics.
    print("Final Evaluation Metrics:")
    print(json.dumps(evaluation_metrics, indent=2))

if __name__ == "__main__":
    run_pipeline()
