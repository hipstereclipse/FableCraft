"""Conservative L4 known-name scanner for pack trees and nested Bedrock archives.

No release exemptions. Findings OR unreadable/unsupported content fail the command.
This static inventory gate cannot establish final naming approval or detect text in art,
audio speech, or arbitrary runtime-generated strings. Original packaging stays blocked.
"""
import argparse
import html
import io
import json
from pathlib import Path
import re
import struct
import unicodedata
from urllib.parse import unquote
import zipfile

from PIL import Image
from fc_strings import STRINGS

ESCAPES = re.compile(r'\\+u\{([0-9a-fA-F]{1,6})\}|\\+u([0-9a-fA-F]{4})|\\+x([0-9a-fA-F]{2})')


def normalize(value):
    for _ in range(8):
        previous = value
        value = html.unescape(unquote(value))
        value = ESCAPES.sub(lambda m: chr(int(next(g for g in m.groups() if g), 16)), value)
        if value == previous:
            break
    value = re.sub(r'§.', '', value)
    value = unicodedata.normalize('NFKC', value)
    value = ''.join(c for c in value if unicodedata.category(c) != 'Cf')
    value = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', value)
    value = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', value).casefold()
    return re.sub(r'[\W_]+', ' ', value).strip()


def rules():
    # Matching every table spelling is intentionally conservative, including ambiguous
    # generic words. Review false positives; never silently exempt a release occurrence.
    unique = {}
    for pair in STRINGS.values():
        spelling = pair['faithful']
        normalized = normalize(spelling)
        entry = unique.setdefault(normalized.replace(' ', ''), [spelling, set()])
        entry[1].add(normalized)
    return [(name, re.compile(r'(?<!\w)(?:' + '|'.join(
        r'\s*'.join(map(re.escape, key.split())) for key in sorted(forms)) + r')(?!\w)'))
            for name, forms in unique.values()]


def nbt_strings(data):
    """Read little-endian NBT tag names/string values without interpreting game state."""
    stream = io.BytesIO(data)
    values = []
    nodes = 0

    def read(length):
        if length < 0 or length > len(data):
            raise ValueError('invalid NBT length')
        value = stream.read(length)
        if len(value) != length:
            raise ValueError('truncated NBT')
        return value

    def string():
        value = read(struct.unpack('<H', read(2))[0]).decode('utf-8')
        values.append(value)

    def count():
        value = struct.unpack('<i', read(4))[0]
        if value < 0 or value > 1_000_000:
            raise ValueError('NBT collection limit exceeded')
        return value

    def payload(kind, depth=0):
        nonlocal nodes
        nodes += 1
        if depth > 64 or nodes > 2_000_000:
            raise ValueError('NBT recursion/node limit exceeded')
        if kind in (1, 2, 3, 4, 5, 6):
            read({1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}[kind])
        elif kind == 8:
            string()
        elif kind in (7, 11, 12):
            read(count() * {7: 1, 11: 4, 12: 8}[kind])
        elif kind == 9:
            child, size = read(1)[0], count()
            if child == 0 and size:
                raise ValueError('invalid NBT end-tag list')
            for _ in range(size):
                payload(child, depth + 1)
        elif kind == 10:
            while (child := read(1)[0]) != 0:
                string()
                payload(child, depth + 1)
        else:
            raise ValueError(f'unsupported NBT tag {kind}')

    kind = read(1)[0]
    string()
    payload(kind)
    if stream.read(1):
        raise ValueError('trailing NBT data')
    return values


