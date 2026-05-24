import hashlib
import json
import os
import random
from datetime import datetime

HISTORY_FILENAME = "session_history.json"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"
EXCLUDED_SUBJECT_IDS = frozenset({"session_history", "tickets", "test_question_bank"})


def history_path(data_dir):
    return os.path.join(data_dir, HISTORY_FILENAME)


def load_history(data_dir):
    path = history_path(data_dir)
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    return data if isinstance(data, list) else []


def save_history(data_dir, entries):
    path = history_path(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(entries, file, ensure_ascii=False, indent=2)


def calculate_bank_fingerprint(data_dir, subject_id):
    bank_path = os.path.join(data_dir, f"{subject_id}.json")
    with open(bank_path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()[:16]


def make_seed():
    return f"{random.randint(0, 999999):06d}"


def build_history_entry(
    *,
    subject,
    topics,
    recipe,
    tickets_count,
    total_points,
    bank_fingerprint,
    seed,
    created_at=None,
):
    return {
        "created_at": created_at or datetime.now().strftime(TIMESTAMP_FORMAT),
        "seed": seed,
        "subject": subject,
        "topics": list(topics),
        "recipe": dict(recipe),
        "tickets_count": tickets_count,
        "total_points": total_points,
        "bank_fingerprint": bank_fingerprint,
    }


def append_history_entry(data_dir, entry):
    entries = load_history(data_dir)
    entries.append(entry)
    save_history(data_dir, entries)
    return entry


def is_subject_bank_file(filename):
    if not filename.endswith(".json"):
        return False

    subject_id = filename[:-5]
    return subject_id not in EXCLUDED_SUBJECT_IDS
