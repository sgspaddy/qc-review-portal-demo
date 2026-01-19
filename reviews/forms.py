from django import forms
from .rules import Decision


class DecisionForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[(d.value, d.value) for d in Decision],
        widget=forms.RadioSelect,
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Optional reviewer comment…"}),
    )

