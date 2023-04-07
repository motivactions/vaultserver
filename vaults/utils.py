from django.contrib.contenttypes.models import ContentType

from .configs import vaults_configs as configs

from .models import Account, AccountType

names = configs.ACCOUNT_NAMES


def get_or_create_account(
    name=None,
    type_name=None,
    code=None,
    account_model=None,
    linked_object=None,
):
    filters = dict()
    if account_model is None:
        account_model = Account
    if linked_object is not None:
        ctype = ContentType.objects.get_for_model(linked_object.__class__)
        filters["linked_object_type"] = ctype
        filters["linked_object_id"] = linked_object.id
    if type_name is not None:
        acc_type = AccountType.objects.get(name=type_name)
        filters["account_type"] = acc_type
    filters["code"] = code
    defaults = {"name": name}
    account, created = account_model.objects.get_or_create(**filters, defaults=defaults)
    return account, created


def get_equity_account(partner):
    account, _ = get_or_create_account(
        name="Quity",
        code="EQU.001",
        type_name=names["EQUITY"],
    )
    return account


def get_partner_balance_account(partner):
    account, _ = get_or_create_account(
        name="%s (Balance)" % str(partner),
        code="BLP.%s" % partner.id,
        type_name=names["PARTNER_BALANCE"],
        linked_object=partner,
    )
    return account


def get_activities_revenue_account():
    account, _ = get_or_create_account(
        name="Activities Revenues",
        code="RV.001",
        type_name=names["ACTIVITIES_REVENUE"],
    )
    return account


def get_activities_expense_account():
    account, _ = get_or_create_account(
        name="Activities Expenses",
        code="XP.001",
        type_name=names["ACTIVITIES_EXPENSE"],
    )
    return account


def get_cash_account(cash_gateway, type_name=None):
    code = "%s" % cash_gateway.id
    account, _ = get_or_create_account(
        name=str(cash_gateway),
        type_name=type_name or names["CASH"],
        code="CASH.%s" % (code.zfill(4)),
        linked_object=cash_gateway,
    )
    return account


def get_midtrans_payment_account():
    account, _ = get_or_create_account(
        name="Midtrans Payments",
        type_name=names["CASH"],
        code="MIDTRANS",
    )
    return account
