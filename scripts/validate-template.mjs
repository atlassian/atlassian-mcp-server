#!/usr/bin/env node

import process from "node:process";
import { validateRepository } from "./validation/repository.mjs";

const { errors, warnings } = await validateRepository(process.cwd());

if (warnings.length > 0) {
  console.log("Warnings:");
  for (const warning of warnings) {
    console.log(`- ${warning}`);
  }
  console.log("");
}

if (errors.length > 0) {
  console.error("Validation failed:");
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exitCode = 1;
} else {
  console.log("Validation passed.");
}
