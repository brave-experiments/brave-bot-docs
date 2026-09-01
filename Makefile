# Local development for the Brave Bot documentation site.
#
# The site is plain Docusaurus, so most targets here are thin wrappers over an npm script
# and exist so there is one place to look. The two that are not are `init`, which installs
# the checked-in agent configuration where each tool looks for it, and the docs-ref
# targets, which track how far behind brave-bot this site has fallen.

# Where the brave-bot checkout lives. Exported because docs-ref.py reads it.
BRAVE_BOT_REPO ?= ../brave-bot
export BRAVE_BOT_REPO

DOCS_REF = python3 agents/skills/update-docs/docs-ref.py

.PHONY: help
help:
	@echo "Brave Bot documentation"
	@echo
	@echo "Development:"
	@echo "  make init                 Install dependencies, then link agents/ into .claude/ and .bravebot/"
	@echo "  make install              Install dependencies only"
	@echo "  make start                Serve locally with live reload"
	@echo "  make build                Build the static site into build/"
	@echo "  make serve                Serve the built site from build/"
	@echo "  make check                What CI checks: a clean build with no broken links"
	@echo "  make clear                Drop the Docusaurus cache"
	@echo "  make clean                Drop build output, cache, and node_modules"
	@echo
	@echo "Agent configuration:"
	@echo "  make agents               Show which links make init would create, and their state"
	@echo "  make unlink               Remove the links make init created"
	@echo
	@echo "Tracking brave-bot:"
	@echo "  make docs-updated-to-sha  The brave-bot commit these docs are current as of"
	@echo "  make docs-changes         What has landed in brave-bot since that commit"
	@echo "  make docs-changes-full    The same, with commit bodies and file lists"
	@echo
	@echo "  BRAVE_BOT_REPO = $(BRAVE_BOT_REPO)"

# agents/ is the checked-in source of truth for skills and AGENTS.md, and no tool reads it:
# Claude Code looks under .claude/ and bravebot under .bravebot/ and the workspace root.
# This creates the symlinks that bridge them. The links are gitignored, so a fresh clone
# needs it once, and it is idempotent, so re-running costs nothing.
.PHONY: init
init: install
	python3 agents/setup.py link

.PHONY: install
install:
	npm install

.PHONY: agents
agents:
	@python3 agents/setup.py list

.PHONY: unlink
unlink:
	python3 agents/setup.py unlink

.PHONY: start
start:
	npm start

.PHONY: build
build:
	npm run build

.PHONY: serve
serve:
	npm run serve

# docusaurus.config.js throws on a broken link or anchor, so a clean build is the whole of
# the site's correctness check. Named separately from `build` because that is what it is
# used for, and so CI and a person reach for the same word.
.PHONY: check
check: build

.PHONY: clear
clear:
	npm run clear

.PHONY: clean
clean:
	rm -rf build .docusaurus .cache-loader node_modules

.PHONY: docs-updated-to-sha
docs-updated-to-sha:
	@$(DOCS_REF) show

.PHONY: docs-changes
docs-changes:
	@$(DOCS_REF) changes

.PHONY: docs-changes-full
docs-changes-full:
	@$(DOCS_REF) changes --full
