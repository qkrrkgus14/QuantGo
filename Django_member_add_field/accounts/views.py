#accounts/views.py
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import SignupForm


#임시 홈페이지 view, accounts 앱에는 홈페이지 구성 필요없음
#다른 앱 만들지 않았고 보여드리기 위함
def homepage(request):
    return render(request, "accounts/layout.html")


#회원가입
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            #return redirect(settings.LOGIN_URL) #디폴트값 : "accounts/login"
            return redirect("homepage") # 리다이렉트는 회원가입하고 제출버튼누르고 회원가입 통과되면
                                        # 다음 화면 어디로 넘어갈지 세팅해주는 코드
    else:
        form = SignupForm()
    return render(request, 'accounts/signup_form.html', {
        'form': form,
    })


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
