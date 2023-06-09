from educations.models import Education, EducationType


class EducationService:

    def get_all_educations(self, education_type_id: int = None):
        if education_type_id is None:
            return Education.objects.all().order_by('-create_date')
        return Education.objects.filter(education_type__id=education_type_id).order_by('-create_date').all()

    def get_all_education_types(self):
        return EducationType.objects.all()


education_service = EducationService()
