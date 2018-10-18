from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class SignupForm(UserCreationForm):
    #회원가입시 받을 수 있게 아래 2개 필드 지정
    #여기서 주의할점은 forms.필드와 modfels.필드는 서로 가지고있는 필드 유형이 각각다릅니다.
    #즉 models.py에 있는 필드가 forms에는 없는 필드도 있고
    #forms.py에 있는 필드가 models에는 없는 필드가 있고 각각 서로 다른 필드를 가지고 있습니다.
    #필드유형을 똑같이 매칭시키면 안될수 있기에 말씀드리고
    #보통 forms.필드에는 CharField()가 무난한 것 같습니다.(저도 자세히는 모릅니다 )
    phone_number = forms.CharField()
    address = forms.CharField()

    #여기는 회원가입란에서 추가필드에 대한 정보를 받아서 저장한다는코드로 보시면 될 것 같습니다.
    def save(self):
        user = super().save()
        profile = Profile.objects.create(
            user = user,
            phone_number = self.cleaned_data["phone_number"],
            address = self.cleaned_data["address"])
        return user