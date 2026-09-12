import js from "@eslint/js";

export default [
  {
    files: ["packs/Fablecraft_BP/scripts/**/*.js"],
    ...js.configs.recommended,
    languageOptions: { ecmaVersion: 2022, sourceType: "module", globals: { console: "readonly" } },
    rules: { ...js.configs.recommended.rules, "no-unused-vars": "warn", "no-empty": ["error", { allowEmptyCatch: true }] },
  },
];
