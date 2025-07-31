from typing import Dict, List, Tuple, Literal, Union

# Define types
LanguageTestType = Literal["listening", "speaking", "reading", "writing"]
ScoreThreshold = Union[float, int, Tuple[int, int]]
TestConversionTable = Dict[LanguageTestType, List[Tuple[ScoreThreshold, int]]]

# IELTS (General Training) to CLB conversion
IELTS_TO_CLB: TestConversionTable = {
    "reading": [
        (8.0, 10), (7.0, 9), (6.5, 8), (6.0, 7),
        (5.0, 6), (4.0, 5), (3.5, 4)
    ],
    "writing": [
        (7.5, 10), (7.0, 9), (6.5, 8), (6.0, 7),
        (5.5, 6), (5.0, 5), (4.0, 4)
    ],
    "listening": [
        (8.5, 10), (8.0, 9), (7.5, 8), (6.0, 7),
        (5.5, 6), (5.0, 5), (4.5, 4)
    ],
    "speaking": [
        (7.5, 10), (7.0, 9), (6.5, 8), (6.0, 7),
        (5.5, 6), (5.0, 5), (4.0, 4)
    ]
}

# CELPIP (General) to CLB conversion (1:1 mapping)
CELPIP_TO_CLB: TestConversionTable = {
    "reading": [(k, k) for k in range(10, 3, -1)],
    "writing": [(k, k) for k in range(10, 3, -1)],
    "listening": [(k, k) for k in range(10, 3, -1)],
    "speaking": [(k, k) for k in range(10, 3, -1)]
}

# PTE Core to CLB conversion
PTE_TO_CLB: TestConversionTable = {
    "reading": [
        ((88, 90), 10), ((78, 87), 9), ((69, 77), 8), ((60, 68), 7),
        ((51, 59), 6), ((42, 50), 5), ((33, 41), 4), ((24, 32), 3)
    ],
    "writing": [
        ((90, 90), 10), ((88, 89), 9), ((79, 87), 8), ((69, 78), 7),
        ((60, 68), 6), ((51, 59), 5), ((41, 50), 4), ((32, 40), 3)
    ],
    "listening": [
        ((89, 90), 10), ((82, 88), 9), ((71, 81), 8), ((60, 70), 7),
        ((50, 59), 6), ((39, 49), 5), ((28, 38), 4), ((18, 27), 3)
    ],
    "speaking": [
        ((89, 90), 10), ((84, 88), 9), ((76, 83), 8), ((68, 75), 7),
        ((59, 67), 6), ((51, 58), 5), ((42, 50), 4), ((34, 41), 3)
    ]
}

# TEF Canada to NCLC conversion (After Dec 10, 2023)
TEF_TO_NCLC_NEW: TestConversionTable = {
    "reading": [
        ((546, 699), 10), ((503, 545), 9), ((462, 502), 8), ((434, 461), 7),
        ((393, 433), 6), ((352, 392), 5), ((306, 351), 4)
    ],
    "writing": [
        ((558, 699), 10), ((512, 557), 9), ((472, 511), 8), ((428, 471), 7),
        ((379, 427), 6), ((330, 378), 5), ((268, 329), 4)
    ],
    "listening": [
        ((546, 699), 10), ((503, 545), 9), ((462, 502), 8), ((434, 461), 7),
        ((393, 433), 6), ((352, 392), 5), ((306, 351), 4)
    ],
    "speaking": [
        ((556, 699), 10), ((518, 555), 9), ((494, 517), 8), ((456, 493), 7),
        ((422, 455), 6), ((387, 421), 5), ((328, 386), 4)
    ]
}

# TEF Canada to NCLC conversion (Oct 1, 2019 - Dec 10, 2023)
TEF_TO_NCLC_OLD: TestConversionTable = {
    "reading": [
        ((566, 699), 10), ((533, 565), 9), ((500, 532), 8), ((450, 499), 7),
        ((400, 449), 6), ((350, 399), 5), ((300, 349), 4)
    ],
    "writing": [
        ((566, 699), 10), ((533, 565), 9), ((500, 532), 8), ((450, 499), 7),
        ((400, 449), 6), ((350, 399), 5), ((300, 349), 4)
    ],
    "listening": [
        ((566, 699), 10), ((533, 565), 9), ((500, 532), 8), ((450, 499), 7),
        ((400, 449), 6), ((350, 399), 5), ((300, 349), 4)
    ],
    "speaking": [
        ((566, 699), 10), ((533, 565), 9), ((500, 532), 8), ((450, 499), 7),
        ((400, 449), 6), ((350, 399), 5), ((300, 349), 4)
    ]
}

# TCF Canada to NCLC conversion
TCF_TO_NCLC: TestConversionTable = {
    "reading": [
        ((549, 699), 10), ((524, 548), 9), ((499, 523), 8), ((453, 498), 7),
        ((406, 452), 6), ((375, 405), 5), ((342, 374), 4)
    ],
    "writing": [
        ((16, 20), 10), ((14, 15), 9), ((12, 13), 8), ((10, 11), 7),
        ((7, 9), 6), ((6, 6), 5), ((4, 5), 4)
    ],
    "listening": [
        ((549, 699), 10), ((523, 548), 9), ((503, 522), 8), ((458, 502), 7),
        ((398, 457), 6), ((369, 397), 5), ((331, 368), 4)
    ],
    "speaking": [
        ((16, 20), 10), ((14, 15), 9), ((12, 13), 8), ((10, 11), 7),
        ((7, 9), 6), ((6, 6), 5), ((4, 5), 4)
    ]
}

