# Plan — Task 0007

1. `stores.py`: `preferences` table + get/set; unit tests.
2. Preference detection: extend `input_guard`/router classification with a "preference statement" intent → persist → acknowledge.
3. Inject preferences into `compose_report` prompt; `/prefs` CLI command.
4. `personas/` seed files; loader that reads the file each turn; `/persona` command + env selection.
5. Tests: pref persistence/injection with fake LLM; persona hot-reload via tmp file edit.
6. Version minor bump. Commit: `feat(memory): add user preferences and hot-reload personas (task 0007)`.
