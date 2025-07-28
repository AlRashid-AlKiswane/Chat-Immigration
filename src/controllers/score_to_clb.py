from typing import Dict, List, Tuple, Literal, Union

# Define types
LanguageTestType = Literal["listening", "speaking", "reading", "writing"]
ScoreThreshold = Union[float, int, Tuple[int, int]]
TestConversionTable = Dict[LanguageTestType, List[Tuple[ScoreThreshold, int]]]

# IELTS to CLB conversion
IELTS_TO_CLB: TestConversionTable = {
    "listening": [
        (4.0, 4), (4.5, 5), (5.0, 6), (6.0, 7),
        (7.5, 8), (8.0, 9), (8.5, 10)
    ],
    "speaking": [
        (4.0, 4), (5.0, 5), (5.5, 6), (6.0, 7),
        (6.5, 8), (7.0, 9), (7.5, 10)
    ],
   "reading": [
    (3.5, 4), (4.0, 5), (5.0, 6), (6.0, 7),
    (6.5, 8), (7.0, 9), (8.0, 10)
        ],
    "writing": [
        (4.0, 4), (5.0, 5), (5.5, 6), (6.0, 7),
        (6.5, 8), (7.0, 9), (7.5, 10)
    ]
}

# CELPIP to CLB conversion (1:1 mapping)
CELPIP_TO_CLB: TestConversionTable = {
    "listening": [(k, k) for k in range(4, 11)],
    "speaking": [(k, k) for k in range(4, 11)],
    "reading": [(k, k) for k in range(4, 11)],
    "writing": [(k, k) for k in range(4, 11)]
}

# TEF Canada to NCLC conversion
TEF_TO_NCLC: TestConversionTable = {
    "reading": [
        (549, 10), (524, 9), (499, 8), (453, 7),
        (406, 6), (375, 5), (342, 4)
    ],
    "writing": [
        (20, 10), (19, 10), (18, 10), (17, 10), (16, 10),
        (15, 9), (14, 9),
        (13, 8), (12, 8),
        (11, 7), (10, 7),
        (9, 6), (8, 6), (7, 6),
        (6, 5),
        (5, 4), (4, 4)
    ],
    "listening": [
        (549, 10), (523, 9), (503, 8), (458, 7),
        (398, 6), (369, 5), (331, 4)
    ],
    "speaking": [
        (20, 10), (19, 10), (18, 10), (17, 10), (16, 10),
        (15, 9), (14, 9),
        (13, 8), (12, 8),
        (11, 7), (10, 7),
        (9, 6), (8, 6), (7, 6),
        (6, 5),
        (5, 4), (4, 4)
    ]
}

# TCF Canada to CLB conversion
TCF_TO_CLB: TestConversionTable = {
    "reading": [
        ((88, 90), 10), ((78, 87), 9), ((69, 77), 8),
        ((60, 68), 7), ((51, 59), 6), ((42, 50), 5),
        ((33, 41), 4), ((24, 32), 3)
    ],
    "writing": [
        ((90, 90), 10), ((88, 89), 9), ((79, 87), 8),
        ((69, 78), 7), ((60, 68), 6), ((51, 59), 5),
        ((41, 50), 4), ((32, 40), 3)
    ],
    "listening": [
        ((89, 90), 10), ((82, 88), 9), ((71, 81), 8),
        ((60, 70), 7), ((50, 59), 6), ((39, 49), 5),
        ((28, 38), 4), ((18, 27), 3)
    ],
    "speaking": [
        ((89, 90), 10), ((84, 88), 9), ((76, 83), 8),
        ((68, 75), 7), ((59, 67), 6), ((51, 58), 5),
        ((42, 50), 4), ((34, 41), 3)
    ]
}

TEST_MAPPINGS = {
    "IELTS": IELTS_TO_CLB,
    "CELPIP": CELPIP_TO_CLB,
    "TEF": TEF_TO_NCLC,
    "TCF": TCF_TO_CLB
}

def convert_score_to_clb(
    test_name: str,
    ability: str,
    score: Union[float, int, Tuple[int, int]]
) -> int:
    """
    Convert language test score to CLB/NCLC level.
    
    Args:
        test_name: One of 'IELTS', 'CELPIP', 'TEF', 'TCF'
        ability: Language skill being tested ('listening', 'speaking', 'reading', 'writing')
        score: Test score (format varies by test)
        
    Returns:
        CLB/NCLC level (3-10)
        
    Raises:
        ValueError: For invalid test names, abilities, or score ranges
    """
    test_name = test_name.upper()
    ability_lower = ability.lower()
    
    # Validate test name
    if test_name not in TEST_MAPPINGS:
        raise ValueError(
            f"Unsupported test '{test_name}'. "
            f"Supported tests: {list(TEST_MAPPINGS.keys())}"
        )
    
    # Validate ability
    valid_abilities = ["listening", "speaking", "reading", "writing"]
    if ability_lower not in valid_abilities:
        raise ValueError(
            f"Invalid ability '{ability}'. "
            f"Must be one of {valid_abilities}"
        )
    
    mapping = TEST_MAPPINGS[test_name]
    thresholds = mapping[ability_lower]  # type: ignore
    min_level = 3  # Minimum CLB level
    
    for threshold, clb_level in sorted(
        thresholds,
        key=lambda x: x[0] if not isinstance(x[0], tuple) else x[0][0],
        reverse=True
    ):
        if isinstance(threshold, tuple):
            # Handle range-based thresholds (TCF)
            if isinstance(score, tuple):
                if threshold[0] <= score[0] <= threshold[1]:
                    return clb_level
            else:
                if threshold[0] <= score <= threshold[1]:
                    return clb_level
        else:
            # Handle minimum threshold (IELTS/CELPIP/TEF)
            if not isinstance(score, tuple) and score >= threshold:
                return clb_level
                
    return min_level