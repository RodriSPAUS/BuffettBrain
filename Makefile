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
