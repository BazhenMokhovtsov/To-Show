from django import forms

from .models.instruction import Instruction
from .models.product import Product


class RecipeInstructionForm(forms.ModelForm):
    instruction = forms.CharField(
        label="Инструкция",
        widget=forms.Textarea(attrs={"placeholder": "Инструкция"}),
        required=False,
    )
    step = forms.IntegerField(label="Шаг", min_value=1, required=False)

    step_image = forms.ImageField(label="step image", required=False)

    class Meta:
        model = Instruction
        fields = ("instruction", "step", "step_image")

class IngredientForm(forms.Form):
    new_product = forms.ModelChoiceField(
        queryset=Product.objects.all().only('title').values_list('title', flat=True),
        label="Продукт",
        required=False,
    )
    grams = forms.FloatField(label="Граммовка", required=False)



