from educations.models import Education


class EducationService:

    def get_all_educations(self, education_type_id: int = None):
        if education_type_id is None:
            return Education.objects.all()
        return Education.objects.filter(education_type__id=education_type_id).all()

education_service = EducationService()
