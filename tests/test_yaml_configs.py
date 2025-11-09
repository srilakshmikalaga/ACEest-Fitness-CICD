import pytest
import yaml
from pathlib import Path

# Directories containing YAML files — adjust as needed
YAML_DIRS = ["k8s", "helm", ".github/workflows"]

def load_yaml(file_path):
    """Safely load one or multiple YAML documents from a file."""
    with open(file_path, "r") as f:
        try:
            docs = list(yaml.safe_load_all(f))
            if len(docs) == 1:
                return docs[0]
            return docs
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML syntax in {file_path}: {e}")

@pytest.mark.parametrize("yaml_file", [
    str(p) for folder in YAML_DIRS if Path(folder).exists()
    for p in Path(folder).rglob("*.yaml")
])
def test_yaml_is_valid(yaml_file):
    """
    ✅ Ensure all YAML files are syntactically valid.
    Supports multi-document YAMLs (--- separated) like Kubernetes manifests.
    """
    with open(yaml_file, "r") as f:
        try:
            list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML syntax in {yaml_file}: {e}")

def test_k8s_yaml_has_required_keys():
    """
    ✅ Verify that all Kubernetes YAML manifests have required top-level keys.
    Works even for multi-document YAMLs.
    """
    k8s_dir = Path("k8s")
    if not k8s_dir.exists():
        pytest.skip("No k8s directory found.")

    for file in k8s_dir.glob("*.yaml"):
        data = load_yaml(file)
        docs = data if isinstance(data, list) else [data]

        for d in docs:
            assert isinstance(d, dict), f"{file} must be a YAML mapping"
            assert "apiVersion" in d, f"{file} missing apiVersion"
            assert "kind" in d, f"{file} missing kind"
            assert "metadata" in d, f"{file} missing metadata section"

            # Optional: print warning for multi-doc YAMLs
            if isinstance(data, list) and len(data) > 1:
                print(f"⚠️  {file} contains multiple YAML documents (---).")

def test_no_empty_yaml_files():
    """Ensure no YAML files are completely empty."""
    for folder in YAML_DIRS:
        if not Path(folder).exists():
            continue
        for yaml_file in Path(folder).rglob("*.yaml"):
            content = Path(yaml_file).read_text().strip()
            assert content, f"{yaml_file} is empty!"
