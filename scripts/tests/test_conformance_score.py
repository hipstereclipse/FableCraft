"""Scoreboard integrity: missing evidence, invalid state, duplicates and stale output."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conformance_score import ROOT, CHECKLIST, AUDIT, START, END, EXPECTED, parse, update, audit_grades, render


class Scoreboard(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / CHECKLIST).read_text()
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for line in self.text.splitlines():
            if not line.startswith('| '): continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            if len(cells) != 5 or cells[2] == '—': continue
            for path in cells[2].split(';')[1:]:
                source = ROOT / path.strip(); target = self.root / path.strip()
                if source.is_dir(): target.mkdir(parents=True, exist_ok=True)
                elif source.is_file():
                    target.parent.mkdir(parents=True, exist_ok=True); target.write_text('fixture')
        target = self.root / AUDIT; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / AUDIT, target)

    def row(self, key): return next(line for line in self.text.splitlines() if line.startswith('| ' + key + ' '))

    def change(self, key, index, value):
        old = self.row(key); cells = [c.strip() for c in old.strip('|').split('|')]
        cells[index] = value; self.text = self.text.replace(old, '| ' + ' | '.join(cells) + ' |')

    def test_actual_repository_and_all_leaf_ids(self):
        self.assertEqual(set(parse((ROOT / CHECKLIST).read_text())), EXPECTED)
        self.assertEqual(len(EXPECTED), 45)

    def test_duplicate_id(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate checklist ID'):
            parse(self.text + '\n' + self.row('L1'), self.root)

    def test_missing_row(self):
        with self.assertRaisesRegex(ValueError, 'Missing checklist IDs'):
            parse(self.text.replace(self.row('L1'), ''), self.root)

    def test_invalid_status(self):
        self.change('L1', 1, 'mostly done')
        with self.assertRaisesRegex(ValueError, 'Invalid status'): parse(self.text, self.root)

    def test_missing_evidence_and_path(self):
        self.change('L1', 2, '—')
        with self.assertRaisesRegex(ValueError, 'Missing evidence'): parse(self.text, self.root)
        self.change('L1', 2, 'abcdef1; screenshots/no-such-evidence')
        with self.assertRaisesRegex(ValueError, 'Missing evidence path'): parse(self.text, self.root)

    def test_done_cannot_hide_pending_manual_checks(self):
        self.change('L1', 1, 'done'); self.change('L1', 3, 'PASS (automated); PENDING (manual)')
        with self.assertRaisesRegex(ValueError, 'Incomplete grade marked done'): parse(self.text, self.root)

    def test_automated_pass_does_not_count_as_done(self):
        self.change('L1', 1, 'in-progress'); self.change('L1', 3, 'PASS (automated); PENDING (manual)')
        row = parse(self.text, self.root)['L1']
        self.assertTrue(row['automated']); self.assertTrue(row['manual_pending']); self.assertNotEqual(row['status'], 'done')

    def test_stale_output_and_marker_integrity(self):
        current = update(self.text, self.root)
        self.assertEqual(update(current, self.root, check=True), current)
        stale = current.replace('45 approved plan leaves', '999 approved plan leaves')
        with self.assertRaisesRegex(ValueError, 'Stale scoreboard'): update(stale, self.root, check=True)
        with self.assertRaisesRegex(ValueError, 'markers'): update(current.replace(END, ''), self.root)

    def test_manual_prose_is_preserved(self):
        text = 'Editorial note before\n' + self.text + '\nEditorial note after\n'
        result = update(text, self.root)
        self.assertTrue(result.startswith('Editorial note before\n')); self.assertTrue(result.endswith('\nEditorial note after\n'))

    def test_bad_or_duplicate_appearance_grade(self):
        with self.assertRaisesRegex(ValueError, 'Invalid structure audit grade'):
            audit_grades('| example | PASS | 100 | 1/1/1 | image |')
        row = '| example | S | 100 | 1/1/1 | image |'
        with self.assertRaisesRegex(ValueError, 'Duplicate structure audit ID'): audit_grades(row + '\n' + row)
        self.assertEqual(audit_grades(row)['S'], 1)


if __name__ == '__main__': unittest.main(verbosity=2)
