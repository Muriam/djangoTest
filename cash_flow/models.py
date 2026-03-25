from django.db import models
from django.core.exceptions import ValidationError


class Status(models.Model):
    """Статусы: Бизнес, Личное, Налог и другие"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TransactionType(models.Model):
    """Типы операций: Пополнение, Списание и другие"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Category(models.Model):
    """Категории, привязанные к типу операции"""
    name = models.CharField(max_length=100, verbose_name='Название')
    transaction_type = models.ForeignKey(
        TransactionType, 
        on_delete=models.CASCADE, 
        related_name='categories',
        verbose_name='Тип операции'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['transaction_type', 'name']
        unique_together = ['name', 'transaction_type']
    
    def __str__(self):
        return f"{self.name} ({self.transaction_type.name})"


class Subcategory(models.Model):
    """Подкатегории, привязанные к категории"""
    name = models.CharField(max_length=100, verbose_name='Название')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='subcategories',
        verbose_name='Категория'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['category', 'name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class CashFlow(models.Model):
    """Запись о движении денежных средств"""
    date = models.DateField(verbose_name='Дата операции')
    status = models.ForeignKey(
        Status, 
        on_delete=models.PROTECT, 
        verbose_name='Статус'
    )
    transaction_type = models.ForeignKey(
        TransactionType, 
        on_delete=models.PROTECT, 
        verbose_name='Тип операции'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        verbose_name='Категория'
    )
    subcategory = models.ForeignKey(
        Subcategory, 
        on_delete=models.PROTECT, 
        verbose_name='Подкатегория'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Сумма (руб.)'
    )
    comment = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Комментарий'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Движение денежных средств'
        verbose_name_plural = 'Движения денежных средств'
        ordering = ['-date', '-created_at']
    

    def clean(self):
        """Валидация бизнес-правил"""
        if self.category_id and self.transaction_type_id:
            if self.category.transaction_type_id != self.transaction_type_id:
                raise ValidationError(
                    {"category": "Категория не соответствует выбранному типу операции"}
                )
        if self.subcategory_id and self.category_id:
            # Аналогично: safe-only когда subcategory_id задан.
            if self.subcategory.category_id != self.category_id:
                raise ValidationError(
                    {
                        "subcategory": "Подкатегория не соответствует выбранной категории",
                    }
                )
    
    def __str__(self):
        return f"{self.date} - {self.amount} руб. - {self.status}"
