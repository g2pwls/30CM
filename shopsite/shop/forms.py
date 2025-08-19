from django import forms # 👈 django forms import
class SearchForm(forms.Form):
    """Search Form Definition"""
    name = forms.CharField() # 👈 글자를 입력할 수 있는 input을 만들어줘요.
    price = forms.IntegerField()