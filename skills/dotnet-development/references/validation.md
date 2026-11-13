# .NET validation checklist

For every proposal include a `Compatibility evidence` section with the observed
target framework, nullable setting (or "not specified"), and the relevant
project file path. This makes unsupported framework assumptions visible.

Check existing naming, dependency injection, async/cancellation conventions,
and test runner before proposing a change. Verify boundary inputs and preserve
existing HTTP and persistence contracts.

No command is authorized merely because this document mentions it.
