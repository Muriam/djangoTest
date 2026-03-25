from __future__ import annotations
from datetime import datetime
from typing import Any
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from .forms import CashFlowForm
from .models import Category, CashFlow, Subcategory, Status, TransactionType


def _parse_date(value: str | None) -> datetime.date | None:
    """
    Преобразует строку даты из GET-параметров к `datetime.date`.

    Поддерживаем два формата:
    - `YYYY-MM-DD` (формат <input type="date">)
    - `DD.MM.YYYY` (формат, указанный для ввода в настройках)
    """
    if not value:
        return None

    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


@require_GET
def categories_by_transaction_type(request: HttpRequest) -> HttpResponse:
    """Возвращает категории, подходящие выбранному типу операции (AJAX)."""
    transaction_type_id_raw = request.GET.get("transaction_type_id")
    try:
        transaction_type_id = int(transaction_type_id_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return JsonResponse({"categories": []})

    categories = Category.objects.filter(transaction_type_id=transaction_type_id).order_by("name")
    payload = {"categories": [{"id": c.id, "name": c.name} for c in categories]}
    return JsonResponse(payload)


@require_GET
def subcategories_by_category(request: HttpRequest) -> HttpResponse:
    """Возвращает подкатегории, подходящие выбранной категории (AJAX)."""
    category_id_raw = request.GET.get("category_id")
    try:
        category_id = int(category_id_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return JsonResponse({"subcategories": []})

    subcategories = Subcategory.objects.filter(category_id=category_id).order_by("name")
    payload = {"subcategories": [{"id": sc.id, "name": sc.name} for sc in subcategories]}
    return JsonResponse(payload)


class TransactionListView(ListView):
    """Список операций ДДС с фильтрами по параметрам из ТЗ."""

    model = CashFlow
    template_name = "cash_flow/transaction_list.html"
    context_object_name = "transactions"

    def get_queryset(self):
        qs = (
            CashFlow.objects.select_related("status", "transaction_type", "category", "subcategory")
            .all()
            .order_by("-date", "-created_at")
        )

        date_from = _parse_date(self.request.GET.get("date_from"))
        date_to = _parse_date(self.request.GET.get("date_to"))
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        status_id = self.request.GET.get("status_id")
        if status_id:
            qs = qs.filter(status_id=int(status_id))

        transaction_type_id = self.request.GET.get("transaction_type_id")
        if transaction_type_id:
            qs = qs.filter(transaction_type_id=int(transaction_type_id))

        category_id = self.request.GET.get("category_id")
        if category_id:
            qs = qs.filter(category_id=int(category_id))

        subcategory_id = self.request.GET.get("subcategory_id")
        if subcategory_id:
            qs = qs.filter(subcategory_id=int(subcategory_id))

        return qs

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Status.objects.all().order_by("name")
        context["types"] = TransactionType.objects.all().order_by("name")
        context["categories"] = Category.objects.all().order_by("transaction_type_id", "name")
        context["subcategories"] = Subcategory.objects.all().order_by("category_id", "name")
        return context


class TransactionCreateView(CreateView):
    """Создание записи о движении денежных средств."""

    model = CashFlow
    form_class = CashFlowForm
    template_name = "cash_flow/transaction_form.html"
    success_url = reverse_lazy("cashflow:transaction_list")


class TransactionUpdateView(UpdateView):
    """Редактирование записи о движении денежных средств."""

    model = CashFlow
    form_class = CashFlowForm
    template_name = "cash_flow/transaction_form.html"
    success_url = reverse_lazy("cashflow:transaction_list")


class TransactionDeleteView(DeleteView):
    """Удаление записи о движении денежных средств."""

    model = CashFlow
    template_name = "cash_flow/transaction_confirm_delete.html"
    success_url = reverse_lazy("cashflow:transaction_list")


class _BaseDictListView(ListView):
    """Базовый ListView для справочников (статусы/типы/категории/подкатегории)."""

    template_name = "cash_flow/dict_list.html"
    context_object_name = "objects"

    dict_title: str = ""
    columns: list[str] = []
    create_url_name: str = ""
    edit_url_name: str = ""
    delete_url_name: str = ""

    def build_cells(self, obj: Any) -> list[str]:
        return [str(obj)]

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        if not self.create_url_name or not self.edit_url_name or not self.delete_url_name:
            raise ImproperlyConfigured("Не заданы URL-имена для справочника.")

        context["dict_title"] = self.dict_title
        context["columns"] = self.columns
        context["create_url"] = reverse(self.create_url_name)

        rows: list[dict[str, Any]] = []
        for obj in context.get("objects", []):
            rows.append(
                {
                    "cells": self.build_cells(obj),
                    "edit_url": reverse(self.edit_url_name, args=[obj.pk]),
                    "delete_url": reverse(self.delete_url_name, args=[obj.pk]),
                }
            )
        context["rows"] = rows
        return context


class StatusListView(_BaseDictListView):
    model = Status
    dict_title = "Справочник статусов"
    columns = ["Название", "Дата создания"]
    create_url_name = "cashflow:status_create"
    edit_url_name = "cashflow:status_edit"
    delete_url_name = "cashflow:status_delete"

    def build_cells(self, obj: Status) -> list[str]:
        return [obj.name, obj.created_at.strftime("%d.%m.%Y %H:%M")]


class TypeListView(_BaseDictListView):
    model = TransactionType
    dict_title = "Справочник типов операций"
    columns = ["Название", "Дата создания"]
    create_url_name = "cashflow:type_create"
    edit_url_name = "cashflow:type_edit"
    delete_url_name = "cashflow:type_delete"

    def build_cells(self, obj: TransactionType) -> list[str]:
        return [obj.name, obj.created_at.strftime("%d.%m.%Y %H:%M")]


class CategoryListView(_BaseDictListView):
    model = Category
    dict_title = "Справочник категорий"
    columns = ["Название", "Тип операции", "Дата создания"]
    create_url_name = "cashflow:category_create"
    edit_url_name = "cashflow:category_edit"
    delete_url_name = "cashflow:category_delete"

    def build_cells(self, obj: Category) -> list[str]:
        return [obj.name, obj.transaction_type.name, obj.created_at.strftime("%d.%m.%Y %H:%M")]


class SubcategoryListView(_BaseDictListView):
    model = Subcategory
    dict_title = "Справочник подкатегорий"
    columns = ["Название", "Категория", "Дата создания"]
    create_url_name = "cashflow:subcategory_create"
    edit_url_name = "cashflow:subcategory_edit"
    delete_url_name = "cashflow:subcategory_delete"

    def build_cells(self, obj: Subcategory) -> list[str]:
        return [obj.name, obj.category.name, obj.created_at.strftime("%d.%m.%Y %H:%M")]


class _BaseDictFormView:
    """Общий функционал для Create/Update страниц справочников."""

    template_name = "cash_flow/dict_form.html"
    dict_title: str = ""
    list_url_name: str = ""
    fields: list[str] = []

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        context["dict_title"] = self.dict_title
        context["cancel_url"] = reverse(self.list_url_name)
        return context


class StatusCreateView(_BaseDictFormView, CreateView):
    model = Status
    fields = ["name"]
    dict_title = "Создание статуса"
    list_url_name = "cashflow:status_list"
    success_url = reverse_lazy("cashflow:status_list")


class StatusUpdateView(_BaseDictFormView, UpdateView):
    model = Status
    fields = ["name"]
    dict_title = "Редактирование статуса"
    list_url_name = "cashflow:status_list"
    success_url = reverse_lazy("cashflow:status_list")


class StatusDeleteView(_BaseDictFormView, DeleteView):
    model = Status
    dict_title = "Удаление статуса"
    list_url_name = "cashflow:status_list"
    template_name = "cash_flow/dict_confirm_delete.html"
    success_url = reverse_lazy("cashflow:status_list")


class TypeCreateView(_BaseDictFormView, CreateView):
    model = TransactionType
    fields = ["name"]
    dict_title = "Создание типа операции"
    list_url_name = "cashflow:type_list"
    success_url = reverse_lazy("cashflow:type_list")


class TypeUpdateView(_BaseDictFormView, UpdateView):
    model = TransactionType
    fields = ["name"]
    dict_title = "Редактирование типа операции"
    list_url_name = "cashflow:type_list"
    success_url = reverse_lazy("cashflow:type_list")


class TypeDeleteView(_BaseDictFormView, DeleteView):
    model = TransactionType
    dict_title = "Удаление типа операции"
    list_url_name = "cashflow:type_list"
    template_name = "cash_flow/dict_confirm_delete.html"
    success_url = reverse_lazy("cashflow:type_list")


class CategoryCreateView(_BaseDictFormView, CreateView):
    model = Category
    fields = ["name", "transaction_type"]
    dict_title = "Создание категории"
    list_url_name = "cashflow:category_list"
    success_url = reverse_lazy("cashflow:category_list")


class CategoryUpdateView(_BaseDictFormView, UpdateView):
    model = Category
    fields = ["name", "transaction_type"]
    dict_title = "Редактирование категории"
    list_url_name = "cashflow:category_list"
    success_url = reverse_lazy("cashflow:category_list")


class CategoryDeleteView(_BaseDictFormView, DeleteView):
    model = Category
    dict_title = "Удаление категории"
    list_url_name = "cashflow:category_list"
    template_name = "cash_flow/dict_confirm_delete.html"
    success_url = reverse_lazy("cashflow:category_list")


class SubcategoryCreateView(_BaseDictFormView, CreateView):
    model = Subcategory
    fields = ["name", "category"]
    dict_title = "Создание подкатегории"
    list_url_name = "cashflow:subcategory_list"
    success_url = reverse_lazy("cashflow:subcategory_list")


class SubcategoryUpdateView(_BaseDictFormView, UpdateView):
    model = Subcategory
    fields = ["name", "category"]
    dict_title = "Редактирование подкатегории"
    list_url_name = "cashflow:subcategory_list"
    success_url = reverse_lazy("cashflow:subcategory_list")


class SubcategoryDeleteView(_BaseDictFormView, DeleteView):
    model = Subcategory
    dict_title = "Удаление подкатегории"
    list_url_name = "cashflow:subcategory_list"
    template_name = "cash_flow/dict_confirm_delete.html"
    success_url = reverse_lazy("cashflow:subcategory_list")

