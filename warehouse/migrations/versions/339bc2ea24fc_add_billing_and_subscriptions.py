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
"""
add_billing_and_subscriptions

Revision ID: 339bc2ea24fc
Revises: 8bee9c119e41
Create Date: 2022-07-12 00:41:55.635862
"""

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

revision = "339bc2ea24fc"
down_revision = "8bee9c119e41"

# Note: It is VERY important to ensure that a migration does not lock for a
#       long period of time and to ensure that each individual migration does
#       not break compatibility with the *previous* version of the code base.
#       This is because the migrations will be ran automatically as part of the
#       deployment process, but while the previous version of the code is still
#       up and running. Thus backwards incompatible changes must be broken up
#       over multiple migrations inside of multiple pull requests in order to
#       phase them in over multiple deploys.
#
#       By default, migrations cannot wait more than 4s on acquiring a lock
#       and each individual statement cannot take more than 5s. This helps
#       prevent situations where a slow migration takes the entire site down.
#
#       If you need to increase this timeout for a migration, you can do so
#       by adding:
#
#           op.execute("SET statement_timeout = 5000")
#           op.execute("SET lock_timeout = 4000")
#
#       To whatever values are reasonable for this migration as part of your
#       migration.


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "subscription_products",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Text(), nullable=True),
        sa.Column("product_name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("tax_code", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "subscription_prices",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("price_id", sa.Text(), nullable=True),
        sa.Column("currency", sa.Text(), nullable=False),
        sa.Column(
            "subscription_product_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("unit_amount", sa.Integer(), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "recurring",
            sa.Enum("month", "year", "week", "day", name="subscriptionpriceinterval"),
            nullable=False,
        ),
        sa.Column("tax_behavior", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subscription_product_id"],
            ["subscription_products.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("customer_id", sa.Text(), nullable=False),
        sa.Column("subscription_id", sa.Text(), nullable=False),
        sa.Column(
            "subscription_price_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "past_due",
                "unpaid",
                "canceled",
                "incomplete",
                "incomplete_expired",
                "trialing",
                name="subscriptionstatus",
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["subscription_price_id"],
            ["subscription_prices.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "customer_id",
            "subscription_id",
            name="_subscription_customer_subscription_uc",
        ),
    )
    op.create_index(
        "subscriptions_customer_id_idx", "subscriptions", ["customer_id"], unique=False
    )
    op.create_index(
        "subscriptions_subscription_id_idx",
        "subscriptions",
        ["subscription_id"],
        unique=False,
    )
    op.create_table(
        "organization_subscription",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "subscription_id",
            name="_organization_subscription_organization_subscription_uc",
        ),
    )
    op.create_index(
        "organization_subscription_organization_id_idx",
        "organization_subscription",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "organization_subscription_subscription_id_idx",
        "organization_subscription",
        ["subscription_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "organization_subscription_subscription_id_idx",
        table_name="organization_subscription",
    )
    op.drop_index(
        "organization_subscription_organization_id_idx",
        table_name="organization_subscription",
    )
    op.drop_table("organization_subscription")
    op.drop_index("subscriptions_subscription_id_idx", table_name="subscriptions")
    op.drop_index("subscriptions_customer_id_idx", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_table("subscription_prices")
    op.drop_table("subscription_products")
    # ### end Alembic commands ###
