from typing import Dict, List, Tuple

IELTS_BAND_TO_CLB: Dict[str, List[Tuple[float, int]]] = {
    "listening": [(4.5, 4), (5.0, 5), (5.5, 6), (6.0, 7), (6.5, 8), (7.0, 9), (8.0, 10)],
    "speaking": [(4.0, 4), (5.0, 5), (5.5, 6), (6.0, 7), (6.5, 8), (7.0, 9), (7.5, 10)],
    "reading": [(3.5, 4), (4.0, 5), (4.5, 6), (5.5, 7), (6.0, 8), (6.5, 9), (7.0, 10)],
    "writing": [(4.0, 4), (5.0, 5), (5.5, 6), (6.0, 7), (6.5, 8), (7.0, 9), (7.5, 10)],
}

CELPIP_TO_CLB: Dict[str, List[Tuple[int, int]]] = {
    "listening": [(5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10)],
    "speaking": [(5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10)],
    "reading": [(4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)],
    "writing": [(4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)],
}

TEF_TO_CLB: Dict[str, List[Tuple[int, int]]] = {
    "listening": [(146, 4), (159, 5), (167, 6), (176, 7), (186, 8), (193, 9), (207, 10)],
    "speaking": [(181, 4), (207, 5), (232, 6), (248, 7), (263, 8), (279, 9), (298, 10)],
    "reading": [(121, 4), (149, 5), (174, 6), (207, 7), (232, 8), (248, 9), (263, 10)],
    "writing": [(181, 4), (207, 5), (232, 6), (248, 7), (263, 8), (279, 9), (298, 10)],
}

TCF_TO_CLB: Dict[str, List[Tuple[int, int]]] = {
    "listening": [(181, 4), (207, 5), (232, 6), (248, 7), (263, 8), (279, 9), (298, 10)],
    "speaking": [(181, 4), (207, 5), (232, 6), (248, 7), (263, 8), (279, 9), (298, 10)],
    "reading": [(181, 4), (207, 5), (232, 6), (248, 7), (263, 8), (279, 9), (298, 10)],
    "writing": [(181, 4), (207, 5), (232, 6), (248, 7), (263, 8), (279, 9), (298, 10)],
}

# PTE mappings based on official ranges, using the min score of each CLB range
PTE_TO_CLB: Dict[str, List[Tuple[int, int]]] = {
    "reading": [(24, 3), (33, 4), (42, 5), (51, 6), (60, 7), (69, 8), (78, 9), (88, 10)],
    "writing": [(32, 3), (41, 4), (51, 5), (60, 6), (69, 7), (79, 8), (88, 9), (90, 10)],
    "listening": [(18, 3), (28, 4), (39, 5), (50, 6), (60, 7), (71, 8), (82, 9), (89, 10)],
    "speaking": [(34, 3), (42, 4), (51, 5), (59, 6), (68, 7), (76, 8), (84, 9), (89, 10)],
}

TEST_MAPPINGS = {
    "IELTS": IELTS_BAND_TO_CLB,
    "CELPIP": CELPIP_TO_CLB,
    "TEF": TEF_TO_CLB,
    "TCF": TCF_TO_CLB,
    "PTE": PTE_TO_CLB,
}

def convert_score_to_clb(test_name: str, ability: str, score: float) -> int:
    test_name = test_name.upper()
    ability = ability.lower()

    if test_name not in TEST_MAPPINGS:
        raise ValueError(f"Test '{test_name}' not supported")

    mapping = TEST_MAPPINGS[test_name]

    if ability not in mapping:
        raise ValueError(f"Ability '{ability}' not recognized for test '{test_name}'")

    thresholds = mapping[ability]

    clb = 0
    for min_score, clb_level in thresholds:
        if score >= min_score:
            clb = clb_level
        else:
            break

    return clb
