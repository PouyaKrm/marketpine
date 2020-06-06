from users.models import Businessman
from common.util import generate_url_safe_base64_file_name


def businessman_related_model_file_upload_path(instance, filename: str):

    return f'{instance.businessman.id}/{generate_url_safe_base64_file_name(filename)}'