class Scanner:
    def __init__(self, max_bytes=256 * 1024 * 1024, max_file_bytes=64 * 1024 * 1024, max_depth=6):
        self.max_bytes, self.max_file_bytes, self.max_depth = max_bytes, max_file_bytes, max_depth
        self.total_bytes = 0
        self.entries = 0
        self.findings = set()
        self.errors = []
        self.rules = rules()

    def text(self, path, kind, value):
        normalized = normalize(value)
        for name, pattern in self.rules:
            if pattern.search(normalized):
                self.findings.add((path, kind, name))

    def consume(self, size):
        self.total_bytes += size
        self.entries += 1
        if size > self.max_file_bytes or self.total_bytes > self.max_bytes or self.entries > 10000:
            raise ValueError('scanner size/entry limit exceeded')

    def blob(self, path, data, depth=0):
        try:
            self.consume(len(data))
            self.text(path, 'filename', path)
            suffix = Path(path).suffix.lower()
            if suffix in ('.zip', '.mcaddon', '.mcpack') or data.startswith(b'PK\x03\x04'):
                if depth >= self.max_depth:
                    raise ValueError('nested archive depth limit exceeded')
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    infos = archive.infolist()
                    if len(infos) + self.entries > 10000:
                        raise ValueError('archive entry limit exceeded')
                    for entry in infos:
                        child = path + '!' + entry.filename
                        self.text(child, 'filename', entry.filename)
                        self.text(child, 'archive entry metadata',
                                  (entry.comment + entry.extra).decode('utf-8', errors='replace'))
                        if entry.flag_bits & 1:
                            raise ValueError('encrypted archive entry')
                        if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                            raise ValueError('archive symlinks are not supported')
                        if entry.file_size > self.max_file_bytes or self.total_bytes + entry.file_size > self.max_bytes:
                            raise ValueError('archive expanded size limit exceeded')
                        if entry.is_dir():
                            continue
                        self.blob(child, archive.read(entry), depth + 1)
                    self.text(path, 'archive comment', archive.comment.decode('utf-8', errors='replace'))
                return
            if suffix == '.mcstructure':
                for value in nbt_strings(data):
                    self.text(path, 'NBT string', value)
                return
            if suffix == '.png':
                with Image.open(io.BytesIO(data)) as image:
                    if image.width * image.height > 16_777_216:
                        raise ValueError('image pixel limit exceeded')
                    image.load()
                    metadata = dict(image.info)
                    metadata.update({str(key): value for key, value in image.getexif().items()})
                    for key, value in metadata.items():
                        if isinstance(value, (str, bytes)):
                            self.text(path, 'image metadata', key + ' ' +
                                      (value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value))
                return
            if suffix == '.wav':
                if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
                    raise ValueError('invalid WAV header')
                if len(data) < 12 or struct.unpack('<I', data[4:8])[0] + 8 != len(data):
                    raise ValueError('invalid WAV length')
                offset = 12
                while offset < len(data):
                    if offset + 8 > len(data):
                        raise ValueError('truncated WAV chunk')
                    tag, size = data[offset:offset+4], struct.unpack('<I', data[offset+4:offset+8])[0]
                    start, end = offset + 8, offset + 8 + size
                    if end > len(data):
                        raise ValueError('truncated WAV metadata')
                    if tag not in (b'fmt ', b'data'):
                        if tag == b'LIST':
                            if size < 4:
                                raise ValueError('truncated WAV LIST type')
                            start += 4  # RIFF list type (e.g. INFO) is structural.
                        self.text(path, 'audio metadata', data[start:end].decode('utf-8', errors='replace'))
                    offset = end + size % 2
                return
            # Text, including extension-less metadata, is checked before JSON parsing.
            encoding = 'utf-16' if data.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
            value = data.decode(encoding)
            if '\x00' in value:
                raise ValueError('unsupported binary content')
            self.text(path, 'text', value)
            if suffix == '.json':
                json.loads(value)  # Invalid generated JSON cannot pass the gate.
        except (ValueError, OSError, UnicodeError, zipfile.BadZipFile, RuntimeError, EOFError,
                Image.DecompressionBombError) as error:
            self.errors.append({'path': path, 'error': str(error)})

    def scan(self, path):
        path = Path(path)
        if path.is_symlink():
            self.errors.append({'path': str(path), 'error': 'symlink input is not supported'})
            return self.result()
        if not path.exists():
            self.errors.append({'path': str(path), 'error': 'input does not exist'})
            return self.result()
        files = sorted(path.rglob('*')) if path.is_dir() else [path]
        for file in files:
            label = file.relative_to(path).as_posix() if path.is_dir() else file.name
            self.text(label, 'filename', label)
            if file.is_symlink():
                self.errors.append({'path': label, 'error': 'symlinks are not supported in release inputs'})
            elif file.is_file():
                try:
                    if file.stat().st_size > self.max_file_bytes:
                        raise ValueError('file size limit exceeded')
                    self.blob(label, file.read_bytes())
                except (OSError, ValueError) as error:
                    self.errors.append({'path': label, 'error': str(error)})
        return self.result()

    def result(self):
        return {
            'clean': not self.findings and not self.errors,
            'scope': 'Conservative known-name static scan; not final release approval or legal clearance.',
            'entries': self.entries, 'bytes_examined': self.total_bytes,
            'findings': [{'path': p, 'kind': k, 'name': n} for p, k, n in sorted(self.findings)],
            'errors': self.errors,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = Scanner().scan(args.input)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"Branding scan: {len(report['findings'])} findings, {len(report['errors'])} read errors; "
          f"{report['entries']} entries examined")
    for item in report['findings'][:30]:
        print(f"  {item['path']}: {item['kind']}: {item['name']}")
    for item in report['errors'][:30]:
        print(f"  ERROR {item['path']}: {item['error']}")
    return 0 if report['clean'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
