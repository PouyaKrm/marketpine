from django import forms
from django.core.exceptions import ValidationError

from common.util import get_file_extension
from educations.models import Education


class EducationCreationForm(forms.ModelForm):

    class Meta:
        model = Education
        fields = '__all__'

    def clean_video(self):
        video = self.cleaned_data.get('video')
        ext = get_file_extension(video.name)
        if ext not in ['.mp4', '.mkv']:
            raise ValidationError('video format should be .mp4 or .mkv')

        return video



