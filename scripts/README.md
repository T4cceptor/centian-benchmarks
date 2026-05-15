# Utility scripts

## Merge two Centian SQLite databases

`merge-centian-sqlite.mjs` merges two Centian event-store databases into a new output file without depending on Centian's Go code or any npm packages:

```bash
node scripts/merge-centian-sqlite.mjs left.sqlite right.sqlite merged.sqlite
```

It uses Node's built-in SQLite module, so it follows the repo's existing Node 24 requirement rather than adding another runtime or package manager dependency.

The script intentionally fails if:

- either input path is missing
- the output path already exists
- the SQLite schemas differ
- `event_store_schema` contents differ
- `PRAGMA user_version` differs
- copying rows violates a constraint
- the final database fails SQLite integrity validation

`event_store_schema` is validated but not copied, because both inputs should contain the same shared metadata row(s).