TEST_MAPPINGS = {
    "IELTS": IELTS_TO_CLB,
    "CELPIP": CELPIP_TO_CLB,
    "PTE": PTE_TO_CLB,
    "TEF_NEW": TEF_TO_NCLC_NEW,
    "TEF_OLD": TEF_TO_NCLC_OLD,
    "TCF": TCF_TO_NCLC
}

def convert_score_to_clb(
    test_name: str,
    ability: str,
    score: Union[float, int],
    test_date: str = "new"
) -> int:
    """
    Convert language test score to CLB/NCLC level.
    
    Args:
        test_name: One of 'IELTS', 'CELPIP', 'PTE', 'TEF', 'TCF'
        ability: Language skill ('listening', 'speaking', 'reading', 'writing')
        score: Test score
        test_date: For TEF tests, use 'new' (after Dec 10, 2023) or 'old' (Oct 2019 - Dec 2023)
        
    Returns:
        CLB/NCLC level (3-10)
    """
    test_name = test_name.upper()
    ability = ability.lower()
    
    # Handle TEF date variants
    if test_name == "TEF":
        test_key = "TEF_NEW" if test_date.lower() == "new" else "TEF_OLD"
    else:
        test_key = test_name
    
    if test_key not in TEST_MAPPINGS:
        raise ValueError(f"Unsupported test '{test_name}'. Supported: IELTS, CELPIP, PTE, TEF, TCF")
    
    if ability not in ["listening", "speaking", "reading", "writing"]:
        raise ValueError(f"Invalid ability '{ability}'. Must be: listening, speaking, reading, writing")
    
    mapping = TEST_MAPPINGS[test_key][ability] # type: ignore
    
    # Check each threshold from highest to lowest level
    for threshold, clb_level in mapping:
        if isinstance(threshold, tuple):
            # Range-based threshold (PTE, TEF, TCF)
            min_score, max_score = threshold
            if min_score <= score <= max_score:
                return clb_level
        else:
            # Minimum threshold (IELTS, CELPIP)
            if score >= threshold:
                return clb_level
    
    return 3  # Minimum level if no match found

def get_score_range_for_level(test_name: str, ability: str, clb_level: int, test_date: str = "new") -> Union[Tuple[float, float], Tuple[int, int], float, int]:
    """
    Get the score range or minimum score needed for a specific CLB/NCLC level.
    
    Args:
        test_name: Test name
        ability: Language skill
        clb_level: Target CLB/NCLC level (3-10)
        test_date: For TEF tests, 'new' or 'old'
        
    Returns:
        Score range (tuple) or minimum score (number)
    """
    test_name = test_name.upper()
    ability = ability.lower()
    
    if test_name == "TEF":
        test_key = "TEF_NEW" if test_date.lower() == "new" else "TEF_OLD"
    else:
        test_key = test_name
    
    if test_key not in TEST_MAPPINGS:
        raise ValueError(f"Unsupported test '{test_name}'")
    
    mapping = TEST_MAPPINGS[test_key][ability] # type: ignore
    
    for threshold, level in mapping:
        if level == clb_level:
            return threshold
    
    raise ValueError(f"CLB level {clb_level} not found for {test_name} {ability}")

def is_score_sufficient(test_name: str, ability: str, score: Union[float, int], 
                       required_clb: int, test_date: str = "new") -> bool:
    """Check if a score meets the required CLB/NCLC level."""
    achieved_clb = convert_score_to_clb(test_name, ability, score, test_date)
    return achieved_clb >= required_clb

# Example usage
if __name__ == "__main__":
    # Test conversions
    print(f"IELTS Reading 7.0 = CLB {convert_score_to_clb('IELTS', 'reading', 7.0)}")
    print(f"CELPIP Speaking 8 = CLB {convert_score_to_clb('CELPIP', 'speaking', 8)}")
    print(f"PTE Reading 75 = CLB {convert_score_to_clb('PTE', 'reading', 75)}")
    print(f"TEF Reading 500 (new) = NCLC {convert_score_to_clb('TEF', 'reading', 500, 'new')}")
    print(f"TCF Writing 12 = NCLC {convert_score_to_clb('TCF', 'writing', 12)}")
    
    # Get score ranges
    ielts_range = get_score_range_for_level('IELTS', 'reading', 7)
    print(f"IELTS Reading CLB 7 requires minimum: {ielts_range}")
    
    pte_range = get_score_range_for_level('PTE', 'listening', 8)
    print(f"PTE Listening CLB 8 range: {pte_range}")
    
    # Check if score is sufficient
    sufficient = is_score_sufficient('IELTS', 'writing', 6.5, 8)
    print(f"IELTS Writing 6.5 sufficient for CLB 8: {sufficient}")