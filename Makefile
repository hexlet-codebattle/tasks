PYTHON := $(shell command -v python3 || command -v python)

preview:
	@pnpm --dir preview install --silent
	@cd preview && pnpm dev

build-private: drop-release
	@$(PYTHON) test_solutions.py private

drop-release:
	@rm -rf release

check-names:
	@$(PYTHON) check_task_names.py

build: check-names drop-release
	@$(PYTHON) test_solutions.py tasks

build-and-preview: build preview

release: build
	tar -czf release.tar.gz release/


push-local:
	@$(PYTHON) push_tasks.py http://localhost:4000/ext_api/tasks --hidden

push-private:
	@$(PYTHON) push_tasks.py https://codebattle.hexlet.io/ext_api/tasks --hidden

push-public:
	@$(PYTHON) push_tasks.py https://codebattle.hexlet.io/ext_api/tasks --public

push-packs-local:
	@$(PYTHON) push_task_packs.py http://localhost:4000/ext_api/task_packs --hidden

push-packs-private:
	@$(PYTHON) push_task_packs.py https://codebattle.hexlet.io/ext_api/task_packs --hidden

push-packs-public:
	@$(PYTHON) push_task_packs.py https://codebattle.hexlet.io/ext_api/task_packs --public

.PHONY: release preview build build-and-preview check-names push push-private push-public push-local push-packs-local push-packs-private push-packs-public
