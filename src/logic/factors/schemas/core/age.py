import re
import logging
from typing import List, Dict, Any, Type, TypeVar
from pydantic import BaseModel, Field
import jdon
T = TypeVar("T", bound=BaseModel)


try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("[Startup] Failed to set up main directory path: %s", e)
    sys.exit(1)

class AgeWithoutSpouseFactors(BaseModel):
    """
    Age points calculation for applicants without a spouse or common-law partner.
    Maximum 110 points.
    """
    age_17_or_less: int = Field(0, description="17 years of age or less")
    age_18: int = Field(99, description="18 years of age")
    age_19: int = Field(105, description="19 years of age")
    age_20_to_29: int = Field(110, description="20 to 29 years of age")
    age_30: int = Field(105, description="30 years of age")
    age_31: int = Field(99, description="31 years of age")
    age_32: int = Field(94, description="32 years of age")
    age_33: int = Field(88, description="33 years of age")
    age_34: int = Field(83, description="34 years of age")
    age_35: int = Field(77, description="35 years of age")
    age_36: int = Field(72, description="36 years of age")
    age_37: int = Field(66, description="37 years of age")
    age_38: int = Field(61, description="38 years of age")
    age_39: int = Field(55, description="39 years of age")
    age_40: int = Field(50, description="40 years of age")
    age_41: int = Field(39, description="41 years of age")
    age_42: int = Field(28, description="42 years of age")
    age_43: int = Field(17, description="43 years of age")
    age_44: int = Field(6, description="44 years of age")
    age_45_or_more: int = Field(0, description="45 years of age or more")


class AgeWithSpouseFactors(BaseModel):
    """
    Age points calculation for applicants with a spouse or common-law partner.
    Maximum 100 points.
    """
    age_17_or_less: int = Field(0, description="17 years of age or less")
    age_18: int = Field(90, description="18 years of age")
    age_19: int = Field(95, description="19 years of age")
    age_20_to_29: int = Field(100, description="20 to 29 years of age")
    age_30: int = Field(95, description="30 years of age")
    age_31: int = Field(90, description="31 years of age")
    age_32: int = Field(85, description="32 years of age")
    age_33: int = Field(80, description="33 years of age")
    age_34: int = Field(75, description="34 years of age")
    age_35: int = Field(70, description="35 years of age")
    age_36: int = Field(65, description="36 years of age")
    age_37: int = Field(60, description="37 years of age")
    age_38: int = Field(55, description="38 years of age")
    age_39: int = Field(50, description="39 years of age")
    age_40: int = Field(45, description="40 years of age")
    age_41: int = Field(35, description="41 years of age")
    age_42: int = Field(25, description="42 years of age")
    age_43: int = Field(15, description="43 years of age")
    age_44: int = Field(5, description="44 years of age")
    age_45_or_more: int = Field(0, description="45 years of age or more")


def normalize_label_to_field(label: str) -> str:
    """
    Convert human-readable age label into a Pydantic-compatible field name.
    """
    label = label.lower().strip()

    if "or more" in label:
        return "age_45_or_more"
    elif "or less" in label:
        return "age_17_or_less"

    label = label.replace("years of age", "").strip()
    label = label.replace("to", "_to_").replace(" ", "_").replace("-", "_")
    label = re.sub(r"__+", "_", label)
    return f"age_{label.strip('_')}"


def load_age_model(
    data: List[Dict[str, Any]],
    value_key: str,
    model_cls: Type[T]
) -> T:
    """
    Load a list of age factor entries into a specified Pydantic model.

    Args:
        data (List[Dict[str, Any]]): List of dicts with "label" and score key.
        value_key (str): Key to extract score (e.g., "points_with_spouse").
        model_cls (Type[T]): Pydantic model class to instantiate.

    Returns:
        T: An instance of the given model.
    """
    mapped = {}
    for item in data:
        label = item.get("label", "")
        value = item.get(value_key, 0)
        field_name = normalize_label_to_field(label)
        mapped[field_name] = value

    return model_cls(**mapped)


# Assuming these are your JSON paths
RULES_DIR = Path("/workspaces/Chat-Immigration/assets/rules_json")

AGE_WITH_SPOUSE_FILE = RULES_DIR / "AgeWithSpouseFactors.json"
AGE_WITHOUT_SPOUSE_FILE = RULES_DIR / "AgeWithoutSpouseFactors.json"

def load_json(path: Path) -> list[dict]:
    """
    Load JSON file from path and return as list of dicts.
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

# Load both datasets from disk
data_with_spouse = load_json(AGE_WITH_SPOUSE_FILE)
data_without_spouse = load_json(AGE_WITHOUT_SPOUSE_FILE)

# Convert to Pydantic models
with_spouse_model = load_age_model(data_with_spouse, "points_with_spouse", AgeWithSpouseFactors)
without_spouse_model = load_age_model(data_without_spouse, "points_without_spouse", AgeWithoutSpouseFactors)

# ✅ Use the models
print(with_spouse_model.age_32)        # 85
print(without_spouse_model.age_32)     # 94