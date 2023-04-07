from django.dispatch import Signal

post_payment_success = Signal()
post_payment_cancel = Signal()
post_refund_success = Signal()
post_activity_completed = Signal()
post_withdraw_success = Signal()
