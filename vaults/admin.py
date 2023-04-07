from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from polymorphic.admin import PolymorphicParentModelAdmin

from .models import Account, AccountType, Entry, Transaction, TransactionType


@admin.register(AccountType)
class AccountTypeAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "debit")  # Sane defaults.
    list_display_links = ("indented_title",)  # Sane defaults.


@admin.register(TransactionType)
class TransactionTypeAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "description")  # Sane defaults.
    list_display_links = ("indented_title",)  # Sane defaults.


@admin.register(Account)
class AccountAdmin(PolymorphicParentModelAdmin):
    child_models = [Account]
    list_filter = ["account_type"]
    search_fields = ["name"]
    list_display = [
        "code",
        "name",
        "balance",
        "status",
        "linked_object",
        "last_modified_at",
        "account_type",
    ]


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    search_fields = ["account__name"]
    list_display = [
        "created_at",
        "trx",
        "account",
        "flow",
        "debit",
        "credit",
    ]
    autocomplete_fields = ["trx", "account"]


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 1
    fields = ("account", "flow", "amount")
    # autocomplete_fields = ["account"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    inlines = [EntryInline]
    list_display = [
        "created_at",
        "reference_id",
        "reference",
        "note",
        "status",
    ]
    actions = ["confirm_transaction"]
    search_fields = ["note", "reference_id"]

    def confirm_transaction(self, request, queryset):
        for obj in queryset.all():
            obj.confirm()
