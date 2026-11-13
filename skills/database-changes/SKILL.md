---
name: database-changes
description: Plan, implement, review, or test SQL Server schema and query changes with data safety and compatibility. Use for database tasks, not unrelated source-only changes.
---

# Database changes

1. Read schema, migrations, data-access code, indexes, and transaction conventions.
   Identify affected readers/writers and deployment ordering.
2. Read [the migration checklist](references/migrations.md). Use expand/contract
   where old and new application versions may overlap.
3. Evaluate null/default semantics, backfill costs, locks, isolation, index use,
   and parameterized queries. Never generate destructive SQL casually.
4. Provide forward steps, validation queries, and a rollback or roll-forward
   strategy that accounts for data written after migration.
5. Propose focused integration cases for existing data, new writes, and failed
   migration recovery. Do not execute migrations or connect to a database
   without an explicitly authorized tool.
