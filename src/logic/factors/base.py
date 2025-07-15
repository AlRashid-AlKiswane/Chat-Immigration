"""
Base class for Comprehensive Ranking System (CRS) Factors implementation.

This abstract base class defines the common interface for all CRS factor calculators.
Concrete subclasses should implement specific scoring logic for each CRS factor.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class CRSFactor(ABC):
    """Abstract base class for CRS factor calculation.
    
    Attributes:
        rules (Dict): A dictionary containing the scoring rules and thresholds 
                     for this specific CRS factor.
    """
    
    def __init__(self, rules: Dict[str, Any]) -> None:
        """Initialize the CRS factor with its scoring rules.
        
        Args:
            rules: A dictionary containing all configuration and rules needed
                  to calculate scores for this factor. The structure is 
                  factor-specific.
        """
        self.rules = rules
    
    @abstractmethod
    def score(self, **kwargs) -> int:
        """Calculate the score for this CRS factor.
        
        This must be implemented by each concrete factor class with its specific
        scoring logic.
        
        Args:
            **kwargs: Factor-specific parameters needed for score calculation.
            
        Returns:
            int: The calculated score for this factor.
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method.
        """
        raise NotImplementedError("Each factor must implement its own scoring logic")