from typing import List


def get_model_ids(models: list) -> List[int]:
    return list(map(lambda e: e.id, models))
