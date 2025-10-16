from celery import shared_task
@shared_task
def handle_deposit_success(tx_ref):
    # Legacy deposit handler removed
    return True