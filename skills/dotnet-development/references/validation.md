# .NET validation checklist

For every proposal include a `Compatibility evidence` section with the observed
target framework, nullable setting (or "not specified"), and the relevant
project file path. This makes unsupported framework assumptions visible.

For a proposal that changes input validation, also include a `Behavior evidence`
section. Give at least one concrete invalid input and its proposed rejection
outcome, and one concrete valid input with its preserved expected output.
Identify the affected method and source path. Label these examples as proposed
or inspection-based unless an approved tool actually executed them; if executed,
cite the command and result. Keep validation marked NOT RUN when no executor
was available.

Check existing naming, dependency injection, async/cancellation conventions,
and test runner before proposing a change. Verify boundary inputs and preserve
existing HTTP and persistence contracts.

No command is authorized merely because this document mentions it.
