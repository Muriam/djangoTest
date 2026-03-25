from django.urls import path
from . import views


app_name = 'cashflow'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),

    # AJAX endpoints для зависимых выпадающих списков в форме операции
    path('ajax/categories-by-type/', views.categories_by_transaction_type, name='ajax_categories_by_type'),
    path('ajax/subcategories-by-category/', views.subcategories_by_category, name='ajax_subcategories_by_category'),
    
    # Справочники
    path('statuses/', views.StatusListView.as_view(), name='status_list'),
    path('statuses/create/', views.StatusCreateView.as_view(), name='status_create'),
    path('statuses/<int:pk>/edit/', views.StatusUpdateView.as_view(), name='status_edit'),
    path('statuses/<int:pk>/delete/', views.StatusDeleteView.as_view(), name='status_delete'),
    
    path('types/', views.TypeListView.as_view(), name='type_list'),
    path('types/create/', views.TypeCreateView.as_view(), name='type_create'),
    path('types/<int:pk>/edit/', views.TypeUpdateView.as_view(), name='type_edit'),
    path('types/<int:pk>/delete/', views.TypeDeleteView.as_view(), name='type_delete'),
    
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    path('subcategories/', views.SubcategoryListView.as_view(), name='subcategory_list'),
    path('subcategories/create/', views.SubcategoryCreateView.as_view(), name='subcategory_create'),
    path('subcategories/<int:pk>/edit/', views.SubcategoryUpdateView.as_view(), name='subcategory_edit'),
    path('subcategories/<int:pk>/delete/', views.SubcategoryDeleteView.as_view(), name='subcategory_delete'),
]