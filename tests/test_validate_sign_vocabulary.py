from scripts.validate_sign_vocabulary import find_problems


def _write_image(folder, name):
    (folder / name).write_bytes(b"not a real image, just needs to exist")


def test_clean_manifest_has_no_problems(tmp_path):
    _write_image(tmp_path, "hello.png")
    manifest = [{"phrase": "Hello", "image": "hello.png"}]
    assert find_problems(manifest, str(tmp_path)) == []


def test_missing_file_is_reported(tmp_path):
    manifest = [{"phrase": "Hello", "image": "does_not_exist.png"}]
    problems = find_problems(manifest, str(tmp_path))
    assert len(problems) == 1
    assert "missing file" in problems[0]


def test_orphaned_image_is_reported(tmp_path):
    _write_image(tmp_path, "unused.png")
    problems = find_problems([], str(tmp_path))
    assert any("unused" in p and "unused.png" in p for p in problems)


def test_duplicate_phrase_is_reported_case_insensitively(tmp_path):
    _write_image(tmp_path, "a.png")
    _write_image(tmp_path, "b.png")
    manifest = [
        {"phrase": "Hello", "image": "a.png"},
        {"phrase": "hello", "image": "b.png"},
    ]
    problems = find_problems(manifest, str(tmp_path))
    assert any("Duplicate phrase" in p for p in problems)


def test_entry_missing_fields_is_reported(tmp_path):
    manifest = [{"phrase": "Hello"}]  # no "image" key
    problems = find_problems(manifest, str(tmp_path))
    assert any("missing" in p.lower() for p in problems)
