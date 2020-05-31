from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import SignUpForm
from movie_app.models import ClusteringStatus
import json
from django.http import HttpResponse


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            # Set clustering Status to done
            cs = ClusteringStatus()
            cs.user = user
            cs.status = 'Not clustered'
            cs.save()
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


class OutputObject:
    """This is the central class """
    def __init__(self, status=None, message=None, data=None,
                 dict_additional_meta_data={}):
        self.status = status
        self.message = message
        self.data = data
        self.additional_meta_data = dict_additional_meta_data

    def build_meta_data(self, standard_dict):
        self.additional_meta_data.update(standard_dict)

    def build_output_dict(self):
        self.build_meta_data(standard_dict={'status': self.status,
                                            'message': self.message})
        self.output_dict = {'meta': self.additional_meta_data,
                            'data': self.data}

    def get_http_response(self):
        self.build_output_dict()
        return HttpResponse(json.dumps(self.output_dict),
                            'application/json')
