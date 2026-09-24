# Dependency and License Policy

The repository uses two lockfiles as the reproducible dependency boundary:

- `uv.lock` for Python, with the web extra and development group declared in `pyproject.toml`. NumPy is the measured local vector-arithmetic dependency for the 100k exact-search target; it is not an ANN database.
- `frontend/package-lock.json` for the React/Vite toolchain.

CI installs with frozen/locked commands only. `pip-audit` and `npm audit --audit-level=high` block known high-severity runtime issues. `scripts/check_licenses.py` requires license metadata for frontend packages; the Python license gate rejects AGPL/GPL/SSPL metadata pending manual review. Release jobs generate CycloneDX SBOMs and license inventories as artifacts. These reports support, but do not replace, legal or firm review of dependency compatibility.

Dependency updates are grouped through `.github/dependabot.yml` and must include tests, typecheck, build, browser workflow, audit, and license checks. Do not bypass lockfiles with `pip install`/`npm install` in automation.
