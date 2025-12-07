PYTHON := $(shell command -v python3 || command -v python)

preview:
	@pnpm --dir preview install --silent
	@cd preview && pnpm dev

build:
	@$(PYTHON) test_solutions.py tasks

build-and-preview: build preview

release: build
	tar -czf release.tar.gz release/

.PHONY: release preview build build-and-preview
