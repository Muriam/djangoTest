from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CashFlow, Status, TransactionType, Category, Subcategory
from .serializers import (
    CashFlowSerializer, StatusSerializer, TransactionTypeSerializer,
    CategorySerializer, SubcategorySerializer
)

class CashFlowViewSet(viewsets.ModelViewSet):
    queryset = CashFlow.objects.select_related(
        'status', 'transaction_type', 'category', 'subcategory'
    ).all().order_by('-date')
    serializer_class = CashFlowSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        status_id = self.request.query_params.get('status_id')
        transaction_type_id = self.request.query_params.get('transaction_type_id')
        category_id = self.request.query_params.get('category_id')
        subcategory_id = self.request.query_params.get('subcategory_id')
        
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if status_id:
            qs = qs.filter(status_id=status_id)
        if transaction_type_id:
            qs = qs.filter(transaction_type_id=transaction_type_id)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if subcategory_id:
            qs = qs.filter(subcategory_id=subcategory_id)
        return qs

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

class TransactionTypeViewSet(viewsets.ModelViewSet):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

@api_view(['GET'])
def categories_by_type(request):
    type_id = request.query_params.get('type_id')
    if type_id:
        categories = Category.objects.filter(transaction_type_id=type_id)
    else:
        categories = Category.objects.none()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def subcategories_by_category(request):
    cat_id = request.query_params.get('category_id')
    if cat_id:
        subcategories = Subcategory.objects.filter(category_id=cat_id)
    else:
        subcategories = Subcategory.objects.none()
    serializer = SubcategorySerializer(subcategories, many=True)
    return Response(serializer.data)