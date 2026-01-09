import os
import sys
import subprocess
import pathlib
import urllib.request
import platform
import tarfile
import tempfile
import shutil

try:
    import tomllib
except ImportError:
    import tomli as tomllib

def get_os_arch():
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        os_name = "macos"
    elif system == "linux":
        os_name = "linux"
    else:
        # For Windows or other OSs where we don't have auto-download logic yet
        # user must install mise manually.
        print(f"uvlisk: Auto-download of mise is not supported on {system}. Please install mise manually.", file=sys.stderr)
        sys.exit(1)

    if machine == "x86_64" or machine == "amd64":
        arch = "x64"
    elif machine == "aarch64" or machine == "arm64":
        arch = "arm64"
    elif machine == "armv7l":
        arch = "armv7"
    else:
        arch = "x64" # Fallback

    return os_name, arch

def ensure_mise():
    # Check if mise is in PATH
    if shutil.which("mise"):
        return "mise"

    # Check XDG_DATA_HOME
    xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    uvlisk_data_dir = os.path.join(xdg_data_home, "uvlisk", "bin")
    mise_path = os.path.join(uvlisk_data_dir, "mise")

    if os.path.exists(mise_path) and os.access(mise_path, os.X_OK):
        return mise_path

    # Download mise
    print("uvlisk: mise not found. Downloading mise...", file=sys.stderr)
    os_name, arch = get_os_arch()

    # Try to determine latest version or use fallback
    try:
        with urllib.request.urlopen("https://github.com/jdx/mise/releases/latest") as response:
            latest_url = response.geturl()
            version = latest_url.split("/")[-1]
    except Exception:
        version = "v2024.11.0" # Fallback

    if not version.startswith("v"):
        version = "v" + version

    url = f"https://github.com/jdx/mise/releases/download/{version}/mise-{version}-{os_name}-{arch}.tar.gz"

    os.makedirs(uvlisk_data_dir, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tar_path = os.path.join(temp_dir, "mise.tar.gz")
            urllib.request.urlretrieve(url, tar_path)

            with tarfile.open(tar_path, "r:gz") as tar:
                # The binary is usually in mise/bin/mise
                try:
                    member = tar.getmember("mise/bin/mise")
                    member.name = "mise" # Rename for extraction
                    tar.extract(member, path=uvlisk_data_dir)
                except KeyError:
                    # Fallback if structure is different
                    tar.extractall(path=temp_dir)
                    found = False
                    for root, dirs, files in os.walk(temp_dir):
                        if "mise" in files:
                            # Verify it's the binary (not a directory named mise)
                            candidate = os.path.join(root, "mise")
                            if os.path.isfile(candidate):
                                shutil.move(candidate, mise_path)
                                found = True
                                break
                    if not found:
                        raise RuntimeError("Could not find mise binary in downloaded archive")
    except Exception as e:
        print(f"Error downloading/installing mise: {e}", file=sys.stderr)
        sys.exit(1)

    # Make executable
    os.chmod(mise_path, 0o755)
    return mise_path

def resolve_uv_version(version):
    """
    Sanitize and resolve the requested uv version.
    Handles PEP 440 constraints:
    - `>=foo` or `<=foo` -> `foo`
    - `==foo` -> `foo`
    - `foo` -> `foo`
    - `latest` or empty -> `latest`
    - `~=foo`, `^foo`, `<foo`, `>foo`, `!=foo`, `*` -> Raise Error
    """
    if not version:
        return "latest"

    version = version.strip()
    if version == "latest":
        return "latest"

    # Check for disallowed characters or constraints
    # Complex ranges separated by comma
    if "," in version:
        raise ValueError(f"Complex version constraints are not supported: {version}")

    # Wildcards
    if "*" in version:
        raise ValueError(f"Wildcard versions are not supported: {version}")

    # Exclusive constraints and other complex operators
    # Check for prefix operators
    if version.startswith(">=") or version.startswith("<="):
        return version[2:].strip()

    if version.startswith("=="):
        if version.startswith("==="):
             raise ValueError(f"Arbitrary equality '===' is not supported: {version}")
        return version[2:].strip()

    if version.startswith("<") or version.startswith(">") or \
       version.startswith("~=") or version.startswith("^") or \
       version.startswith("!="):
        raise ValueError(f"Unsupported version constraint: {version}")

    # If no known operator prefix, assume it's a version literal
    return version

def find_uv_version():
    # Start from current directory and walk up
    current_dir = pathlib.Path.cwd()
    root_dir = pathlib.Path(current_dir.root)

    while True:
        # Check .uv-version
        uv_version_file = current_dir / ".uv-version"
        if uv_version_file.exists():
            return resolve_uv_version(uv_version_file.read_text().strip())

        # Check pyproject.toml
        pyproject_file = current_dir / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, "rb") as f:
                    data = tomllib.load(f)
                    required_version = data.get("tool", {}).get("uv", {}).get("required-version")
                    if required_version:
                        return resolve_uv_version(required_version)
            except Exception:
                pass # Ignore parsing errors

        if current_dir.parent == current_dir:
            break

        current_dir = current_dir.parent

    return "latest"

def main():
    try:
        mise_bin = ensure_mise()
        uv_version = find_uv_version()

        cmd = [mise_bin, "exec", f"uv@{uv_version}", "--", "uv"] + sys.argv[1:]

        # Replace current process
        if platform.system() == "Windows":
             sys.exit(subprocess.call(cmd))
        else:
             os.execvp(cmd[0], cmd)

    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"uvlisk error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
