"""Negative release-name fixtures across paths, text, nested packs and metadata."""
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scan_branding import Scanner
from fc_lib import nbt_compound, nbt_string, write_mcstructure


def zip_bytes(entries, comment=b''):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
        archive.comment = comment
    return output.getvalue()


class BrandingScan(unittest.TestCase):
    def scan_blob(self, filename, data, **limits):
        scanner = Scanner(**limits)
        scanner.blob(filename, data if isinstance(data, bytes) else data.encode())
        return scanner.result()

    def assert_name(self, result, name):
        self.assertFalse(result['clean'])
        self.assertIn(name, [entry['name'] for entry in result['findings']])
        self.assertEqual(result['errors'], [])

    def test_original_text_passes_and_substrings_do_not_match(self):
        result = self.scan_blob('manifest.json', json.dumps({'name': 'Wayfarer Tales', 'realm': 'Elderfen',
                                                            'text': 'Favor your friends; avoid trouble.'}))
        self.assertTrue(result['clean'], result)

    def test_each_pack_text_type_rejects_known_names(self):
        for suffix in ('.json', '.js', '.lang', '.mcmeta', '.txt', '.mcfunction', ''):
            with self.subTest(suffix=suffix):
                self.assert_name(self.scan_blob('file' + suffix, '"Albion"'), 'Albion')

    def test_case_separators_camelcase_and_compacted_phrase(self):
        for value in ('JACK_OF_BLADES', 'fc:jack-of-blades', 'JackOfBlades', 'jackofblades'):
            with self.subTest(value=value):
                self.assert_name(self.scan_blob('script.js', value), 'Jack of Blades')

    def test_escaped_and_encoded_text(self):
        for value in (r'Alb\u0069on', r'Alb\x69on', r'Alb\u{69}on',
                      r'Alb\\u0069on', 'Alb&#105;on', 'Alb%69on', 'Ａｌｂｉｏｎ', 'Al\u200bbion'):
            with self.subTest(value=value):
                self.assert_name(self.scan_blob('script.js', value), 'Albion')
        self.assert_name(self.scan_blob('script.txt', 'Albion'.encode('utf-16')), 'Albion')

    def test_color_codes_comments_and_identifier_tokens(self):
        for value in ('// §6Fablecraft', 'const FABLE_EMOTES = [];', 'fc:balverine_fang'):
            with self.subTest(value=value):
                self.assertFalse(self.scan_blob('script.js', value)['clean'])

    def test_filenames_and_empty_directories(self):
        self.assert_name(self.scan_blob('entities/theresa.json', '{}'), 'Theresa')
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'Albion').mkdir()
            self.assert_name(Scanner().scan(directory), 'Albion')

    def test_nested_mcaddon_mcpack_and_arbitrary_archive_extension(self):
        inner = zip_bytes({'texts/en_US.lang': 'realm=Albion'})
        for label in ('packs/clean.mcpack', 'packs/unknown.dat'):
            result = self.scan_blob('clean.mcaddon', zip_bytes({label: inner}))
            self.assert_name(result, 'Albion')
            self.assertTrue(any('!texts/en_US.lang' in entry['path'] for entry in result['findings']))

    def test_archive_and_entry_comments(self):
        self.assert_name(self.scan_blob('clean.mcaddon', zip_bytes({'file.txt': 'clean'}, b'Albion')), 'Albion')
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as archive:
            info = zipfile.ZipInfo('file.txt'); info.comment = b'Theresa'
            archive.writestr(info, 'clean')
        self.assert_name(self.scan_blob('clean.mcpack', out.getvalue()), 'Theresa')

    def test_png_text_metadata_and_clean_pixels(self):
        clean = io.BytesIO(); Image.new('RGB', (2, 2)).save(clean, format='PNG')
        self.assertTrue(self.scan_blob('image.png', clean.getvalue())['clean'])
        output = io.BytesIO(); metadata = PngImagePlugin.PngInfo(); metadata.add_text('Description', 'Albion')
        Image.new('RGB', (2, 2)).save(output, format='PNG', pnginfo=metadata)
        self.assert_name(self.scan_blob('image.png', output.getvalue()), 'Albion')

    def test_wav_metadata_but_not_sample_bytes(self):
        def wav(tag, data):
            body = b'WAVE' + tag + struct.pack('<I', len(data)) + data + b'\0' * (len(data) % 2)
            return b'RIFF' + struct.pack('<I', len(body)) + body
        self.assertTrue(self.scan_blob('sound.wav', wav(b'data', b'Albion'))['clean'])
        self.assert_name(self.scan_blob('sound.wav', wav(b'LIST', b'INFOAlbion')), 'Albion')

    def test_structure_nbt_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'site.mcstructure'
            write_mcstructure(path, nbt_compound({'name': nbt_string('Albion')}))
            self.assert_name(Scanner().scan(path), 'Albion')
            path.write_bytes(path.read_bytes()[:-1])
            self.assertTrue(Scanner().scan(path)['errors'])

    def test_limits_corruption_and_unknown_binary_fail_closed(self):
        cases = [('pack.mcaddon', b'not zip', {}), ('thing.bin', b'\xff\x00', {}),
                 ('script.js', b'clean', {'max_file_bytes': 2}),
                 ('pack.mcaddon', zip_bytes({'inner.mcpack': zip_bytes({'text': 'clean'})}), {'max_depth': 1})]
        for name, data, limits in cases:
            with self.subTest(name=name, limits=limits):
                result = self.scan_blob(name, data, **limits)
                self.assertFalse(result['clean']); self.assertTrue(result['errors'])

    def test_encrypted_entries_and_symlinks_fail_closed(self):
        data = bytearray(zip_bytes({'file.txt': 'clean'}))
        central = data.index(b'PK\x01\x02')
        data[6] |= 1
        data[central + 8] |= 1
        self.assertIn('encrypted', self.scan_blob('pack.mcaddon', bytes(data))['errors'][0]['error'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'target').write_text('clean')
            (root / 'link').symlink_to(root / 'target')
            self.assertTrue(Scanner().scan(root / 'link')['errors'])

    def test_clean_static_scan_still_cannot_enable_original_release(self):
        from build_addon import package
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'packs').mkdir()
            (root / 'packs/manifest.json').write_text('{"name":"Elderfen"}')
            self.assertTrue(Scanner().scan(root / 'packs')['clean'])
            with self.assertRaisesRegex(ValueError, 'final naming and compatibility review'):
                package(root, 'original')
            self.assertFalse((root / 'dist').exists())

    def test_cli_exit_codes_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'text.lang'; report = Path(directory) / 'report.json'
            cmd = [sys.executable, str(ROOT / 'scripts/scan_branding.py'), str(path), '--output', str(report)]
            for value, expected in [('Elderfen', 0), ('Albion', 1)]:
                path.write_text(value)
                result = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertEqual(json.loads(report.read_text())['clean'], expected == 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
