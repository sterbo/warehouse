# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import pytest
import stripe

from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent, HTTPNotFound

from warehouse.api import billing

from ...common.db.organizations import (
    OrganizationFactory,
    OrganizationStripeCustomerFactory,
    OrganizationSubscriptionFactory,
)
from ...common.db.subscriptions import SubscriptionFactory


class TestHandleBillingWebhookEvent:
    # checkout.session.completed
    def test_handle_billing_webhook_event_checkout_complete_update(
        self, db_request, subscription_service
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )
        subscription = SubscriptionFactory.create(
            customer_id=organization_stripe_customer.customer_id
        )
        OrganizationSubscriptionFactory.create(
            organization=organization, subscription=subscription
        )

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": organization_stripe_customer.customer_id,
                    "status": "complete",
                    "subscription": subscription.subscription_id,
                },
            },
        }

        billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_checkout_complete_add(
        self, db_request, subscription_service
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": organization_stripe_customer.customer_id,
                    "status": "complete",
                    "subscription": "sub_12345",
                },
            },
        }

        billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_checkout_complete_invalid_status(
        self, db_request
    ):
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_1234",
                    "status": "invalid_status",
                    "subscription": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_checkout_complete_invalid_customer(
        self, db_request
    ):
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "",
                    "status": "complete",
                    "subscription": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_checkout_complete_invalid_subscription(
        self, db_request
    ):
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_1234",
                    "status": "complete",
                    "subscription": "",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    # customer.subscription.deleted
    def test_handle_billing_webhook_event_subscription_deleted_update(
        self, db_request, subscription_service
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )
        subscription = SubscriptionFactory.create(
            customer_id=organization_stripe_customer.customer_id
        )
        OrganizationSubscriptionFactory.create(
            organization=organization, subscription=subscription
        )

        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": organization_stripe_customer.customer_id,
                    "status": "canceled",
                    "id": subscription.subscription_id,
                },
            },
        }

        billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_deleted_not_found(
        self, db_request, subscription_service
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )

        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": organization_stripe_customer.customer_id,
                    "status": "canceled",
                    "id": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPNotFound):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_deleted_invalid_status(
        self, db_request
    ):
        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": "cus_1234",
                    "status": "invalid_status",
                    "id": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_deleted_invalid_customer(
        self, db_request
    ):
        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": "",
                    "status": "canceled",
                    "id": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_deleted_invalid_subscription(
        self, db_request
    ):
        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": "cus_1234",
                    "status": "canceled",
                    "id": "",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    # customer.subscription.updated
    def test_handle_billing_webhook_event_subscription_updated_update(
        self, db_request, subscription_service
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )
        subscription = SubscriptionFactory.create(
            customer_id=organization_stripe_customer.customer_id
        )
        OrganizationSubscriptionFactory.create(
            organization=organization, subscription=subscription
        )

        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "customer": organization_stripe_customer.customer_id,
                    "status": "canceled",
                    "id": subscription.subscription_id,
                },
            },
        }

        billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_updated_not_found(
        self, db_request, subscription_service
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )

        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "customer": organization_stripe_customer.customer_id,
                    "status": "canceled",
                    "id": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPNotFound):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_updated_no_change(
        self, db_request
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )
        subscription = SubscriptionFactory.create(
            customer_id=organization_stripe_customer.customer_id
        )
        OrganizationSubscriptionFactory.create(
            organization=organization, subscription=subscription
        )

        assert subscription.status == "active"

        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "customer": organization_stripe_customer.customer_id,
                    "status": "active",
                    "id": subscription.subscription_id,
                },
            },
        }

        billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_updated_invalid_status(
        self, db_request
    ):
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "customer": "cus_1234",
                    "status": "invalid_status",
                    "id": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_updated_invalid_customer(
        self, db_request
    ):
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "customer": "",
                    "status": "canceled",
                    "id": "sub_12345",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_subscription_updated_invalid_subscription(
        self, db_request
    ):
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "customer": "cus_1234",
                    "status": "canceled",
                    "id": "",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    # customer.deleted
    def test_handle_billing_webhook_event_customer_deleted(
        self, db_request, subscription_service
    ):
        organization = OrganizationFactory.create()
        organization_stripe_customer = OrganizationStripeCustomerFactory.create(
            organization=organization
        )
        subscription = SubscriptionFactory.create(
            customer_id=organization_stripe_customer.customer_id
        )
        OrganizationSubscriptionFactory.create(
            organization=organization, subscription=subscription
        )

        event = {
            "type": "customer.deleted",
            "data": {
                "object": {
                    "id": organization_stripe_customer.customer_id,
                },
            },
        }

        billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_customer_deleted_no_subscriptions(
        self, db_request
    ):
        event = {
            "type": "customer.deleted",
            "data": {
                "object": {
                    "id": "cus_12345",
                },
            },
        }

        with pytest.raises(HTTPNotFound):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_customer_deleted_invalid_customer(
        self, db_request
    ):
        event = {
            "type": "customer.deleted",
            "data": {
                "object": {
                    "id": "",
                },
            },
        }

        with pytest.raises(HTTPBadRequest):
            billing.handle_billing_webhook_event(db_request, event)

    def test_handle_billing_webhook_event_unmatched_event(self, db_request):
        event = {
            "type": "your.birthday",
            "data": {
                "object": {
                    "id": "day_1234",
                },
            },
        }

        billing.handle_billing_webhook_event(db_request, event)


class TestBillingWebhook:
    def test_billing_webhook(self, pyramid_request, billing_service, monkeypatch):
        pyramid_request.body = json.dumps({"type": "mock.webhook.payload"})
        pyramid_request.headers = {"Stripe-Signature": "mock-stripe-signature"}

        monkeypatch.setattr(
            billing_service,
            "webhook_received",
            lambda p, s: json.loads(p),
        )

        monkeypatch.setattr(
            billing, "handle_billing_webhook_event", lambda *a, **kw: None
        )

        result = billing.billing_webhook(pyramid_request)

        assert isinstance(result, HTTPNoContent)

    def test_billing_webhook_value_error(
        self, pyramid_request, billing_service, monkeypatch
    ):
        pyramid_request.body = json.dumps({"type": "mock.webhook.payload"})
        pyramid_request.headers = {"Stripe-Signature": "mock-stripe-signature"}

        def webhook_received(payload, sig_header):
            raise ValueError()

        monkeypatch.setattr(billing_service, "webhook_received", webhook_received)

        with pytest.raises(HTTPBadRequest):
            billing.billing_webhook(pyramid_request)

    def test_billing_webhook_signature_error(
        self, pyramid_request, billing_service, monkeypatch
    ):
        pyramid_request.body = json.dumps({"type": "mock.webhook.payload"})
        pyramid_request.headers = {"Stripe-Signature": "mock-stripe-signature"}

        def webhook_received(payload, sig_header):
            raise stripe.error.SignatureVerificationError("signature error", sig_header)

        monkeypatch.setattr(billing_service, "webhook_received", webhook_received)

        with pytest.raises(HTTPBadRequest):
            billing.billing_webhook(pyramid_request)
