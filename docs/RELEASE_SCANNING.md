# Release naming scan

L4 has a tested recursive scanner; original release packaging remains blocked.
The current original preview still contains 2,512 known-name findings across 1,647
entries. The local faithful nested mcaddon has 4,174 findings across 1,648 entries.
Both scans read every supported entry without errors and correctly return exit 1.
These are occurrence groups (path, category, name), not counts of literal repetitions.
Evidence: `screenshots/validation/L4/release-scan-summary.json` and adjacent logs.

```sh
python scripts/scan_branding.py <pack-tree-or-mcaddon> --output tmp/release-scan.json
python scripts/tests/test_branding_scan.py
python scripts/validate.py --output screenshots/validation/L4
```

The scanner checks filenames, empty directory names, text of any extension, nested
ZIP/mcpack/mcaddon archives, archive comments and entry metadata, PNG text/EXIF
metadata, WAV non-sample chunks, and little-endian structure NBT names/string values.
It normalizes Unicode compatibility forms, case, separators, camel case, color codes,
invisible format characters, and up to eight rounds of JS/Unicode, URL and HTML escapes.
Known phrases also match their compact spelling. UTF-8 and BOM-marked UTF-16 are read.

Every faithful spelling in fc_strings.STRINGS is checked, including ambiguous generic
words. This conservative policy can produce false positives. No runtime, identifier,
comment or compatibility-key exemptions exist. Findings must be reviewed explicitly;
a clean result only means this finite static check found no known-name occurrences.

Unreadable, malformed, encrypted, symlinked or unsupported binary input fails closed.
Limits are 64 MiB per file, 256 MiB examined including expanded archives, 10,000 file
entries, six archive levels, 16,777,216 pixels per image, and bounded NBT depth/nodes.
Reports include read errors separately from naming findings; both prevent success.
The tests inject names into each supported content category and cover corruption,
resource limits, nested archives, escaped spellings and packaging refusal.

This is not OCR, speech recognition, arbitrary code execution or legal clearance.
Unknown names, visual text, audible speech, unfamiliar metadata conventions and
runtime string construction require separate inventory/review. The earlier display
inventory understates release debt because identifiers, paths, comments and legacy
lookup keys are included here. Remaining vocabulary review includes unnamed inn/guild
phrases and other names missing from the table; no zero-debt claim is justified.

`build_addon.package(..., "original")` now runs the scan and rejects findings/errors.
Even a clean test fixture cannot enable release: final public naming and saved-world
compatibility review remain explicit blockers. The CLI also refuses original packaging
without `--preview`. Wayfarer Tales remains a provisional test name. Faithful builds
stay under ignored `tmp/builds/`; no development archive is staged or published.

To complete L4, finish the name inventory, design a reference-aware isolated remap for
pack paths/IDs and legacy compatibility tables, validate old-world behavior, obtain the
final public title, then inspect all three original archives recursively before enabling
release. Do not replace these requirements with scanner exemptions or blind text replacement.
