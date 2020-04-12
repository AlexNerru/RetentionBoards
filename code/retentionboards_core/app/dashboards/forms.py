from django import forms


class UploadForm(forms.Form):
    name = forms.CharField(label='Eventset name', max_length=100)
    file = forms.FileField(label='File')