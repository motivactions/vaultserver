from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import Entry, Transaction
from .signals import (
    post_payment_success,
    post_payment_cancel,
    post_refund_success,
    post_withdraw_success,
    post_activity_completed,
)
from .utils import (
    get_midtrans_payment_account,  # Kas
    get_partner_balance_account,  # Balance
    get_activities_revenue_account,  # Pendapatan Jasa
    get_activities_expense_account,
)


@transaction.atomic
def record_sales_transaction(payment, invoice, *args, **kwargs):
    """Trigered when transaction success"""
    trx = Transaction.objects.create(
        reference=payment,
        note=f"{str(invoice.user).title()} buy service from {str(invoice.partner).title()} invoice #{invoice.id}.",
    )
    trx.save()
    Entry.objects.create(
        trx=trx,
        account=get_midtrans_payment_account(),
        flow=Entry.DEBITED,
        amount=payment.amount,
    )
    Entry.objects.create(
        trx=trx,
        account=get_activities_revenue_account(),
        flow=Entry.CREDITED,
        amount=payment.amount,
    )
    trx.confirm()


@transaction.atomic
def reverse_sales_transaction(invoice, *args, **kwargs):
    """Trigered when transaction success"""
    trx = Transaction.objects.create(
        reference=invoice,
        note=f"{str(invoice.user).title()} buy service from {str(invoice.partner).title()} invoice #{invoice.id}.",
    )
    trx.save()
    Entry.objects.create(
        trx=trx,
        account=get_activities_revenue_account(),
        flow=Entry.DEBITED,
        amount=invoice.amount_total,
    )
    Entry.objects.create(
        trx=trx,
        account=get_midtrans_payment_account(),
        flow=Entry.CREDITED,
        amount=invoice.amount_total,
    )
    trx.confirm()


@transaction.atomic
def record_refund_transaction(payment, credit_note, *args, **kwargs):
    trx = Transaction.objects.create(
        reference=payment,
        note=f"{str(credit_note.recipient).title()} cancel purchase from {str(credit_note.partner).title()}.",
    )
    Entry.objects.create(
        trx=trx,
        account=get_activities_revenue_account(),
        flow=Entry.DEBITED,
        amount=payment.amount,
    )
    Entry.objects.create(
        trx=trx,
        account=get_midtrans_payment_account(),
        flow=Entry.CREDITED,
        amount=payment.amount,
    )
    trx.confirm()


@transaction.atomic
def record_activity_complete_transaction(vendor_bill, *args, **kwargs):
    trx = Transaction.objects.create(
        reference=vendor_bill,
        note=f"{str(vendor_bill.partner).title()} balance added.",
    )
    Entry.objects.create(
        trx=trx,
        account=get_activities_expense_account(),
        flow=Entry.DEBITED,
        amount=vendor_bill.amount_total,
    )
    Entry.objects.create(
        trx=trx,
        account=get_partner_balance_account(vendor_bill.partner),
        flow=Entry.CREDITED,
        amount=vendor_bill.amount_total,
    )
    trx.confirm()


@transaction.atomic
def record_partner_balance_topup(partner, amount, *args, **kwargs):
    trx = Transaction.objects.create(
        reference=partner,
        note=f"{str(partner).title()} topup.",
    )
    Entry.objects.create(
        trx=trx,
        account=get_midtrans_payment_account(),
        flow=Entry.DEBITED,
        amount=amount,
    )
    Entry.objects.create(
        trx=trx,
        account=get_partner_balance_account(partner),
        flow=Entry.CREDITED,
        amount=amount,
    )
    trx.confirm()


@transaction.atomic
def record_withdrawal(payment, withdraw_statement, *args, **kwargs):
    trx = Transaction.objects.create(
        reference=payment,
        note=f"{str(withdraw_statement.partner).title()} withdrawal #{withdraw_statement.id}.",
    )
    Entry.objects.create(
        trx=trx,
        account=get_partner_balance_account(withdraw_statement.partner),
        flow=Entry.DEBITED,
        amount=payment.amount,
    )
    Entry.objects.create(
        trx=trx,
        account=get_midtrans_payment_account(),
        flow=Entry.CREDITED,
        amount=payment.amount,
    )
    trx.confirm()


# Connect the signal
post_payment_success.connect(
    record_sales_transaction,
    dispatch_uid="commerce.vaults.models.transaction",
)

post_payment_cancel.connect(
    reverse_sales_transaction,
    dispatch_uid="commerce.vaults.models.transaction",
)

post_activity_completed.connect(
    record_activity_complete_transaction,
    dispatch_uid="commerce.vaults.models.transaction",
)

post_refund_success.connect(
    record_refund_transaction,
    dispatch_uid="commerce.vaults.models.transaction",
)

post_withdraw_success.connect(
    record_withdrawal,
    dispatch_uid="commerce.vaults.models.transaction",
)
