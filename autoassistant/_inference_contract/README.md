# Pinned inference validators

These standard-library modules are vendored from the public PyAutoInsight
`insight/summary.py` and `insight/catalogue.py` at the commit declared in
`provenance.json`. Only import paths and the attribution header changed. They
validate declarations, not scientific quality or artifact bytes. The consumer
supports only v2 even though the shared validator also understands v1.

`provenance.json` records source and vendored SHA-256 hashes. The test suite
checks vendored hashes; source drift is detectable by comparing each declared
`source_path` against its hash in an explicitly pinned Insight checkout.

To refresh: review the public contract change and affected consumers; pin a
full source commit; copy both modules together; adapt only package imports;
update the attribution headers and both hashes. Update contract fixtures and
run consumer tests and the complete assistant suite. Never refresh silently or
use the latest package at runtime. No producer summary is duplicated here;
the synthetic test fixture is not scientific evidence.
