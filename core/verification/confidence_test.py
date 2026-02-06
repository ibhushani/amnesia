"""
Statistical confidence tests for unlearning verification
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from typing import Dict, Any, Tuple
import numpy as np
from scipy import stats

from utils import get_logger

log = get_logger(__name__)


class ConfidenceTest:
    """
    Statistical tests to verify unlearning effectiveness.
    
    Uses statistical hypothesis testing to determine if
    the model has truly "forgotten" the target data.
    """
    
    def __init__(
        self,
        model: nn.Module,
        device: torch.device = None,
        significance_level: float = 0.05,
    ):
        self.model = model
        self.device = device or torch.device("cpu")
        self.significance_level = significance_level
        self.model.to(self.device)
    
    def get_confidence_distribution(
        self,
        dataloader: DataLoader,
    ) -> np.ndarray:
        """Get confidence values for all samples"""
        self.model.eval()
        confidences = []
        
        with torch.no_grad():
            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                logits = self.model(batch_x)
                probs = F.softmax(logits, dim=1)
                correct_probs = probs.gather(1, batch_y.view(-1, 1)).squeeze()
                confidences.extend(correct_probs.cpu().numpy())
        
        return np.array(confidences)
    
    def t_test_against_random(
        self,
        forget_confidences: np.ndarray,
        num_classes: int,
    ) -> Dict[str, Any]:
        """
        One-sample t-test: Is confidence significantly different from random (1/num_classes)?
        
        H0: Mean confidence = 1/num_classes (model is guessing randomly)
        H1: Mean confidence ≠ 1/num_classes
        
        For successful unlearning, we want to FAIL to reject H0
        (confidence should be near random).
        """
        random_baseline = 1.0 / num_classes
        
        t_stat, p_value = stats.ttest_1samp(forget_confidences, random_baseline)
        
        result = {
            "test_type": "one_sample_t_test",
            "null_hypothesis": f"mean_confidence = {random_baseline:.4f} (random guessing)",
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "mean_confidence": float(np.mean(forget_confidences)),
            "random_baseline": random_baseline,
            "conclusion": "random" if p_value > self.significance_level else "not_random",
            "unlearning_success": p_value > self.significance_level,
        }
        
        return result
    
    def compare_distributions(
        self,
        forget_confidences: np.ndarray,
        never_seen_confidences: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Two-sample test: Are forget set confidences similar to never-seen data?
        
        If unlearning is successful, the model should treat forgotten data
        the same as data it never saw.
        """
        # Mann-Whitney U test (non-parametric)
        u_stat, p_value = stats.mannwhitneyu(
            forget_confidences,
            never_seen_confidences,
            alternative='two-sided'
        )
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.ks_2samp(forget_confidences, never_seen_confidences)
        
        result = {
            "test_type": "distribution_comparison",
            "mann_whitney_u": float(u_stat),
            "mann_whitney_p": float(p_value),
            "ks_statistic": float(ks_stat),
            "ks_p_value": float(ks_p),
            "forget_mean": float(np.mean(forget_confidences)),
            "never_seen_mean": float(np.mean(never_seen_confidences)),
            "distributions_similar": p_value > self.significance_level,
        }
        
        return result
    
    def full_verification(
        self,
        forget_loader: DataLoader,
        retain_loader: DataLoader,
        num_classes: int,
    ) -> Dict[str, Any]:
        """
        Complete verification suite.
        
        Returns comprehensive test results.
        """
        log.info("Running full verification suite...")
        
        forget_conf = self.get_confidence_distribution(forget_loader)
        retain_conf = self.get_confidence_distribution(retain_loader)
        
        # Test 1: Is forget set near random?
        random_test = self.t_test_against_random(forget_conf, num_classes)
        
        # Test 2: Is retain set still confident?
        retain_test = self.t_test_against_random(retain_conf, num_classes)
        
        # Summary statistics
        results = {
            "forget_set": {
                "mean_confidence": float(np.mean(forget_conf)),
                "std_confidence": float(np.std(forget_conf)),
                "near_random": random_test["unlearning_success"],
            },
            "retain_set": {
                "mean_confidence": float(np.mean(retain_conf)),
                "std_confidence": float(np.std(retain_conf)),
                "still_confident": not retain_test["unlearning_success"],
            },
            "tests": {
                "forget_random_test": random_test,
                "retain_confidence_test": retain_test,
            },
            "overall_success": (
                random_test["unlearning_success"] and 
                not retain_test["unlearning_success"]
            ),
        }
        
        log.info(f"Verification complete. Overall success: {results['overall_success']}")
        
        return results