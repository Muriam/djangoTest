from django.core.management.base import BaseCommand
from cash_flow.models import Status, TransactionType, Category, Subcategory


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными'

    def handle(self, *args, **options):
        # Создание статусов
        statuses = ['Бизнес', 'Личное', 'Налог']
        for status_name in statuses:
            Status.objects.get_or_create(name=status_name)
        self.stdout.write(self.style.SUCCESS('Статусы созданы'))

        # Создание типов операций
        types = ['Пополнение', 'Списание']
        for type_name in types:
            TransactionType.objects.get_or_create(name=type_name)
        self.stdout.write(self.style.SUCCESS('Типы операций созданы'))

        # Создание категории и подкатегории
        categories_data = {
            'Списание': {
                'Инфраструктура': ['VPS', 'Proxy', 'Хостинг'],
                'Маркетинг': ['Farpost', 'Avito', 'Яндекс.Директ'],
                'Зарплата': ['Оклад', 'Премия'],
                'Офис': ['Аренда', 'Интернет', 'Коммунальные услуги']
            },
            'Пополнение': {
                'Доход от услуг': ['Консультации', 'Разработка', 'Поддержка'],
                'Инвестиции': ['Дивиденды', 'Проценты']
            }
        }

        for type_name, categories in categories_data.items():
            transaction_type = TransactionType.objects.get(name=type_name)
            for category_name, subcategories in categories.items():
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    transaction_type=transaction_type
                )
                for subcategory_name in subcategories:
                    Subcategory.objects.get_or_create(
                        name=subcategory_name,
                        category=category
                    )
        
        self.stdout.write(self.style.SUCCESS('Категории и подкатегории созданы'))