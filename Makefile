PY := python3
S  := scripts

.PHONY: lint lint-strict lint-detail baseline quotes links frontmatter raw propagation help

help:
	@echo "make lint        run every check (do this before closing an ingest)"
	@echo "                 fails only on NEW errors, not on the known backlog"
	@echo "make lint-strict fail on any error at all, ignoring the baseline"
	@echo "make lint-detail show every error, including the known ones"
	@echo "make baseline    re-record the backlog after fixing pages"
	@echo "make quotes      verify every quotation against the Raw/ file it cites"
	@echo "make links       broken wikilinks, phantom sources, orphans, fake anchors"
	@echo "make frontmatter page metadata against wiki/SCHEMA.md"
	@echo "make raw         source-extraction quality gate on Raw/"
	@echo "make propagation are ingested sources reaching the compiled layer?"
	@echo ""
	@echo "Check one page or folder:"
	@echo "  $(PY) $(S)/verify_quotes.py wiki/Sources/1985ltr.md"
	@echo ""
	@echo "One-off passes (pass ARGS=--dry-run first):"
	@echo "  make migrate     apply AGENT.md/SCHEMA.md conventions to existing pages"
	@echo "  make repair-raw  restore word boundaries in mangled Raw/ extractions"

lint:
	@cd $(S) && $(PY) lint.py

lint-strict:
	@cd $(S) && $(PY) lint.py --strict

lint-detail:
	@cd $(S) && $(PY) verify_quotes.py; $(PY) lint_links.py; $(PY) check_frontmatter.py

baseline:
	@cd $(S) && $(PY) lint.py --record

quotes:
	@cd $(S) && $(PY) verify_quotes.py

links:
	@cd $(S) && $(PY) lint_links.py

frontmatter:
	@cd $(S) && $(PY) check_frontmatter.py

raw:
	@cd $(S) && $(PY) check_raw_quality.py

propagation:
	@cd $(S) && $(PY) check_propagation.py

# One-off passes, not part of `make lint`.
.PHONY: migrate repair-raw

migrate:
	@cd $(S) && $(PY) migrate_conventions.py $(ARGS)

repair-raw:
	@cd $(S) && $(PY) repair_raw_spacing.py $(ARGS)

# Find a citable passage: make quote Q="circle of competence"
.PHONY: quote
quote:
	@cd $(S) && $(PY) quote.py $(if $(Y),--year $(Y),) $(if $(C),--context $(C),) "$(Q)"
