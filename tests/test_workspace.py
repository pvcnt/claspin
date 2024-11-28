import pytest

from claspin.workspace import ConfigFile, Workspace


@pytest.fixture
def workspace(tmp_path_factory: pytest.TempPathFactory) -> Workspace:
    root_dir = tmp_path_factory.mktemp("workspace")
    root_dir.joinpath("a").mkdir()
    root_dir.joinpath("a/b").mkdir()
    root_dir.joinpath("f1.star").write_text("f1 content")
    root_dir.joinpath("f2.star").write_text("f2 content")
    root_dir.joinpath("a").joinpath("f3.star").write_text("f3 content")
    root_dir.joinpath("a/b").joinpath("f4.star").write_text("f4 content")
    root_dir.joinpath("a/b").joinpath("f5.star").write_text("f5 content")
    return Workspace(root_dir)


def test_iter_files(workspace: Workspace):
    files = set(workspace.iter_files())
    assert files == {
        ConfigFile("f1.star", "f1 content"),
        ConfigFile("f2.star", "f2 content"),
        ConfigFile("a/f3.star", "f3 content"),
        ConfigFile("a/b/f4.star", "f4 content"),
        ConfigFile("a/b/f5.star", "f5 content"),
    }


def test_resolve_file(workspace: Workspace):
    f1 = workspace.resolve_file("//f1.star")
    assert f1 == ConfigFile("f1.star", "f1 content")

    f3 = workspace.resolve_file("//a/f3.star")
    assert f3 == ConfigFile("a/f3.star", "f3 content")

    f4 = workspace.resolve_file("//a/b/f4.star")
    assert f4 == ConfigFile("a/b/f4.star", "f4 content")

    f5 = workspace.resolve_file("f5.star", f4)
    assert f5 == ConfigFile("a/b/f5.star", "f5 content")

    with pytest.raises(ValueError) as exc_info:
        workspace.resolve_file("//does_not_exist.star")
    assert str(exc_info.value) == "Cannot resolve label '//does_not_exist.star'"

    with pytest.raises(ValueError) as exc_info:
        workspace.resolve_file("does_not_exist.star", f4)
    assert str(exc_info.value) == "Cannot resolve label 'does_not_exist.star'"
