from binarybyte.core.config import default_config
from binarybyte.eval.checks.secrets import check_secrets

CLEAN_DIFF = """\
diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,4 @@
+import os
+print("hello world")
"""

AWS_KEY_DIFF = """\
diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1 +1,2 @@
+AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
"""

PRIVATE_KEY_DIFF = """\
diff --git a/keys/deploy.pem b/keys/deploy.pem
--- /dev/null
+++ b/keys/deploy.pem
@@ -0,0 +1 @@
+-----BEGIN RSA PRIVATE KEY-----
"""

GITHUB_PAT_DIFF = """\
diff --git a/ci.sh b/ci.sh
--- a/ci.sh
+++ b/ci.sh
@@ -1 +1,2 @@
+export GITHUB_TOKEN="ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"
"""

API_KEY_ASSIGNMENT_DIFF = """\
diff --git a/settings.py b/settings.py
--- a/settings.py
+++ b/settings.py
@@ -1 +1,2 @@
+api_key = "sk-abcdefghij1234567890abcdefghij"
"""


def test_clean_diff_passes():
    config = default_config()
    result = check_secrets(CLEAN_DIFF, config)
    assert result.passed is True
    assert result.name == "secret_detection"


def test_aws_key_detected():
    config = default_config()
    result = check_secrets(AWS_KEY_DIFF, config)
    assert result.passed is False
    assert any("AKIA" in d for d in result.details)


def test_private_key_detected():
    config = default_config()
    result = check_secrets(PRIVATE_KEY_DIFF, config)
    assert result.passed is False
    assert any("PRIVATE KEY" in d for d in result.details)


def test_github_pat_detected():
    config = default_config()
    result = check_secrets(GITHUB_PAT_DIFF, config)
    assert result.passed is False
    assert any("ghp_" in d for d in result.details)


def test_api_key_assignment_detected():
    config = default_config()
    result = check_secrets(API_KEY_ASSIGNMENT_DIFF, config)
    assert result.passed is False


def test_scan_secrets_disabled():
    config = default_config()
    config.eval.safety.scan_secrets = False
    result = check_secrets(AWS_KEY_DIFF, config)
    assert result.passed is True
    assert "disabled" in result.details[0].lower()


def test_empty_diff():
    config = default_config()
    result = check_secrets("", config)
    assert result.passed is True
