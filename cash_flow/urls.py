from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.CashFlowViewSet, basename='transaction')
router.register(r'statuses', views.StatusViewSet)
router.register(r'types', views.TransactionTypeViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'subcategories', views.SubcategoryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/get-categories/', views.categories_by_type, name='categories_by_type'),
    path('api/get-subcategories/', views.subcategories_by_category, name='subcategories_by_category'),
    path('', TemplateView.as_view(template_name='cash_flow/index.html'), name='home'),
]