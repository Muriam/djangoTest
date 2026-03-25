from django.contrib import admin
from .models import Status, TransactionType, Category, Subcategory, CashFlow


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'transaction_type', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('name',)

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'transaction_type', 'category', 'subcategory', 'amount', 'comment')
    list_filter = ('date', 'status', 'transaction_type', 'category')
    search_fields = ('comment',)
    date_hierarchy = 'date'
