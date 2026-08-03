.PHONY: validate-literature-citations audit test chat-bundle chat-bundle-check

validate-literature-citations:
	python -m autoassistant.literature validate-citations

# Symbol/idiom audit of skills + wiki against the installed stack.
audit:
	python autoassistant/audit_skill_apis.py

# Assistant tooling test suite (slow: the gate tests import autolens per case).
test:
	python -m pytest autoassistant/tests -q

# Regenerate the free-tier chat bundles (llms-chat.txt + chat_pack/).
# Run with the stack installed so the API surface is refreshed, not reused.
chat-bundle:
	python autoassistant/chat_bundle.py

# Verify the committed bundles are current and their invariants hold.
chat-bundle-check:
	python autoassistant/chat_bundle.py --check
