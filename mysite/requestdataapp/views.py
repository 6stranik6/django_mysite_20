from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from requestdataapp.forms import UserBioForms, UploadFileForms


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a")
    b = request.GET.get("b")
    result = a + b
    context = {
        "a": a,
        "b": b,
        'result': result,
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        'form': UserBioForms(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:

    if request.method == 'POST':
        form = UploadFileForms(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data['file']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print('"saved file', filename)
    else:
        form = UploadFileForms()

    context = {
        "form": form,
    }
    return render(request, 'requestdataapp/file-upload.html', context=context)


