#! /usr/bin/env python3.6
"""
Python 3.6 or newer required.
"""
import json
import stripe
import datetime
from flask import Flask, redirect, jsonify, request, send_from_directory
from flask_cors import CORS


stripe.api_key = "sk_test_51P6R0zG1Ea829cAu8IqrZlWChn6ABEt9BuuYpNwhbdFZQWrb1KhIXXXTJe0tr6gtBVQ8pw2qzCoNWw4VOctLVHkV00rMUCPnVn"

app = Flask(__name__, static_folder='public',
            static_url_path='', template_folder='public')

CORS(app)

SERVER_DOMAIN = 'http://localhost:4242'
CLIENT_DOMAIN = 'http://localhost:3000'

def convert_timestamp(date):
    return datetime.datetime.fromtimestamp(date).strftime('%Y.%m.%d %H:%M:%S')

def calculate_order_amount(items): # items : { id: "..." } []
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client

    # USD is two-decimal: 10$ == 1000
    return 1000

def get_stripe_customer_id(vox_id):
    # TODO: get corresponding stripe customer_id from DB
    return ""

# create payment : make one-time-pay intent
@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['items']),
            currency='USD',
            # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
            automatic_payment_methods={
                'enabled': True,
            },
        )
        response =  jsonify( {'clientSecret': intent['client_secret']} )
        response.headers['Content-Security-Policy'] = "deafult-src 'self'; connect-src https://*;"
        return response
    
    except Exception as e:
        return jsonify(error=str(e)), 403

# create checkout session : make checkout session for subscription
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # lookup_keys : Only return the price with these lookup_keys, if any exist.
        prices = stripe.Price.list(
            lookup_keys=[request.form['lookup_key']],
            expand=['data.product']
        )

        pay_mode = request.form['pay_type']

        customer_id = get_stripe_customer_id("voxfactory_id")
        if not customer_id:
            customer_id = stripe.Customer.create(
                name="test_name",
                email="test@email.com"
            ).id
            print("new customer:", customer_id)

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            allow_promotion_codes=True,
            custom_fields=[
                {
                    'key': 'field1',
                    'label': {
                        'custom': 'custom field1',
                        'type': 'custom'
                    },
                    'type': 'text', # 'dropdown' | 'numeric' | 'text'
                    'optional': False,
                    'text': {
                        'default_value': 'field 1',
                        'maximum_length': 30,
                        'minimum_length': 1
                    }
                }
            ],
            customer=customer_id,  # if blank in case of subscription & payment(customer_createion=always), it will create a new customer.
            mode=pay_mode,  # this is subscription or payment
            success_url=CLIENT_DOMAIN + '/redirection?success=true&mode='+pay_mode+'&session_id={CHECKOUT_SESSION_ID}', # when payment success
            cancel_url=CLIENT_DOMAIN + '/checkoutsubscription?canceled=true', # when user go back to previous page
        )
        return redirect(checkout_session.url, code=303)
    
    except Exception as e:
        print(e)
        return "Server error", 500

