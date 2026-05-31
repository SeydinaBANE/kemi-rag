from __future__ import annotations

import hashlib

from app.utils.hash import sha256_file, sha256_hash


class TestSha256Hash:
    def test_sha256_hash_string(self) -> None:
        result = sha256_hash("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_sha256_hash_bytes(self) -> None:
        result = sha256_hash(b"hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_sha256_hash_empty_string(self) -> None:
        result = sha256_hash("")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_sha256_hash_different_inputs(self) -> None:
        a = sha256_hash("foo")
        b = sha256_hash("bar")
        assert a != b


class TestSha256File:
    def test_sha256_file(self, tmp_path: str) -> None:
        import os

        path = os.path.join(tmp_path, "test.txt")
        with open(path, "w") as f:
            f.write("hello world")

        result = sha256_file(path)
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert result == expected

    def test_sha256_file_larger_than_chunk(self) -> None:
        import os

        path = os.path.join("/tmp", "test_large.txt")
        data = "A" * 70000  # larger than 65536 chunk size
        with open(path, "w") as f:
            f.write(data)

        try:
            result = sha256_file(path)
            expected = hashlib.sha256(data.encode()).hexdigest()
            assert result == expected
        finally:
            os.remove(path)
