from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile


class UserBioForms(forms.Form):
    name = forms.CharField(label='Your name', max_length="33")
    age = forms.IntegerField(label="Your age", min_value='1', max_value='111')
    bio = forms.CharField(label='Biography', widget=forms.Textarea)


def validate_file_name(file:InMemoryUploadedFile) -> None:
    if file.name and "virus" in file.name:
        raise ValidationError("file name should not contain 'virus'")


def validate_file_size(file:InMemoryUploadedFile) -> None:
    if file.size > 1024 ** 2:
        raise ValidationError("file size too large, file mast be less than 1Mb")


class UploadFileForms(forms.Form):
    file = forms.FileField(validators=[validate_file_name, validate_file_size])

