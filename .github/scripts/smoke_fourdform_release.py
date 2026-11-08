#!/usr/bin/env python3
"""macOS smoke check: provision a skills release or test a built CLI and render PNGs."""

import argparse
import hashlib
import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import zlib


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "4d-skills/skills/4dtools/scripts/provision_fourdform.py"
FORM = ROOT / "4d-skills/Project/Sources/Forms/DropdownExamples/form.4DForm"
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("provision_fourdform", SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class SmokeError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise SmokeError(message)


def png_info(path):
    data = path.read_bytes()
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"{path}: output is not PNG")
    offset, dimensions, compressed, ended, stride = 8, None, bytearray(), False, None
    while offset < len(data):
        require(offset + 12 <= len(data), f"{path}: truncated PNG chunk")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 12 + length
        require(end <= len(data), f"{path}: truncated PNG data")
        payload = data[offset + 8:end - 4]
        crc = struct.unpack(">I", data[end - 4:end])[0]
        require(zlib.crc32(kind + payload) == crc, f"{path}: invalid PNG CRC")
        if kind == b"IHDR":
            require(offset == 8 and length == 13, f"{path}: invalid PNG header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            dimensions = width, height
            require(min(dimensions) > 0, f"{path}: empty PNG dimensions")
            formats = {0: (1, (1, 2, 4, 8, 16)), 2: (3, (8, 16)),
                       3: (1, (1, 2, 4, 8)), 4: (2, (8, 16)), 6: (4, (8, 16))}
            require(color in formats and depth in formats[color][1], f"{path}: invalid PNG format")
            require(compression == filtering == interlace == 0,
                    f"{path}: smoke checker requires standard noninterlaced PNG")
            stride = 1 + (width * formats[color][0] * depth + 7) // 8
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            require(length == 0 and end == len(data), f"{path}: invalid PNG ending")
            ended = True
        offset = end
    require(dimensions and compressed and ended, f"{path}: incomplete PNG")
    decoder = zlib.decompressobj()
    pixels = decoder.decompress(compressed) + decoder.flush()
    require(decoder.eof and not decoder.unused_data and pixels, f"{path}: invalid PNG pixels")
    require(len(pixels) == stride * dimensions[1], f"{path}: invalid PNG raster dimensions")
    require(all(pixels[row] <= 4 for row in range(0, len(pixels), stride)),
            f"{path}: invalid PNG scanline filter")
    return dimensions, hashlib.sha256(pixels).hexdigest()


def render(binary, output, *options, form=FORM):
    result = subprocess.run(
        [str(binary), str(form), "--output", str(output), *options],
        capture_output=True, text=True, timeout=60,
    )
    require(result.returncode == 0, f"Rendering failed: {result.stderr or result.stdout}")
    return png_info(output)


def smoke(root, binary=None):
    root.mkdir(parents=True, exist_ok=True)
    manifest = installer.load_manifest(installer.MANIFEST)
    provisioned = binary is None
    if provisioned:
        binary = installer.provision(root, manifest)
    else:
        installer.verify_binary(binary, installer.check_platform(manifest))
    outputs = root / "preview-output"
    outputs.mkdir(exist_ok=True)
    pixels = {}
    for theme in ("classic-light", "classic-dark", "liquid-glass-light", "liquid-glass-dark"):
        dimensions, pixels[theme] = render(
            binary, outputs / f"{theme}.png",
            "--theme", theme, "--page", "1", "--scale", "1.5",
            "--max-dimension", "256", "--language", "ja",
        )
        require(max(dimensions) <= 256, f"{theme}: --max-dimension bound was not honored")
        print(f"{theme}: verified PNG {dimensions[0]}x{dimensions[1]}")
    for prefix in ("classic", "liquid-glass"):
        require(pixels[f"{prefix}-light"] != pixels[f"{prefix}-dark"],
                f"{prefix}: light/dark themes produced identical pixels")
    normal, _ = render(binary, outputs / "scale-1.png", "--scale", "1", "--page", "1")
    doubled, _ = render(binary, outputs / "scale-2.png", "--scale", "2", "--page", "1")
    require(doubled == tuple(value * 2 for value in normal), "--scale 2 did not double dimensions")
    print(f"scale: {normal} -> {doubled}")
    invalid_output = outputs / "invalid-input.png"
    require(not invalid_output.exists(), "Invalid-input output already exists; use a fresh consumer root")
    result = subprocess.run(
        [str(binary), str(root / "missing.4DForm"), "--output", str(invalid_output)],
        capture_output=True, text=True, timeout=60,
    )
    require(result.returncode != 0 and result.stderr.strip(), "Invalid input did not report failure")
    require(not invalid_output.exists(), "Invalid input produced a success-shaped PNG output")
    if provisioned:
        require((root / ".gitignore").read_text().splitlines().count("/tools/4dform/") == 1,
                "Consumer .gitignore does not contain exactly one scoped tool entry")
        require(installer.provision(root, manifest) == binary, "Compatible installation was not reused")
    print(f"Verified fourdform binary and PNG outputs: {root}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer-root", required=True, type=Path,
                        help="isolated scratch consumer directory (not a real project)")
    parser.add_argument("--binary", type=Path,
                        help="test a locally built CLI without downloading a release")
    arguments = parser.parse_args()
    try:
        smoke(arguments.consumer_root.resolve(),
              arguments.binary.resolve(strict=True) if arguments.binary else None)
    except (SmokeError, installer.ProvisionError, OSError, ValueError, KeyError,
            zlib.error, subprocess.TimeoutExpired) as error:
        print(f"fourdform live smoke failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
