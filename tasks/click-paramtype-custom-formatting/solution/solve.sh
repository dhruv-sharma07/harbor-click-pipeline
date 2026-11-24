#!/bin/bash
set -euo pipefail
echo "=========================================="
echo "Harbor v0.25.x Oracle Solution: click-paramtype-custom-formatting"
echo "=========================================="
cd /workspace/click
# Apply Oracle Solution
cat << 'EOF' | patch -p1
--- a/src/click/types.py
+++ b/src/click/types.py
@@ -82,7 +82,7 @@ class ParamType:
     def get_metavar(self, param: t.Optional["Parameter"]) -> t.Optional[str]:
         """Returns the metavar default for this param if it provides one."""
         if self.name is not None:
-            return self.name.upper()
+            return self.name.upper() if self.name else self.__class__.__name__.upper()
         return None
@@ -102,6 +102,9 @@ class ParamType:
         """
         if self.name is None:
             name = self.__class__.__name__.lower()
+        elif not self.name.strip():
+            name = self.__class__.__name__.lower()
         else:
             name = self.name
EOF
echo "[ORACLE] Solution patch successfully applied."
