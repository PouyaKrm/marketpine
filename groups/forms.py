from django import forms
import django.core.validators

from groups.models import BusinessmanGroups


class AddGroupForm(forms.ModelForm):
    title = forms.CharField(max_length=40)

    class Meta:
        model = BusinessmanGroups
        fields = '__all__'

    def clean(self):
        super().clean()
        group_type = self.cleaned_data.get('type')
        businessman = self.cleaned_data.get('businessman')
        if self.instance is not None and ((
                                                  group_type == BusinessmanGroups.TYPE_TOP_PURCHASE and self.instance.type != BusinessmanGroups.TYPE_TOP_PURCHASE) or (
                                                  group_type != BusinessmanGroups.TYPE_TOP_PURCHASE and self.instance.type == BusinessmanGroups.TYPE_TOP_PURCHASE)):
            raise forms.ValidationError('can not change group with type PURCHASE TOP or change to PURCHASE TOP')
        elif self.instance is None and group_type == BusinessmanGroups.TYPE_TOP_PURCHASE:
            raise forms.ValidationError('can create group with type PURCHASE TOP')

        title = self.cleaned_data.get('title')
        if self.instance is None and not BusinessmanGroups.is_title_unique(businessman, title):
            raise forms.ValidationError('group title must be unique')
        elif self.instance is not None and (
                title != self.instance.title and not BusinessmanGroups.is_title_unique(businessman, title)):
            raise forms.ValidationError('group title must be unique')
        else:
            pass
