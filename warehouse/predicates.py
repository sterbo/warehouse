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

from typing import List

from pyramid import predicates
from pyramid.exceptions import ConfigurationError
from pyramid.util import is_same_domain

from warehouse.admin.flags import AdminFlagValue
from warehouse.organizations.models import OrganizationType


class DomainPredicate:
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "domain = {!r}".format(self.val)

    phash = text

    def __call__(self, info, request):
        # Support running under the same instance for local development and for
        # test.pypi.io which will continue to host it's own uploader.
        if self.val is None:
            return True

        return is_same_domain(request.domain, self.val)


class HeadersPredicate:
    def __init__(self, val: List[str], config):
        if not val:
            raise ConfigurationError(
                "Excpected at least one value in headers predicate"
            )

        self.sub_predicates = [
            predicates.HeaderPredicate(subval, config) for subval in val
        ]

    def text(self):
        return ", ".join(sub.text() for sub in self.sub_predicates)

    phash = text

    def __call__(self, context, request):
        return all(sub(context, request) for sub in self.sub_predicates)


class ActiveOrganizationPredicate:
    def __init__(self, val, config):
        self.val = bool(val)

    def text(self):
        return f"require_active_organization = {self.val}"

    phash = text

    def __call__(self, organization, request):
        if self.val is False:
            return True

        return (
            # Organization accounts are enabled.
            not request.flags.enabled(AdminFlagValue.DISABLE_ORGANIZATIONS)
            # Organization is active.
            and organization.is_active
            # Organization has active subscription if it is a Company.
            and (
                organization.orgtype != OrganizationType.Company
                or organization.active_subscription
            )
        )


def includeme(config):
    config.add_route_predicate("domain", DomainPredicate)
    config.add_view_predicate("require_headers", HeadersPredicate)
    config.add_view_predicate(
        "require_active_organization", ActiveOrganizationPredicate
    )
