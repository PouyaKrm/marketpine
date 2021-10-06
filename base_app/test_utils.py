from typing import List

from django.db.models import QuerySet


def get_model_list_ids(models: list) -> List[int]:
    return list(map(lambda e: e.id, models))


def count_model_queryset_by_ids(model: QuerySet, ids: List[int]) -> int:
    return model.filter(id__in=ids).count()
