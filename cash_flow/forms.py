from django import forms
from .models import CashFlow, Category, Subcategory


class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = ['date', 'status', 'transaction_type', 'category', 'subcategory', 'amount', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_transaction_type'}),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'subcategory': forms.Select(attrs={'class': 'form-control', 'id': 'id_subcategory'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Необязательный комментарий'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если есть выбранный тип, фильтруются категории
        if 'transaction_type' in self.data:
            try:
                transaction_type_id = int(self.data.get('transaction_type'))
                self.fields['category'].queryset = Category.objects.filter(
                    transaction_type_id=transaction_type_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['category'].queryset = self.instance.transaction_type.categories.all()
        
        # Если есть выбранная категория, фильтруются подкатегории
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(
                    category_id=category_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.all()