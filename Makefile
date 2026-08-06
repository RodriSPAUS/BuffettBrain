PY := python3
S  := scripts

.PHONY: hooks figures lint lint-strict lint-detail baseline check quotes links frontmatter structure coverage raw propagation new help

help:
	@echo "make hooks       install the pre-commit hook (do this once, per clone)"
	@echo "make lint        run every check (do this before closing an ingest)"
	@echo "                 fails only on NEW errors, not on the known backlog"
	@echo "make lint-strict fail on any error at all, ignoring the baseline"
	@echo "make lint-detail show every error, including the known ones"
	@echo "make baseline    re-record the backlog after fixing pages"
	@echo "make quotes      verify every quotation against the Raw/ file it cites"
	@echo "make links       broken wikilinks, phantom sources, orphans, fake anchors"
	@echo "make frontmatter page metadata against wiki/SCHEMA.md"
	@echo "make structure   required sections, outbound links, tag quality"
	@echo "make coverage    what the sources talk about that the wiki never mentions"
	@echo "make figures     numbers on a page vs the letter it cites"
	@echo "make raw         source-extraction quality gate on Raw/"
	@echo "make propagation are ingested sources reaching the compiled layer?"
	@echo ""
	@echo "Start a page with the schema already correct (never write frontmatter by hand):"
	@echo "  make new P=Sources/1978ltr"
	@echo "  make new P=Concepts/Moat"
	@echo ""
	@echo "Check ONE finished page with zero tolerance (do this after each letter):"
	@echo "  make check P=Sources/1996ltr"
	@echo ""
	@echo "One-off passes (pass ARGS=--dry-run first):"
	@echo "  make migrate     apply the AGENTS.md / SCHEMA.md conventions to existing pages"
	@echo "  make repair-raw  restore word boundaries in mangled Raw/ extractions"

hooks:
	@git config core.hooksPath .githooks
	@echo "pre-commit hook active: commits with unverifiable quotations will be refused"

lint:
	@cd $(S) && $(PY) lint.py

lint-strict:
	@cd $(S) && $(PY) lint.py --strict

lint-detail:
	@cd $(S) && $(PY) verify_quotes.py; $(PY) lint_links.py; $(PY) check_frontmatter.py; $(PY) check_structure.py

baseline:
	@cd $(S) && $(PY) lint.py --record

# Zero tolerance on a single page. The ratchet forgives errors a file already
# had, which is wrong for a page you just finished writing.
check:
	@cd $(S) && $(PY) check_coverage.py "$(P)"
	@cd $(S) && $(PY) check_figures.py "$(P)"
	@cd $(S) && $(PY) lint.py --page "$(P)"

quotes:
	@cd $(S) && $(PY) verify_quotes.py

links:
	@cd $(S) && $(PY) lint_links.py

frontmatter:
	@cd $(S) && $(PY) check_frontmatter.py

structure:
	@cd $(S) && $(PY) check_structure.py

coverage:
	@cd $(S) && $(PY) check_coverage.py $(P)

figures:
	@cd $(S) && $(PY) check_figures.py $(P)

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

# Scaffold a page: frontmatter and sections pre-filled, prose left as TODO.
.PHONY: new
new:
	@cd $(S) && $(PY) new_page.py "$(P)" $(ARGS)

# Find a citable passage: make quote Q="circle of competence"
.PHONY: quote
quote:
	@cd $(S) && $(PY) quote.py $(if $(Y),--year $(Y),) $(if $(C),--context $(C),) "$(Q)"
