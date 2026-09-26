import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "tools"))
import check_compatibility


MANIFEST = (pathlib.Path(__file__).parents[1] / "project-manifest.yaml").read_text()


class CompatibilityProbeTests(unittest.TestCase):
    def test_manifest_has_all_pins_and_contracts(self):
        value = check_compatibility.parse_manifest(MANIFEST)
        self.assertEqual(set(value["pins"]), check_compatibility.PROJECTS)
        self.assertEqual(len(value["contracts"]), 6)

    def test_tampered_pin_is_rejected(self):
        tampered = MANIFEST.replace("84652fe8dac5604a8e53bbc0c19f573948a9697c", "0" * 40)
        value = check_compatibility.parse_manifest(tampered)

        def reject(pin, contracts):
            if pin["commit"] == "0" * 40:
                raise ValueError("immutable commit mismatch")
            return {"repository": pin["repository"], "release": pin["release"], "commit": pin["commit"], "tag_verified": True, "contracts": contracts}

        with self.assertRaisesRegex(ValueError, "immutable commit mismatch"):
            check_compatibility.validate(value, reject)

    def test_missing_tag_is_rejected(self):
        value = check_compatibility.parse_manifest(MANIFEST)

        def reject(pin, contracts):
            if pin["repository"].endswith("agent-workflow-ui"):
                raise ValueError("release tag is missing")
            return {"repository": pin["repository"], "release": pin["release"], "commit": pin["commit"], "tag_verified": True, "contracts": contracts}

        with self.assertRaisesRegex(ValueError, "release tag is missing"):
            check_compatibility.validate(value, reject)

    def test_schema_incompatibility_is_rejected(self):
        value = check_compatibility.parse_manifest(MANIFEST)

        def reject(pin, contracts):
            if contracts and contracts[0]["schema_version"] == "1.0":
                raise ValueError("schema mismatch")
            return {"repository": pin["repository"], "release": pin["release"], "commit": pin["commit"], "tag_verified": True, "contracts": contracts}

        with self.assertRaisesRegex(ValueError, "schema mismatch"):
            check_compatibility.validate(value, reject)


if __name__ == "__main__":
    unittest.main()
