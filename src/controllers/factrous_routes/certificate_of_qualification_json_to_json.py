import json
import logging
from typing import Any

logger = logging.getLogger("EXTRACT_CERTIFICATE_QUALIFICATION")


def extract_certificate_of_qualification(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    mapped_data: dict[str, Any] = {}

    for row in raw_data:
        mapped_data["CERTIFICATE_CLB_5_TO_6"] = row.get(
            "Points for certificate of qualification + CLB 5 or more on all first official language abilities, one or more under 7 (Maximum 25 points)",
            0
        )
        mapped_data["CERTIFICATE_CLB_7_OR_MORE"] = row.get(
            "Points for certificate of qualification + CLB 7 or more on all four first official language abilities (Maximum 50 points)",
            0
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapped_data, f, indent=2)

    logger.info("Certificate of qualification points extracted to: %s", output_path)
