# uvlisk

`uvlisk` is a wrapper for [uv](https://github.com/astral-sh/uv) that automatically uses the version of `uv` specified in `.uv-version` or `pyproject.toml` (via `tool.uv.required-version`). If no version is specified, it uses the latest version.

It is inspired by [bazelisk](https://github.com/bazelbuild/bazelisk).

`uvlisk` uses [mise](https://mise.jdx.dev) to manage and run the `uv` versions. It will automatically download a standalone `mise` binary if one is not found in your PATH.

## Installation

You can install `uvlisk` directly from git using `pipx`:

```bash
pipx install git+https://github.com/gueraf/uvlisk.git --force
```

## Usage

Use `uvlisk` just like you would use `uv`.

```bash
uvlisk sync
uvlisk pip install requests
```

`uvlisk` will look for `.uv-version` or `pyproject.toml` in the current directory or any parent directories to determine which version of `uv` to run.

### Version Configuration

**`.uv-version`**:
Simply put the version string in the file.
```
0.4.20
```

**`pyproject.toml`**:
Configure it under `[tool.uv]`.
```toml
[tool.uv]
required-version = "0.4.20"
```
