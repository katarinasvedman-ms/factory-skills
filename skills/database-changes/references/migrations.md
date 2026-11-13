# Migration checklist

Use the heading `Data safety` in database proposals. State whether the change
can lose data, which application versions remain compatible, and what happens
if a backfill stops partway through.

Prefer additive nullable fields and staged backfills over immediate destructive
renames or drops. State locking risks and how row counts/constraints will be
checked. A schema rollback does not automatically undo data transformations.