# create portal session : make portal session for user
@app.route('/create-portal-session', methods=['POST'])
def create_portal_session():
    try:
        # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
        # Typically this is stored alongside the authenticated user in your database.
        checkout_session_id = request.form.get('session_id')
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

        portalSession = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=CLIENT_DOMAIN,
        )
        return redirect(portalSession.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@app.route('/refund-payment', methods=['POST'])
def refund_payment():
    try:
        data = json.loads(request.data)

        refund = stripe.Refund.create(
            payment_intent=data['paymentIntent']
        )
    
    except Exception as e:
        return jsonify(error=str(e)), 403

# fulfill checkout : get the event data from "checkout.session.completed"
def fulfill_checkout(session_id):
    try:
        # Retrieve the Checkout Session from the API with line_items expanded
        checkout_session = stripe.checkout.Session.retrieve(
            session_id,
            expand=['line_items']
        )

        products = [{"id": item.price.product,
                    "price": item.price.unit_amount,
                    "currency": item.currency,
                    } for item in checkout_session.line_items.data]

        # Check the Checkout Session's payment_status property to determine if fulfillment should be peformed
        if checkout_session.payment_status != 'unpaid':
            return {
                "mode" : checkout_session.mode,                     # payment | subscription
                "transaction" : "purchase",                         # purchase | change | cancel
                "customer_id" : checkout_session.customer,          # id assigned by Stripe server
                "date" : convert_timestamp(checkout_session.created),                                      # Measured in seconds since the Unix epoch (1970.01.01. 09:00:00 GMT+0900)
                "date_expiry" : None,                
                "products" : products,
            }
    
    except Exception as e:
        print(e)
        return "Server error", 500

# fulfill payment intent : get the event data from "payment_intent.succeeded"
def fulfill_payment_intent(session_id):
    try:
        payment_intent = stripe.PaymentIntent.retrieve(
            session_id
        )

        return {
   	        'mode': payment_intent.description if payment_intent.description else 'payment',  # 'payment' | 'Subscription creation' | 'Subscription update'
   	        'customer_id': payment_intent.customer,  # it will be null if the user has not made any subscription before
            'payment_intent': payment_intent.id,  # it is needed due to the refund method.
            'date': convert_timestamp(payment_intent.created),
            'price': payment_intent.amount,
            'currency': payment_intent.currency,
        }

    except Exception as e:
        print(e)
        return "Server error", 500
    
# fulfill subscription : get the event datat from "customer.subscription.update"
def fulfill_subscription(session_id, transaction):
    try:
        date = 0 # date when the transaction was created
        date_expiry = None # date of expected expiry date

        subscription = stripe.Subscription.retrieve(
            session_id
        )

        products = [{"id": item.price.product,
                    "price": item.price.unit_amount,
                    "interval": item.price.recurring.interval,
                    "currency": item.price.currency,
                    } for item in subscription["items"].data]

        # case for plan cancel
        if (transaction == "cancel"):
            date = subscription.canceled_at
            date_expiry = convert_timestamp(subscription.cancel_at)
        # case for plan add & change
        else:
            date = subscription.created

        return {
            "transaction" : transaction,            # add | change | cancel
            "customer_id" : subscription.customer,  # id assigned by Stripe server
            "date" : convert_timestamp(date),
            "date_expiry" : date_expiry,
            "products" : products,
        }

    except Exception as e:
        print(e)
        return "Server error", 500
    
# Use the secret provided by Stripe CLI for local testing.
#   $ .\stripe listen --forward-to localhost:4242/webhook
#
# On the live mode, use your webhook endpoint's secret.
endpoint_secret = 'whsec_ef6b97d6c336879fd5efa57c46bd35a6243655d7c5fe7647c112f3efe448d4d4'

# webhook view : call whenever the Stripe server make a transaction of payment or subscription
@app.route('/webhook', methods=['POST'])
def webhook_view():
  payload = request.get_data(as_text=True)
  sig_header = request.headers.get('Stripe-Signature')
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return jsonify(success=False), 400
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return jsonify(success=False), 400
  
  # if (event['type'] in ['checkout.session.completed', 'checkout.session.async_payment_succeeded']):
  #   print(fulfill_checkout(event['data']['object']['id']))

  ## purchase information ##
  #
  # for each purchase, the webhook gets the information:
  # {
  # 	'mode': 'payment' | 'Subscription creation' | 'Subscription update',
  # 	'customer_id': string,
  #     'payment_intent': string,  # it is needed due to the refund method.
  #     'date': string,
  #     'price': number,
  #     'currency': string,
  # }

  if (event['type'] == 'payment_intent.succeeded'):
    print(fulfill_payment_intent(event['data']['object']['id']))

  ## subscription transaction information ##
  #
  # for each transaction, the webhook gets the information:
  # {
  # 	'transaction': 'add' | 'change' | 'cancel',
  # 	'customer_id': string,
  #     'email': string,
  #     'date': string,
  #     'date_expiry': string | None,
  #     'products': {
  #         'id': string,
  #         'price': number,
  #         'currency': string,         
  #     }[]
  # }

  if (event['type'] == 'customer.subscription.updated'):
    subscription_id = event['data']['object']['id']

    # change subscription
    if ("plan" in event['data']['previous_attributes'].keys()):
        print(fulfill_subscription(subscription_id, "change"))

    # cancel subscription
    elif (event['data']['object']['canceled_at']):
        # During cancelation, subscription.update is called twice: cancelation and cancelation feedback
        # One of them should be blocked.
        if ("cancel_at" in event['data']['previous_attributes'].keys()):
            print(fulfill_subscription(subscription_id, "cancel"))

    # add subscription
    else:
        print(fulfill_subscription(subscription_id, "add"))

  return jsonify(success=True), 200

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(port=4242)