PY := python3
S  := scripts

.PHONY: lint quotes links frontmatter raw help

help:
	@echo "make lint        run every check (do this before closing an ingest)"
	@echo "make quotes      verify every quotation against the Raw/ file it cites"
	@echo "make links       broken wikilinks, phantom sources, orphans, fake anchors"
	@echo "make frontmatter page metadata against wiki/SCHEMA.md"
	@echo "make raw         source-extraction quality gate on Raw/"
	@echo ""
	@echo "Check one page or folder:"
	@echo "  $(PY) $(S)/verify_quotes.py wiki/Sources/1985ltr.md"
	@echo ""
	@echo "One-off passes (pass ARGS=--dry-run first):"
	@echo "  make migrate     apply AGENT.md/SCHEMA.md conventions to existing pages"
	@echo "  make repair-raw  restore word boundaries in mangled Raw/ extractions"

lint:
	@cd $(S) && $(PY) lint.py

quotes:
	@cd $(S) && $(PY) verify_quotes.py

links:
	@cd $(S) && $(PY) lint_links.py

frontmatter:
	@cd $(S) && $(PY) check_frontmatter.py

raw:
	@cd $(S) && $(PY) check_raw_quality.py

# One-off passes, not part of `make lint`.
.PHONY: migrate repair-raw

migrate:
	@cd $(S) && $(PY) migrate_conventions.py $(ARGS)

repair-raw:
	@cd $(S) && $(PY) repair_raw_spacing.py $(ARGS)
