from rest_framework import serializers
from .models import CashFlow, Status, TransactionType, Category, Subcategory

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'transaction_type']

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']

class CashFlowSerializer(serializers.ModelSerializer):
    status_name = serializers.ReadOnlyField(source='status.name')
    type_name = serializers.ReadOnlyField(source='transaction_type.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.name')
    
    class Meta:
        model = CashFlow
        fields = ['id', 'date', 'status', 'status_name', 'transaction_type',
                  'type_name', 'category', 'category_name', 'subcategory',
                  'subcategory_name', 'amount', 'comment', 'created_at']