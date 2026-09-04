"""create core schema

Revision ID: 708347567601
Revises:
Create Date: 2026-09-04 16:04:27.532974

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "708347567601"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

artifact_kind = sa.Enum("text", "document", "json", name="artifactkind")
context_item_kind = sa.Enum("file", "verified_fact", name="contextitemkind")
workflow_run_status = sa.Enum(
    "pending",
    "running",
    "waiting_for_input",
    "completed",
    "failed",
    "cancelled",
    name="workflowrunstatus",
)
step_run_status = sa.Enum(
    "pending",
    "running",
    "waiting_for_input",
    "completed",
    "failed",
    "skipped",
    name="steprunstatus",
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("storage_ref", sa.String(), nullable=False),
        sa.Column("sha256", sa.String(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
    )
    op.create_index("ix_documents_sha256", "documents", ["sha256"], unique=True)

    op.create_table(
        "prompts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_prompts"),
        sa.UniqueConstraint("name", name="uq_prompts_name"),
    )

    op.create_table(
        "workflows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflows"),
    )

    op.create_table(
        "contexts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_contexts_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_contexts"),
    )
    op.create_index("ix_contexts_user_id", "contexts", ["user_id"])

    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prompt_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("template", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["prompt_id"], ["prompts.id"], name="fk_prompt_versions_prompt_id_prompts"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_prompt_versions"),
        sa.UniqueConstraint("prompt_id", "version", name="uq_prompt_versions_prompt_id"),
    )
    op.create_index("ix_prompt_versions_prompt_id", "prompt_versions", ["prompt_id"])

    op.create_table(
        "workflow_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"], ["workflows.id"], name="fk_workflow_versions_workflow_id_workflows"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_versions"),
        sa.UniqueConstraint("workflow_id", "version", name="uq_workflow_versions_workflow_id"),
    )
    op.create_index("ix_workflow_versions_workflow_id", "workflow_versions", ["workflow_id"])

    op.create_table(
        "context_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("context_id", sa.Uuid(), nullable=False),
        sa.Column("kind", context_item_kind, nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("statement", sa.Text(), nullable=True),
        sa.Column("source_item_id", sa.Uuid(), nullable=True),
        sa.Column("evidence_quote", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            """
            (kind = 'file' AND document_id IS NOT NULL
                AND statement IS NULL AND source_item_id IS NULL AND evidence_quote IS NULL) OR
            (kind = 'verified_fact' AND document_id IS NULL
                AND statement IS NOT NULL AND source_item_id IS NOT NULL
                AND evidence_quote IS NOT NULL)
            """,
            name="fact_needs_source",
        ),
        sa.ForeignKeyConstraint(
            ["context_id"], ["contexts.id"], name="fk_context_items_context_id_contexts"
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"], name="fk_context_items_document_id_documents"
        ),
        sa.ForeignKeyConstraint(
            ["source_item_id"],
            ["context_items.id"],
            name="fk_context_items_source_item_id_context_items",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_context_items"),
    )
    op.create_index("ix_context_items_context_id", "context_items", ["context_id"])

    op.create_table(
        "workflow_nodes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_version_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("position_x", sa.Float(), nullable=False),
        sa.Column("position_y", sa.Float(), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_version_id"],
            ["workflow_versions.id"],
            name="fk_workflow_nodes_workflow_version_id_workflow_versions",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_nodes"),
    )
    op.create_index(
        "ix_workflow_nodes_workflow_version_id", "workflow_nodes", ["workflow_version_id"]
    )

    op.create_table(
        "workflow_edges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_version_id", sa.Uuid(), nullable=False),
        sa.Column("from_node_id", sa.Uuid(), nullable=False),
        sa.Column("from_port", sa.String(), nullable=False),
        sa.Column("to_node_id", sa.Uuid(), nullable=False),
        sa.Column("to_port", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_version_id"],
            ["workflow_versions.id"],
            name="fk_workflow_edges_workflow_version_id_workflow_versions",
        ),
        sa.ForeignKeyConstraint(
            ["from_node_id"],
            ["workflow_nodes.id"],
            name="fk_workflow_edges_from_node_id_workflow_nodes",
        ),
        sa.ForeignKeyConstraint(
            ["to_node_id"],
            ["workflow_nodes.id"],
            name="fk_workflow_edges_to_node_id_workflow_nodes",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_edges"),
    )
    op.create_index(
        "ix_workflow_edges_workflow_version_id", "workflow_edges", ["workflow_version_id"]
    )

    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_version_id", sa.Uuid(), nullable=False),
        sa.Column("status", workflow_run_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_version_id"],
            ["workflow_versions.id"],
            name="fk_workflow_runs_workflow_version_id_workflow_versions",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_runs"),
    )
    op.create_index(
        "ix_workflow_runs_workflow_version_id", "workflow_runs", ["workflow_version_id"]
    )

    op.create_table(
        "step_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("node_id", sa.Uuid(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("status", step_run_status, nullable=False),
        sa.Column("prompt_version_id", sa.Uuid(), nullable=True),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["run_id"], ["workflow_runs.id"], name="fk_step_runs_run_id_workflow_runs"
        ),
        sa.ForeignKeyConstraint(
            ["node_id"], ["workflow_nodes.id"], name="fk_step_runs_node_id_workflow_nodes"
        ),
        sa.ForeignKeyConstraint(
            ["prompt_version_id"],
            ["prompt_versions.id"],
            name="fk_step_runs_prompt_version_id_prompt_versions",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_step_runs"),
        sa.UniqueConstraint("run_id", "node_id", "attempt", name="uq_step_runs_run_id"),
    )
    op.create_index("ix_step_runs_run_id_status", "step_runs", ["run_id", "status"])

    op.create_table(
        "artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", artifact_kind, nullable=False),
        sa.Column("produced_by_step_run_id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("json_schema_id", sa.String(), nullable=True),
        sa.Column("json_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            """
            (kind = 'text' AND text IS NOT NULL
                AND document_id IS NULL AND json_data IS NULL) OR
            (kind = 'document' AND document_id IS NOT NULL
                AND text IS NULL AND json_data IS NULL) OR
            (kind = 'json' AND json_data IS NOT NULL
                AND text IS NULL AND document_id IS NULL)
            """,
            name="payload_matches_kind",
        ),
        sa.ForeignKeyConstraint(
            ["produced_by_step_run_id"],
            ["step_runs.id"],
            name="fk_artifacts_produced_by_step_run_id_step_runs",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"], name="fk_artifacts_document_id_documents"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_artifacts"),
    )
    op.create_index(
        "ix_artifacts_produced_by_step_run_id", "artifacts", ["produced_by_step_run_id"]
    )


def downgrade() -> None:
    op.drop_table("artifacts")
    op.drop_table("step_runs")
    op.drop_table("workflow_runs")
    op.drop_table("workflow_edges")
    op.drop_table("workflow_nodes")
    op.drop_table("context_items")
    op.drop_table("workflow_versions")
    op.drop_table("prompt_versions")
    op.drop_table("contexts")
    op.drop_table("workflows")
    op.drop_table("prompts")
    op.drop_table("documents")
    op.drop_table("users")

    bind = op.get_bind()
    for enum_type in (step_run_status, workflow_run_status, context_item_kind, artifact_kind):
        enum_type.drop(bind, checkfirst=True)
