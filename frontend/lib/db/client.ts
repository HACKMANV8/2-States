import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import * as schema from "./schema";
import path from "path";

// Use the database file relative to the frontend directory
// In development, process.cwd() points to the frontend directory
const dbPath = path.join(process.cwd(), "lib", "db", "testgpt.db");

// Create database with proper error handling
const sqlite = new Database(dbPath);
export const db = drizzle(sqlite, { schema });
