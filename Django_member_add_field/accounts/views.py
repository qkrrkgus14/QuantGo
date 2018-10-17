#accounts/views.py
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import SignupForm


#임시홈페이지 view, accounts 앱에는 홈페이지 구성 필요없음
def homepage(request):
    return render(request, "accounts/layout.html")


#회원가입
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            #return redirect(settings.LOGIN_URL) #디폴트값 : "accounts/login"
            return redirect("homepage") #디폴트값 : "accounts/login"
    else:
        form = SignupForm()
    return render(request, 'accounts/signup_form.html', {
        'form': form,
    })


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
