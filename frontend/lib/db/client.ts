import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import * as schema from "./schema";
import path from "path";

// Use the same database path as the backend API (testgpt.db in this directory)
const dbPath = path.join(__dirname, "testgpt.db");
const sqlite = new Database(dbPath);
export const db = drizzle(sqlite, { schema });
