.PHONY: validate-literature-citations audit test colab colab-contexts

validate-literature-citations:
	python -m autoassistant.literature validate-citations

# Symbol/idiom audit of skills + wiki against the installed stack.
audit:
	python autoassistant/audit_skill_apis.py

# Assistant tooling test suite (slow: the gate tests import autolens per case),
# plus the one-shot prompt freeze (card hashes vs benchmarks/VERSIONS.lock).
test:
	python -m pytest autoassistant/tests -q
	python autoassistant/benchmark.py freeze-check

# colab/contexts.yaml: mapped skills exist and every entry fits the 20k Gemini cap.
colab-contexts:
	python -m autoassistant.colab_contexts check

# Rebuild the executed Colab notebook from its source: the static figures it shows before
# the code, the conversion (stamping its Colab Gemini instruction from colab/contexts.yaml),
# then a full execution so every code cell carries its output.
# Jupyter runs a notebook from its own folder, so it is executed from a copy at the
# repository root (where `dataset/` and `scripts/` resolve) and moved back.
PYAUTOHANDS_PATH ?= $(if $(PYAUTO_HANDS),$(PYAUTO_HANDS),../PyAutoHands)
# Maintainers supply a PyAutoHands checkout (or set PYAUTOHANDS_PATH).
COLAB_SOURCE = docs/colab/cosmos_web_ring_colab.py
COLAB_NOTEBOOK = docs/colab/cosmos_web_ring_colab.ipynb

colab:
	PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1 python docs/colab/make_colab_figures.py
	python -m autoassistant.to_notebook $(COLAB_SOURCE) $(COLAB_NOTEBOOK) \
		--gemini-context autolens_assistant/$(COLAB_NOTEBOOK) \
		--colab-setup "$(PYAUTOHANDS_PATH)"
	cp $(COLAB_NOTEBOOK) _colab_execute.ipynb
	PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1 jupyter nbconvert --to notebook --execute --inplace \
		--ExecutePreprocessor.timeout=1800 _colab_execute.ipynb
	mv _colab_execute.ipynb $(COLAB_NOTEBOOK)
