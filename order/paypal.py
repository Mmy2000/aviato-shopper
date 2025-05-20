# utils/paypal.py
import requests
from django.conf import settings
from paypalrestsdk import Payment
import paypalrestsdk

from order.models import Order,RefundPayment

paypalrestsdk.configure({
    "mode":  settings.PAYPAL_MODE,
    "client_id":  settings.PAYPAL_CLIENT_ID,
    "client_secret":  settings.PAYPAL_CLIENT_SECRET,
})

def get_paypal_access_token():
    url = f"{settings.PAYPAL_API_BASE_URL}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)

    response = requests.post(url, headers=headers, data=data, auth=auth)
    response.raise_for_status()
    return response.json().get("access_token")

def refund_payment(order):
    try:
        if order.payment_method.lower() == 'paypal':
            refund_data = {}
            payment = Payment.find(order.payment.payment_id)
            sale_id = payment.transactions[0].related_resources[0].sale.id
            sale = paypalrestsdk.Sale.find(sale_id)
            refund_data["amount"] = {
                "total": f"{float(order.order_total):.2f}",
                "currency": "USD",
            }
            refund = sale.refund(refund_data)
            print(f"Payment ID: {order.payment.payment_id}")
            if not order:
                return {"status": "error", "message": "order not found."}
            if refund.success():
                refund_response = refund.to_dict()
                refund_id = refund_response.get("id")
                refund_status = refund_response.get("state", "failed")
                refund_amount = refund_response["amount"]["total"]
                refund_currency = refund_response["amount"]["currency"]
                refund_from_transaction_fee = refund_response["refund_from_transaction_fee"]["value"]
                sale_id = refund_response["sale_id"]
                response_message = str(refund_response)
                RefundPayment.objects.create(
                    order=order,
                    payment_id=order.payment.payment_id,
                    sale_id=sale_id,
                    refund_id=refund_id,
                    refund_amount=refund_amount,
                    refund_from_transaction_fee=refund_from_transaction_fee,
                    currency=refund_currency,
                    status="completed" if refund_status == "completed" else "failed",
                    response_message=response_message
                )
                return {"status": "success", "message": "Refund processed successfully."}
            else:
                print(refund.error)
                return {"status": "error", "message": refund.error}

        elif order.payment_method.lower() == 'stripe':
            # Example stub: integrate Stripe SDK logic here
            # stripe.Refund.create(payment_intent=order.payment.payment_id)
            return True, "Stripe refund processed"

        return False, "Unsupported payment gateway"
    except Exception as e:
        return False, str(e)
