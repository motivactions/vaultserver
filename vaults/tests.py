from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import tag
from activities.models import FlexyTicket, OneTimeTicket, Activity
from commerce.invoices.models import Invoice, InvoiceLine
from commerce.partners.models import Partner
from commerce.payments.models import Bank, CustomerPayment, PartnerPayment
from commerce.refunds.models import CreditNote
from commerce.withdraws.models import (
    BeneficiaryBank,
    PartnerBankAccount,
    UserBankAccount,
    WithdrawStatement,
    WithdrawRequest,
)

from commerce.vaults.handlers import (
    post_payment_success,
    post_refund_success,
    post_withdraw_success,
    post_activity_completed,
    record_partner_balance_topup,
)
from commerce.vaults.models import Account, Entry, Transaction
from commerce.vaults.utils import (
    get_midtrans_payment_account,  # Kas
    get_partner_balance_account,  # Balance
    get_activities_revenue_account,  # Pendapatan Jasa
    get_activities_expense_account,  # Biaya Usaha
)
from commerce.vendorbills.helpers import complete_ticket

User = get_user_model()


class VaultUnitTestCase(TestCase):
    def setUp(self):
        call_command("init_accounts")
        self.user = User.objects.create_user(
            username="user",
            email="test@yopmail.com",
            password="testpassword",
            is_superuser=True,
            is_staff=True,
        )
        self.bank = Bank(code="101", name="BCA")
        self.bank.save()
        self.beneficiary_bank = BeneficiaryBank(code="bca", name="BCA")
        self.beneficiary_bank.save()
        self.user_bank = UserBankAccount(
            user=self.user,
            bank=self.beneficiary_bank,
            name="BCA",
            holder="Test name",
            account="0011223344",
            note="test",
        )
        self.user_bank.save()
        self.partner = Partner(
            user=self.user,
            name="Partner Old",
            phone="+6289523115484",
            email="test@partner.id",
        )
        self.partner.save()
        self.partner_bank = PartnerBankAccount(
            partner=self.partner,
            bank=self.beneficiary_bank,
            name="Test Partner Bank",
            holder="Test name",
            account="0011223344",
            note="test",
        )
        self.partner_bank.save()
        self.activity = Activity(
            partner=self.partner,
            name="test activity",
            is_active=True,
            is_published=True,
        )
        self.activity.save()
        self.first_product = OneTimeTicket(
            partner=self.partner,
            name="One time ticket",
            price=100000,
            discount=10.0,
            service=self.activity,
            date_time_start=timezone.now(),
            date_time_end=timezone.now() + timezone.timedelta(days=30),
            is_published=True,
            stock_on_hold=2,
        )
        self.first_product.save()
        self.second_product = FlexyTicket(
            partner=self.partner,
            name="test flexy ticket",
            price=50000,
            discount=20.0,
            service=self.activity,
            date_time_start=timezone.now(),
            date_time_end=timezone.now() + timezone.timedelta(days=30),
            is_published=True,
            reusable=4,
            stock_on_hold=2,
        )
        self.second_product.save()
        self.invoice = Invoice(
            user=self.user,
            tax=0.0,
            platform_fee=5.0,
        )
        self.invoice.save()
        self.first_invoice_line = InvoiceLine(
            status=InvoiceLine.CONFIRMED,
            invoice=self.invoice,
            product=self.first_product,
            product_price=self.first_product.price,
            product_discount=self.first_product.discount,
            quantity=1,
        )
        self.first_invoice_line.save()
        self.second_invoice_line = InvoiceLine(
            status=InvoiceLine.CONFIRMED,
            invoice=self.invoice,
            product=self.second_product,
            product_price=self.second_product.price,
            product_discount=self.second_product.discount,
            quantity=2,
        )
        self.second_invoice_line.save()
        self.payment = CustomerPayment(
            status="paid",
            reference_object=self.invoice,
            user=self.user,
            amount=self.invoice.amount_total,
            payment_type="credit card",
        )
        self.payment.save()
        self.credit_note = CreditNote(
            recipient=self.user,
            recipient_account=self.user_bank,
            partner=self.partner,
            invoice=self.invoice,
            amount_initial=self.first_invoice_line.amount_total,
        )
        self.credit_note.save()
        self.credit_note.add_from_invoice_lines(self.first_invoice_line)
        self.refund_payment = PartnerPayment(
            status="paid",
            reference_object=self.credit_note,
            partner=self.credit_note.partner,
            amount=self.credit_note.amount_total,
            payment_type="credit card",
        )
        self.refund_payment.save()
        record_partner_balance_topup(self.partner, 1000000)
        # self.partner.balance = 1000000  # temporary bypass partner balance limit
        self.withdraw_request = WithdrawRequest(
            status="approved",
            partner=self.partner,
            bank=self.partner_bank,
            amount=100000,
            user=self.user,
            name="BANK",
            holder="test user",
            account=123456,
        )
        self.withdraw_request.save()
        self.withdraw_statement = WithdrawStatement(
            status="approved",
            withdraw_request=self.withdraw_request,
            bank=self.withdraw_request.bank,
            amount=100000,
            partner=self.partner,
        )
        self.withdraw_statement.save()
        self.withdraw_payment = PartnerPayment(
            status="paid",
            reference_object=self.withdraw_statement,
            partner=self.withdraw_statement.partner,
            amount=self.withdraw_statement.amount,
            payment_type="midtrans",
        )
        self.withdraw_payment.save()

    @tag("vaults_test", "vault_unit_test")
    def test_handle_payment_success(self):
        trx_count = Transaction.objects.count()
        entry_count = Entry.objects.count()
        post_payment_success.send(
            payment=self.payment, invoice=self.invoice, sender=None
        )
        self.assertEqual(Transaction.objects.count(), trx_count + 1)
        self.assertEqual(Entry.objects.count(), entry_count + 2)
        self.assertEqual(get_activities_revenue_account().balance, 170000)
        self.assertEqual(get_midtrans_payment_account().balance, 1170000)

    @tag("vault_test", "vault_unit_test")
    def test_handle_refund_success(self):
        trx_count = Transaction.objects.count()
        entry_count = Entry.objects.count()

        # Create sales transaction
        post_payment_success.send(
            payment=self.payment,
            invoice=self.invoice,
            sender=None,
        )

        self.assertEqual(Transaction.objects.count(), trx_count + 1)
        self.assertEqual(Entry.objects.count(), entry_count + 2)
        self.assertEqual(get_activities_revenue_account().balance, 170000)
        self.assertEqual(get_midtrans_payment_account().balance, 1170000)

        # create refund transaction
        self.credit_note.set_to_paid("midtrans")

        self.assertEqual(Transaction.objects.count(), trx_count + 2)
        self.assertEqual(Entry.objects.count(), entry_count + 4)
        self.assertEqual(self.credit_note.amount_total, 90000.00)
        self.assertEqual(get_activities_revenue_account().balance, 80000.00)
        self.assertEqual(get_midtrans_payment_account().balance, 1080000.00)
        self.assertEqual(get_activities_expense_account().balance, 0.00)
        self.assertEqual(get_partner_balance_account(self.partner).balance, 1000000.00)

        # completing ticket with no invoice lines confirmed will raise validation error
        with self.assertRaises(ValidationError):
            complete_ticket(self.first_product)

        # completing which has transaction / invoice lines confirmed
        vendor_bill = complete_ticket(self.second_product)

        self.assertEqual(Transaction.objects.count(), trx_count + 3)
        self.assertEqual(Entry.objects.count(), entry_count + 6)
        self.assertEqual(get_activities_expense_account().balance, 64000.00)
        self.assertEqual(
            get_partner_balance_account(vendor_bill.partner).balance, 1064000.00
        )

        post_withdraw_success.send(
            payment=self.withdraw_payment,
            withdraw_statement=self.withdraw_statement,
            sender=None,
        )

        self.assertEqual(Transaction.objects.count(), trx_count + 4)
        self.assertEqual(Entry.objects.count(), entry_count + 8)
        self.assertEqual(get_midtrans_payment_account().balance, 980000.00)
        self.assertEqual(
            get_partner_balance_account(vendor_bill.partner).balance, 964000.00
        )
