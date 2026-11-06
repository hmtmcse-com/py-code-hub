import asyncio

import aiohttp


class ShurjoPay:
    def __init__(self, username, password, prefix, sandbox=True):
        self.username = username
        self.password = password
        self.prefix = prefix

        self.base_url = (
            "https://sandbox.shurjopayment.com/api"
            if sandbox
            else "https://engine.shurjopayment.com/api"
        )

    async def _post(self, endpoint, data, token=None):
        headers = {"Accept": "application/json"}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/{endpoint}",
                data=data,
                headers=headers,
            ) as response:
                content = await response.text()

                print("Status:", response.status)
                print("Content:", content)
                response.raise_for_status()
                return await response.json(content_type=None)

    async def get_token(self):
        result = await self._post(
            "get_token",
            {
                "username": self.username,
                "password": self.password,
            },
        )

        if not result.get("token"):
            raise Exception(f"Authentication failed: {result}")

        return result

    async def create_payment(
        self,
        order_id,
        amount,
        name,
        phone,
        email,
        address,
        city,
        return_url,
        cancel_url,
        currency="BDT",
    ):
        auth = await self.get_token()

        data = {
            "prefix": self.prefix,
            "token": auth["token"],
            "store_id": auth["store_id"],
            "order_id": order_id,
            "amount": str(amount),
            "currency": currency,
            "client_ip": "10.0.40.1",
            "customer_name": name,
            "customer_phone": phone,
            "customer_email": email,
            "customer_address": address,
            "customer_city": city,
            "customer_post_code": "5400",
            "customer_country": "BD",
            "return_url": return_url,
            "cancel_url": cancel_url,
        }

        result = await self._post(
            "secret-pay",
            data,
            token=auth["token"],
        )

        if not result.get("checkout_url"):
            raise Exception(f"Payment creation failed: {result}")

        return result

    async def verify_payment(self, sp_order_id):
        auth = await self.get_token()

        result = await self._post(
            "verification",
            {"order_id": sp_order_id},
            token=auth["token"],
        )

        if not isinstance(result, list) or not result:
            raise Exception(f"Payment verification failed: {result}")

        return result[0]


# =========================
# TEST
# =========================

async def main():
    pay = ShurjoPay(
        username="sp_sandbox",
        password="pyyk97hu&6u6",
        prefix="PSR",
        sandbox=True,
    )

    payment = await pay.create_payment(
        order_id="INV-1001",
        amount=500,
        name="Test Customer",
        phone="01700000000",
        email="test@example.com",
        address="Rangpur",
        city="Rangpur",
        return_url="https://example.com/payment/return",
        cancel_url="https://example.com/payment/cancel",
    )

    print("Payment:", payment)
    print("Checkout URL:", payment["checkout_url"])

    # After completing checkout, use the returned sp_order_id.
    # Uncomment the following lines to verify:
    #
    # result = await pay.verify_payment(payment["sp_order_id"])
    # print("Verification:", result)
    # print("Successful:", str(result.get("sp_code")) == "1000")


if __name__ == "__main__":
    asyncio.run(main())