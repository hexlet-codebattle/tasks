preview:
	@pnpm --dir preview install --silent
	@cd preview && pnpm dev

build:
	python3 test_solutions.py tasks || python test_solutions.py tasks

build-and-preview: build preview

release: build
	tar -czf release.tar.gz release/

.PHONY: release preview build-and-preview
