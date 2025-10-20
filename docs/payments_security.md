

# Retail — Payments & Security Conceptual Note

## 1. Payment Gateway Integration

The checkout system is designed to integrate with a **UPI/GPay payment flow** for simplicity and speed during the demo:

* When the user presses **`p`** in the detection interface:

  1. All items currently in the cart are packaged into a JSON payload.
  2. The payload includes:

     * `items`: list of item names and prices
     * `payment_method`: `"UPI"` or `"GPay"`
     * `upi_id`: user’s UPI ID (e.g., `user@upi`)
     * `total_amount`: sum of all item prices
  3. The backend receives this request at the `/checkout` endpoint.
  4. A **mock transaction ID** is generated to simulate payment confirmation.
  5. The transaction status and ID are returned to the detection interface and displayed on the cart overlay.

This approach demonstrates the **end-to-end flow from item detection → cart logging → payment confirmation**.

---

## 2. Security Measures

To ensure secure operations, the following measures are recommended:

1. **Secure Communication (HTTPS)**

   * All API requests (add item, checkout) should be sent over HTTPS to prevent eavesdropping and man-in-the-middle attacks.

2. **Token-Based Authentication**

   * Each client (detection script) is assigned a secure API token.
   * All requests include this token in headers, ensuring only authorized clients can log items or trigger checkout.

3. **Encrypted Storage**

   * Cart items, prices, and transaction IDs are stored in **encrypted format** in the database.
   * Sensitive fields like UPI IDs are never logged in plain text.

4. **Input Validation**

   * All API inputs are validated using Pydantic models in FastAPI.
   * Prevents invalid or malicious data from corrupting the backend.

---

## 3. Privacy-First Data Handling

Privacy of users is a priority. Measures include:

* **Minimal Data Storage:** Only store item names, prices, paid status, and transaction IDs.
* **No Personal Identifiers:** UPI IDs are optional for the demo and not stored persistently.
* **Cart Reset Option:** Users can reset or clear their cart at any time (`r` key in detection interface).
* **Transparent Flow:** All operations (item detection, checkout) are visible on-screen in real-time.

---

## 4. Demo Implementation Notes

* The detection interface shows a live **cart overlay** with item names, counts, total price, and mock transaction status.
* Pressing **`p`** triggers the checkout and mock payment flow.
* The backend records items and marks them as paid for demonstration purposes.
* This setup demonstrates **conceptual integration of CV checkout + payment + secure handling**, suitable for a 3-day technical evaluation.

---

✅ **Deliverable:** Markdown file (`docs/payments_security.md`) ready for submission.


