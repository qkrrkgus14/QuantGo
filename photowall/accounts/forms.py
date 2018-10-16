from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields 이렇게 생성된 필드들은 self.fields를 통해 접근 할 수 있다.
        self.fields['password1'].help_text = " "
        self.fields['username'].help_text = "Enter the ID."
        #self.fields['last_name'].help_text = "사용자 성을 입력하세요"
        #self.fields['first_name'].help_text = "사용자 이름을 입력하세요"

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)
        fields = UserCreationForm.Meta.fields + ('first_name','last_name',)
        

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            if get_user_model().objects.filter(email=email).exists():
                raise forms.ValidationError('duplicated email')
        return email

