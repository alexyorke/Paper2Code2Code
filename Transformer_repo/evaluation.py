## evaluation.py
"""
Module: evaluation.py
Defines the Evaluator class for repository evaluation.
This module provides a comprehensive assessment of the generated repository using both reference-based and reference-free evaluation methods.
It uses configuration parameters loaded from config.yaml (such as n_way_sampling and evaluation_model) to conduct n-way sampling evaluations.
The Evaluator computes summary statistics (file count, total tokens, and function count) and simulates external LLM integration for scoring.
"""

import os
import re
import logging
import yaml
import json
from typing import Any, Dict, List

class Evaluator:
    """
    Evaluator class:
    Provides evaluation of the generated repository using both reference-based and reference-free methods.
    It uses configuration from config.yaml to obtain evaluation parameters such as n_way_sampling and evaluation_model.
    """

    def __init__(self, repository: Dict[str, Any], config: Dict[str, Any] = None) -> None:
        """
        Initializes the Evaluator with the generated repository and configuration.

        Args:
            repository (Dict[str, Any]): Dictionary representing the generated repository files (filename: code string).
            config (Dict[str, Any], optional): Configuration dictionary loaded from config.yaml containing evaluation parameters.
                                               If not provided, the configuration is loaded from the local config.yaml file.
        
        Raises:
            ValueError: If the repository is empty.
        """
        if not repository:
            logging.error("The repository provided for evaluation is empty.")
            raise ValueError("Repository cannot be empty.")
        self.repository = repository

        # Load configuration if not provided.
        if config is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = yaml.safe_load(f)
                    if not loaded_config:
                        logging.error("Configuration file config.yaml is empty.")
                        loaded_config = {}
            except Exception as e:
                logging.error("Failed to load config.yaml: %s", e)
                loaded_config = {}
            config = loaded_config

        self.config = config

        # Extract evaluation settings with defaults.
        evaluation_config: Dict[str, Any] = self.config.get("evaluation", {})
        self.n_way_sampling: int = evaluation_config.get("n_way_sampling", 8)
        self.evaluation_model: str = evaluation_config.get("evaluation_model", "o3-mini-high")
        logging.info("Evaluator initialized with n_way_sampling: %d, evaluation_model: %s",
                     self.n_way_sampling, self.evaluation_model)

    def _compute_summary_statistics(self) -> Dict[str, Any]:
        """
        Computes summary statistics for the repository including:
          - file_count: number of files in the repository.
          - total_tokens: estimated total token count based on whitespace tokenization.
          - function_count: total number of function definitions (approximated by counting 'def' occurrences).

        Returns:
            Dict[str, Any]: A dictionary containing summary statistics.
        """
        file_count: int = len(self.repository)
        total_tokens: int = 0
        function_count: int = 0

        for file_name, code in self.repository.items():
            tokens: List[str] = code.split()
            total_tokens += len(tokens)
            # Count occurrences of 'def' as an approximation for number of functions
            function_count += len(re.findall(r'\bdef\b', code))
        
        stats: Dict[str, Any] = {
            "file_count": file_count,
            "total_tokens": total_tokens,
            "function_count": function_count
        }
        logging.info("Repository Summary Statistics: %s", stats)
        return stats

    def _simulate_llm_evaluation(self, prompt: str) -> float:
        """
        Simulates an LLM evaluation call by returning a fixed score.
        In a real implementation, this method would interface with an external LLM (e.g., GPT-4) using a library like Hugging Face Transformers.

        Args:
            prompt (str): The prompt sent to the evaluation model.

        Returns:
            float: A simulated evaluation score on a scale from 1 (worst) to 5 (best).
        """
        # For simulation purposes, if the prompt mentions gold-standard evaluation, return 4.0; otherwise, return 4.5.
        if "gold-standard" in prompt.lower():
            score = 4.0
        else:
            score = 4.5
        logging.debug("Simulated LLM evaluation for prompt: '%s' returned score: %f", prompt, score)
        return score

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluates the generated repository using both reference-based and reference-free methods.
        The evaluation process performs n-way sampling (as specified in config.yaml) for stability and averages the scores.
        
        Workflow:
          a. Preprocessing: Computes summary statistics of the repository.
          b. Reference-Based Evaluation: If a gold-standard repository is available in the repository dictionary (key 'gold_standard'),
             constructs a prompt for comparison and simulates evaluation.
          c. Reference-Free Evaluation: Constructs a prompt based solely on the repository and paper description.
          d. Aggregation: Computes average scores and aggregates summary statistics.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - reference_based_score (float or None)
                - reference_free_score (float)
                - human_score (float, simulated)
                - summary_statistics (dict)
                - evaluation_model (str)
                - n_way_sampling (int)
        """
        summary_stats: Dict[str, Any] = self._compute_summary_statistics()

        ref_based_scores: List[float] = []
        ref_free_scores: List[float] = []

        # Determine if a gold-standard repository is present for reference-based evaluation.
        has_gold_standard: bool = "gold_standard" in self.repository

        if has_gold_standard:
            prompt_ref = ("Evaluate the generated repository against the gold-standard repository. "
                          "Assess the coverage and correctness of the required components on a scale of 1 to 5.")
        else:
            prompt_ref = "No gold-standard available."

        prompt_free = ("Evaluate the generated repository based solely on the experimental methods described in the paper. "
                       "Provide a correctness score on a scale of 1 to 5.")

        # Run n-way sampling evaluations.
        for _ in range(self.n_way_sampling):
            if has_gold_standard:
                score_ref: float = self._simulate_llm_evaluation(prompt_ref)
                ref_based_scores.append(score_ref)
            score_free: float = self._simulate_llm_evaluation(prompt_free)
            ref_free_scores.append(score_free)

        # Average the scores from the n-way sampling.
        reference_based_score: float = round(sum(ref_based_scores) / len(ref_based_scores), 2) \
            if has_gold_standard and ref_based_scores else None
        reference_free_score: float = round(sum(ref_free_scores) / len(ref_free_scores), 2) if ref_free_scores else None

        # Simulate a human evaluation score (as reported in the paper, e.g., 4.2 out of 5).
        human_score: float = 4.2

        aggregated_metrics: Dict[str, Any] = {
            "reference_based_score": reference_based_score,
            "reference_free_score": reference_free_score,
            "human_score": human_score,
            "summary_statistics": summary_stats,
            "evaluation_model": self.evaluation_model,
            "n_way_sampling": self.n_way_sampling
        }
        logging.info("Aggregated Evaluation Metrics: %s", aggregated_metrics)
        return aggregated_metrics

# Standalone testing for Evaluator module
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Create a sample generated repository.
    sample_repository: Dict[str, Any] = {
        "main.py": "def main():\n    print('Hello World')\n",
        "paper_parser.py": "def parse():\n    return {}\n",
        "planner.py": "def plan():\n    return {}\n",
        "analyzer.py": "def analyze():\n    return []\n",
        "code_generator.py": "def generate():\n    return {}\n",
        "evaluation.py": "def evaluate():\n    return {}\n"
        # Uncomment the next line to simulate presence of a gold-standard repository.
        # "gold_standard": "Official repository code content..."
    }

    # Simulate loading configuration from config.yaml via a sample configuration.
    sample_config: Dict[str, Any] = {
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

    evaluator = Evaluator(sample_repository, sample_config)
    results: Dict[str, Any] = evaluator.evaluate()
    print(json.dumps(results, indent=2))
