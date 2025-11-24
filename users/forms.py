from django import forms
from .models import User
from . import models
from django.contrib.auth.forms import UserChangeForm

class LoginForm(forms.Form):
    """Login Form Definition"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',  # CSS 클래스 추가
    }),
        label="이메일(아이디)")
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',  # CSS 클래스 추가
    }),
        label="비밀번호")
    def clean(self):
        email = self.cleaned_data.get("email") # 👈 유효성 검사를 진행한 email field에 값을 추출합니다.
        password = self.cleaned_data.get("password") # 👈 유효성 검사를 진행한 password field에 값을 추출합니다.
        try:
            user = models.User.objects.get(email=email) # 👈 emil을 기준으로 해당 Object를 가져와요!
            if user.check_password(password):  # 👈 비밀번호가 서로 일치하다면 True, 아니면 False 반환
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("Password is wrong"))
        except models.User.DoesNotExist:
            self.add_error("email", forms.ValidationError("User does not exist"))

class SignUpForm(forms.Form):
    name = forms.CharField(max_length=10)
    email = forms.EmailField()
    tel = forms.CharField()
    birthday = forms.DateField()
    postcode = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255 )
    detail_address = forms.CharField(max_length=255)
    extra_address = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput) # 👈 Password로 템플릿에 필드가 표시됩니다.
    password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password") # 👈 label값으로 템플릿에 필드가 표시됩니다.

# email이 이미 등록되었는지에 대한 validation
    def clean_email(self):
        email = self.cleaned_data.get("email") # 👈 필드의 입력값 가져오기
        try:
            models.User.objects.get(email=email) # 👈 필드의 email값이 DB에 존재하는지 확인
            raise forms.ValidationError("User already exists with that email")
        except models.User.DoesNotExist:
            return email  # 👈 존재하지 않는다면, 데이터를 반환시킵니다.
    # 두개의 password가 일치한지에 대한 validation
    def clean_password1(self):
        password = self.cleaned_data.get("password") # 👈 필드의 입력값 가져오기
        password1 = self.cleaned_data.get("password1") # 👈 필드의 입력값 가져오기
        if password != password1:
            raise forms.ValidationError("Password confirmation does not match")
        else:
            return password
    # save 매서드로 DB에 저장
    def save(self):
        name = self.cleaned_data.get("name")
        email = self.cleaned_data.get("email")
        tel = self.cleaned_data.get("tel")
        birthday = self.cleaned_data.get("birthday", null=True)
        postcode = self.cleaned_data.get("postcode")
        address = forms.CharField(max_length=255, blank=True, null=True)
        detail_address = forms.CharField(max_length=255, blank=True, null=True)
        extra_address = forms.CharField(max_length=255, blank=True, null=True)
        password = self.cleaned_data.get("password")
        # create_user()에 id(email), email(email), password(password) 값을 순서대로 넣어줘요!
        user = models.User.objects.create_user(email, email, password)
        user.name = name
        user.tel = tel
        user.birthday = birthday
        user.postcode = postcode
        user.address = address
        user.detail_address = detail_address
        user.extra_address = extra_address
        user.save()       

class SignUpForm(forms.ModelForm): # 👈 ModelForm을 상속하면 Model을 활용할 수 있어요!
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'emailform-control',  # CSS 클래스 추가
            'placeholder': 'abc@email.com',  # 선택적으로 placeholder 추가
        }),
        label="이메일(아이디)"  # 라벨도 명시적으로 지정
    )

    class Meta:
        model = models.User
        fields = ("email",)

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
    }), label="Confirm Password")
    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")
        if password != password1:
            raise forms.ValidationError("Password confirmation does not match")
        else:
            return password    
    def save(self, *args, **kwargs): # 👈 save 매서드 가로채기
        user = super().save(commit=False) # 👈 Object는 생성하지만, 저장은 하지 않습니다.
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password) # 👈 set_password는 비밀번호를 해쉬값으로 변환해요!
        user.save() # 👈 이제 저장해줄께요:) 

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User()
        fields = ('email', 'name',)

from django import forms
from .models import User

class SignupCompleteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'tel', 'birthday']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '이름 입력', 'maxlength': '10'}),
            'tel': forms.TextInput(attrs={'placeholder': '전화번호 입력 ("-" 제외)', 'maxlength': '11'}),
            'birthday': forms.DateInput(attrs={'type': 'date', 'placeholder': '생일 입력 (YYYY-MM-DD)'}),
        }
        labels = {
            'name': '이름',
            'tel': '전화번호',
            'birthday': '생일',
        }
