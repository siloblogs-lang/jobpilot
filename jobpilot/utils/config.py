import os, yaml
from dotenv import load_dotenv

def _read_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def load_configs(profile_path="configs/profile.yaml", searches_path="configs/searches.yaml") -> dict:
    load_dotenv(override=False)
    cfg = {}
    cfg["env"] = {
        "DICE_EMAIL": os.getenv("DICE_EMAIL"),
        "DICE_PASSWORD": os.getenv("DICE_PASSWORD"),
        "GOOGLE_SA_JSON": os.getenv("GOOGLE_SA_JSON"),
        "SHEETS_SPREADSHEET_NAME": os.getenv("SHEETS_SPREADSHEET_NAME", "JobPilot"),
    }
    cfg["profile"]  = _read_yaml(profile_path).get("profile", {})
    cfg.update(_read_yaml(searches_path))   # adds `dice:` block, etc.
    return cfg
