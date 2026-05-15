#!/usr/bin/env node

import { existsSync, unlinkSync } from 'node:fs';
import { resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const METADATA_TABLES = new Set(['event_store_schema']);

main();

function main() {
  const [leftArg, rightArg, outputArg] = process.argv.slice(2);
  if (!leftArg || !rightArg || !outputArg || process.argv.length !== 5) {
    fail('Usage: node scripts/merge-centian-sqlite.mjs <left.sqlite> <right.sqlite> <output.sqlite>');
  }

  const leftPath = resolve(leftArg);
  const rightPath = resolve(rightArg);
  const outputPath = resolve(outputArg);

  assertInputPath(leftPath, 'left');
  assertInputPath(rightPath, 'right');
  assertDistinctPaths(leftPath, rightPath, outputPath);

  if (existsSync(outputPath)) {
    fail(`Output database already exists: ${outputPath}`);
  }

  const leftDb = new DatabaseSync(leftPath);
  const rightDb = new DatabaseSync(rightPath);
  let outputDb;

  try {
    assertCompatibleDatabases(leftDb, rightDb);

    // VACUUM INTO creates a clean SQLite copy from a consistent snapshot.
    leftDb.exec(`VACUUM INTO ${quoteString(outputPath)}`);
    outputDb = new DatabaseSync(outputPath);

    const copiedRows = mergeIntoOutput(outputDb, rightPath);
    assertHealthyDatabase(outputDb);

    console.log(`Merged ${leftPath}`);
    console.log(`   + ${rightPath}`);
    console.log(`   = ${outputPath}`);
    for (const { table, rows } of copiedRows) {
      console.log(`Copied ${rows} row(s) from ${table}`);
    }
  } catch (error) {
    outputDb?.close();
    if (existsSync(outputPath)) {
      unlinkSync(outputPath);
    }
    fail(error instanceof Error ? error.message : String(error));
  } finally {
    leftDb.close();
    rightDb.close();
    outputDb?.close();
  }
}

function assertInputPath(path, label) {
  if (!existsSync(path)) {
    fail(`Missing ${label} database: ${path}`);
  }
}

function assertDistinctPaths(leftPath, rightPath, outputPath) {
  if (leftPath === rightPath) {
    fail('Left and right database paths must be different.');
  }
  if (outputPath === leftPath || outputPath === rightPath) {
    fail('Output database path must be different from both input paths.');
  }
}

function assertCompatibleDatabases(leftDb, rightDb) {
  const leftSchema = schemaSignature(leftDb);
  const rightSchema = schemaSignature(rightDb);
  if (JSON.stringify(leftSchema) !== JSON.stringify(rightSchema)) {
    throw new Error('Input databases do not have identical SQLite schemas.');
  }

  if (!leftSchema.some(({ type, name }) => type === 'table' && name === 'event_store_schema')) {
    throw new Error('Missing required event_store_schema table.');
  }

  const leftMetadata = rows(leftDb, 'SELECT name, version FROM event_store_schema ORDER BY name');
  const rightMetadata = rows(rightDb, 'SELECT name, version FROM event_store_schema ORDER BY name');
  if (leftMetadata.length === 0) {
    throw new Error('event_store_schema is empty; schema version metadata is missing.');
  }
  if (JSON.stringify(leftMetadata) !== JSON.stringify(rightMetadata)) {
    throw new Error('Input databases do not have identical event store schema versions.');
  }

  const leftUserVersion = scalar(leftDb, 'PRAGMA user_version');
  const rightUserVersion = scalar(rightDb, 'PRAGMA user_version');
  if (leftUserVersion !== rightUserVersion) {
    throw new Error(`Input databases do not have identical PRAGMA user_version values (${leftUserVersion} != ${rightUserVersion}).`);
  }
}

function schemaSignature(db) {
  return rows(
    db,
    `
      SELECT type, name, tbl_name, sql
      FROM sqlite_schema
      WHERE name NOT LIKE 'sqlite_%'
      ORDER BY type, name
    `,
  );
}

function mergeIntoOutput(outputDb, rightPath) {
  outputDb.exec(`ATTACH DATABASE ${quoteString(rightPath)} AS source`);
  outputDb.exec('PRAGMA foreign_keys = OFF');

  const copiedRows = [];
  try {
    outputDb.exec('BEGIN IMMEDIATE');

    for (const table of dataTables(outputDb)) {
      const columns = writableColumns(outputDb, table);
      if (columns.length === 0) {
        throw new Error(`Table ${table} has no writable columns.`);
      }

      const quotedTable = quoteIdentifier(table);
      const quotedColumns = columns.map(quoteIdentifier).join(', ');
      const sourceRows = scalar(outputDb, `SELECT COUNT(*) FROM source.${quotedTable}`);

      try {
        outputDb.exec(`
          INSERT INTO main.${quotedTable} (${quotedColumns})
          SELECT ${quotedColumns}
          FROM source.${quotedTable}
        `);
      } catch (error) {
        throw new Error(
          `Failed while copying table ${table}. Inputs may overlap or violate a constraint: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }

      copiedRows.push({ table, rows: sourceRows });
    }

    outputDb.exec('COMMIT');
    return copiedRows;
  } catch (error) {
    safeExec(outputDb, 'ROLLBACK');
    throw error;
  } finally {
    safeExec(outputDb, 'PRAGMA foreign_keys = ON');
    safeExec(outputDb, 'DETACH DATABASE source');
  }
}

function dataTables(db) {
  return rows(
    db,
    `
      SELECT name
      FROM sqlite_schema
      WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
      ORDER BY name
    `,
  )
    .map(({ name }) => name)
    .filter((name) => !METADATA_TABLES.has(name));
}

function writableColumns(db, table) {
  return rows(db, `PRAGMA main.table_xinfo(${quoteIdentifier(table)})`)
    .filter(({ hidden }) => hidden === 0)
    .map(({ name }) => name);
}

function assertHealthyDatabase(db) {
  const integrity = scalar(db, 'PRAGMA integrity_check');
  if (integrity !== 'ok') {
    throw new Error(`Merged database failed integrity_check: ${integrity}`);
  }
}

function rows(db, sql) {
  return db.prepare(sql).all();
}

function scalar(db, sql) {
  const row = db.prepare(sql).get();
  return row[Object.keys(row)[0]];
}

function quoteIdentifier(identifier) {
  return `"${identifier.replaceAll('"', '""')}"`;
}

function quoteString(value) {
  return `'${value.replaceAll("'", "''")}'`;
}

function safeExec(db, sql) {
  try {
    db.exec(sql);
  } catch {
    // Best-effort cleanup after a failed merge.
  }
}

function fail(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}
