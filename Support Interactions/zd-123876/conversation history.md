# Conversation History: WooCommerce Debugging & Duplicate Orders

**Customer:** Mummy Liz
**Support Rep:** Daniel Danilov
**Date Range:** April 5–7, 2025
**Topic:** Difficulty enabling debugging; duplicated Stripe orders #9986 and #9998

---

### 📩 April 5, 2025 — Initial Inquiry

> **Mummy Liz:**
> I am not able to perform step 6 to turn on Debugging. I see the following under WooCommerce > Settings > Advanced:
> `SCR-20250405-nek.png`
> May I know where the Debugging option is?

---

### 🛠 April 6, 2025 — Support Reply from Daniel

> **Daniel Danilov:**
> Thanks for reaching out!
>
> It looks like the AI response may have misdirected you. To enable logging:
> - Go to **WooCommerce > Status > Logs**
>   [Direct link to logs](https://mummylizbakes.com/wp-admin/admin.php?page=wc-status&tab=logs&view=settings)
>
> For debugging features:
> - Go to **WooCommerce > Settings > Advanced > Features**
>   [Direct link to features](https://mummylizbakes.com/wp-admin/admin.php?page=wc-settings&tab=advanced§ion=features)
> - Enable:
>   *"Enable this feature to log errors and related data to Automattic servers for debugging purposes and to improve WooCommerce"*

---

### 📩 April 7, 2025 — Customer Follow-up with Logs

> **Mummy Liz (Calvin):**
> Thanks for the reply. I’ve attached the logs.
>
> Can you help check if there were problems with:
> - Order #9986 (April 3)
> - Order #9998 (April 5)
>
> Customers reported errors and repeated their orders (#9987 and #9999 respectively).

---

### 🔍 April 7, 2025 — Log Review by Daniel

> **Daniel Danilov:**
> Thanks for sharing the logs and details.
>
> For **Order #9986**:
> - `transaction_id` is empty → suggests payment wasn’t captured.
> - Stripe logs show a `payment_intents` request and customer object, but no confirmation of success.
>
> Possible causes:
> - User closed the browser or frontend error during Stripe confirmation.
>
> Suggested next steps:
> - Check **Stripe Dashboard** around `2025-04-03 01:14 UTC` for incomplete payment_intents.
> - Review **webhook logs** in Stripe: `payment_intent.succeeded`
> - Enable **detailed Stripe logging** in WooCommerce:
>   - WooCommerce > Settings > Payments > Stripe > Settings > Advanced
> - Reproduce and monitor via WooCommerce > Status > Logs
> - Consider testing in default theme (e.g., Storefront) to rule out JS conflicts
>
> This seems isolated so far, but let us know if it recurs.
> FULL REPLY:

Hi there!

Thanks for following up and sharing the log details.

From what you've described, customers encountered an error on orders #9986 (Apr 3) and #9998 (Apr 5), which led them to place duplicate orders #9987 and #9999. I reviewed the Stripe debug logs and order metadata for #9986, and here’s what I noticed:

The transaction_id field is empty in the order data, which usually means payment wasn’t successfully captured.
The debug logs show a Stripe payment_intents request was made for order #9986 using payment method pm_1R9cMjIgxmLk6owS4anjMeeB, and a customer object was also returned. However, there’s no corresponding confirmation that the payment was successful or a response indicating failure.
This could mean the customer was redirected or closed the browser mid-transaction, or that there was a frontend error during the Stripe confirmation step.

Here’s what you can do to investigate further:

Check your Stripe dashboard for payment_intents created around 2025-04-03 01:14 UTC. See if there’s a failed or incomplete payment linked to order #9986.
Review browser console logs or Stripe webhook logs (under Developers > Webhooks in Stripe) to confirm whether the webhook for payment_intent.succeeded was sent and received.
For a clearer audit trail, enable detailed logging in WooCommerce > Settings > Payments > Stripe > Settings > Advanced settings, then reproduce the error if possible. This can help with future investigations if the issue occurs again.
Then head to: WooCommerce > Status > Logs to review what’s captured moving forward.
Consider installing a logging plugin like WP Crontrol to inspect whether the wc_stripe_process_payment and woocommerce_payment_complete hooks are firing as expected.
If this turns out to be a frontend conflict (e.g., theme or JS conflict during Stripe confirmation), you may want to test a purchase in a default theme like Storefront with only WooCommerce and Stripe enabled. However, this depends on the severity of the problem. If this only happened to a single customer, it was most likely an error on their end within their browser. However, if this happens frequently, that's likely a configuration conflict in your own site.

I hope this helps. Please let us know if you have any other questions.


---

### 📩 April 7, 2025 — Customer Disagrees with Diagnosis

> **Mummy Liz (Calvin):**
> Thanks again.
>
> Just to clarify:
> - **Advanced logging was already enabled**.
> - The logs I sent are from **WooCommerce > Status > Logs**.
>
> Re: **Order #9986**, I do see successful payment confirmation in the logs:
> - Log contains: `Webhook received: charge.succeeded`
> - `amount_captured`: 12790
> - `captured: true`
> - `status: succeeded`
> - `seller_message: Payment complete.`
>
> Also, the `transaction_id` is missing across **other successful orders** too (e.g., #9992).
>
> Issue only affects a **small, irregular subset** of orders — hence I’d appreciate advice on **any other areas** to investigate.
> See `stripe_order_note.png` as an example
> Full reply:

Hi

Thanks for the quick reply.

The advanced logging setting had already been enabled. The logs I had sent earlier were from WooCommerce > Status > Logs as you have indicated.

SCR-20250407-q3v.png


I am a bit confused as to your observations though. For instance, you mentioned that there was no confirmation that the payment was successfully completed. Here are the stripe payment intent messages for order #9986 which showed that the order was completed. Below I have also extracted out the relevant lines which indicate the same.
SCR-20250407-q8z.png


Within the logs you had inspected, I found these lines in the log which indicated successful completion:

025-04-03T01:14:51+00:00 DEBUG Webhook received: charge.succeeded
2025-04-03T01:14:51+00:00 DEBUG Webhook body: {
  "id": "evt_3R9cMmIgxmLk6owS0SWDENWQ",
  "object": "event",
  "api_version": "2024-06-20",
  "created": 1743642890,
  "data": {
    "object": {
      "id": "ch_3R9cMmIgxmLk6owS0YF1dJSc",
      "object": "charge",
      "amount": 12790,
      "amount_captured": 12790,
      "amount_refunded": 0,
      "application": "ca_BC3QvYOCCxiOW3Klo6zL8KlBgSHzwTKn",
      "application_fee": null,
      "application_fee_amount": null,
      "balance_transaction": "txn_3R9cMmIgxmLk6owS0Mte5r7h",
      "billing_details": {
        "address": {
          "city": null,
          "country": "SG",
          "line1": "128 Beach Rd, #21-01 Guoco Midtown, Singapore 189773",
          "line2": "",
          "postal_code": "189773",
          "state": null
        },
        "email": "machiav3llian@gmail.com",
        "name": "Xuan Ren Chen",
        "phone": "83686891"
      },
      "calculated_statement_descriptor": "MUMMYLIZ* O #9986",
      "captured": true,
      "created": 1743642889,
      "currency": "sgd",
      "customer": "cus_S3jq1IipvFObFS",
      "description": "Mummy Liz Bakes - Order 9986",
      "destination": null,
      "dispute": null,
      "disputed": false,
      "failure_balance_transaction": null,
      "failure_code": null,
      "failure_message": null,
      "fraud_details": {
      },
      "invoice": null,
      "livemode": true,
      "metadata": {
        "order_key": "wc_order_IUwvSfjVCkqA4",
        "tax_amount": "0",
        "site_url": "https://mummylizbakes.com",
        "customer_email": "machiav3llian@gmail.com",
        "signature": "9986:a2a91a99a3153f144ae35fe2ba641162",
        "customer_name": "Xuan Ren Chen",
        "order_id": "9986",
        "payment_type": "single"
      },
      "on_behalf_of": null,
      "order": null,
      "outcome": {
        "advice_code": null,
        "network_advice_code": null,
        "network_decline_code": null,
        "network_status": "approved_by_network",
        "reason": null,
        "risk_level": "normal",
        "seller_message": "Payment complete.",
        "type": "authorized"
      },
      "paid": true,
      "payment_intent": "pi_3R9cMmIgxmLk6owS0WTdcc6H",
      "payment_method": "pm_1R9cMjIgxmLk6owS4anjMeeB",
      "payment_method_details": {
        "card": {
          "amount_authorized": 12790,
          "authorization_code": "T99205",
          "brand": "mastercard",
          "checks": {
            "address_line1_check": "unavailable",
            "address_postal_code_check": "unavailable",
            "cvc_check": "pass"
          },
          "country": "SG",
          "exp_month": 2,
          "exp_year": 2027,
          "extended_authorization": {
            "status": "disabled"
          },
          "fingerprint": "ZTJtIsFxjPVhANXW",
          "funding": "credit",
          "incremental_authorization": {
            "status": "unavailable"
          },
          "installments": null,
          "last4": "9264",
          "mandate": null,
          "multicapture": {
            "status": "unavailable"
          },
          "network": "mastercard",
          "network_token": {
            "used": false
          },
          "network_transaction_id": "WMRYS17N40402",
          "overcapture": {
            "maximum_amount_capturable": 12790,
            "status": "unavailable"
          },
          "regulated_status": "unregulated",
          "three_d_secure": null,
          "wallet": null
        },
        "type": "card"
      },
      "radar_options": {
      },
      "receipt_email": null,
      "receipt_number": null,
      "receipt_url": "https://pay.stripe.com/receipts/payment/CAcQARoXChVhY2N0XzFLYVdZNklneG1MazZvd1MoisK3vwYyBrVCQdkknDosFsu9i4TLi_OJ4kkmdEGMy--3BGoWuelPUWsZn4mIPkW14CHCWrwVY-PEfLY",
      "refunded": false,
      "review": null,
      "shipping": {
        "address": {
          "city": "",
          "country": "SG",
          "line1": "128 Beach Rd, #21-01 Guoco Midtown, Singapore 189773",
          "line2": "",
          "postal_code": "189773",
          "state": ""
        },
        "carrier": null,
        "name": "Xuan Ren Chen",
        "phone": null,
        "tracking_number": null
      },
      "source": null,
      "source_transfer": null,
      "statement_descriptor": null,
      "statement_descriptor_suffix": "O #9986",
      "status": "succeeded",
      "transfer_data": null,
      "transfer_group": null
    }
  },
  "livemode": true,
  "pending_webhooks": 1,
  "request": {
    "id": "req_G1SGRlH4TcxnfZ",
    "idempotency_key": "afce4896-0b7b-478b-bcfd-87ce8b48f9be"
  },
  "type": "charge.succeeded"
}

Regarding the missing transaction_Id, we note that there is a value for the balance_transaction in the logs as highlighted above. Also, the transaction_id records are blank for the other orders which have successfully completed too such as for order #9992 in the same logs.

Please note also that the issue occurs only for a small fraction of the monthly transactions in an intermittent and irregular way. Hence, the reason for reaching out to see if there are any other areas to look into.

Appreciate your help to shed further light on this. Thank you!

---

### ✅ Current Status

- Debugging and logging are enabled.
- Customer confirmed that Stripe logs indicate **successful payment** for order #9986.
- Issue appears **intermittent** and not tied to `transaction_id` field alone.
- Awaiting further suggestions or systemic insights from support.

---