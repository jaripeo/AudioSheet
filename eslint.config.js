// @ts-check
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "**/dist/**",
      "**/node_modules/**",
      "**/*.d.ts",
      // Generated artefact; see scripts/gen_schema.py.
      "packages/schema/schema/**",
      // In scope from Phase 2 (web) and Phase 8 (desktop).
      "apps/**",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // Phase 0 ships stubs whose parameters are unused by design; the signature
      // is the deliverable. Underscore-prefixing every one of them would make the
      // real implementations diff noisily in later phases.
      "@typescript-eslint/no-unused-vars": [
        "error",
        { args: "none", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/explicit-module-boundary-types": "error",
      "@typescript-eslint/consistent-type-imports": "error",
      "no-restricted-globals": [
        "error",
        { name: "fetch", message: "INV-1: the app must not open network connections." },
        { name: "XMLHttpRequest", message: "INV-1: the app must not open network connections." },
      ],
    },
  },
  {
    // Tests live outside the packages' emit projects (see tsconfig.test.json), so
    // they are typed against that project explicitly.
    files: ["packages/*/test/**/*.ts"],
    languageOptions: {
      parserOptions: {
        projectService: false,
        project: ["./tsconfig.test.json"],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // Tests assert on optional lookups deliberately.
      "@typescript-eslint/no-non-null-assertion": "off",
      "@typescript-eslint/no-unnecessary-condition": "off",
    },
  },
  {
    files: ["**/*.config.ts", "**/*.config.js", "eslint.config.js"],
    ...tseslint.configs.disableTypeChecked,
  },
);
