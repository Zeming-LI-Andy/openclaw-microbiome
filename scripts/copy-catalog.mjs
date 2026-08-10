import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const src = path.join(root, "catalog");
const dest = path.join(root, "dist", "catalog");

fs.mkdirSync(dest, { recursive: true });
fs.copyFileSync(path.join(src, "tools.yaml"), path.join(dest, "tools.yaml"));
console.log(`Copied catalog → ${dest}`);
