from django.conf import settings

from rest_framework.response import Response

download_settings = settings.DOWNLOAD_SETTINGS 
location = download_settings['NGINX_LOCATION']
redirect_header = download_settings['NGINX_REDIRECT_HEADER']
attachement_header = download_settings['ATTACHEMENT_HEADER']


def generate_attachement_name(file_name: str):
    return "attachement;filename=" + file_name

def generate_redirection_path(file_path: str):
    return f'/{location}/{file_path}'

def attach_file(file, response: Response = Response()):
    response[redirect_header] = generate_redirection_path(file.name)
    response[attachement_header] = generate_attachement_name(get_file_name(file.name))

    return response

def get_file_name(file_name: str):

    index = file_name.rfind('/')

    if index == -1:
        return file_name
    else:
        return file_name[index+1:]
