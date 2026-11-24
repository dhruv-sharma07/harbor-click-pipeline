#!/bin/bash
set -euo pipefail
echo "=========================================="
echo "Harbor v0.25.x Oracle Solution: click-hide-sensitive-prompt-default"
echo "=========================================="
cd /workspace/click
# Apply Oracle Solution
cat << 'EOF' | patch -p1
--- a/src/click/core.py
+++ b/src/click/core.py
@@ -2545,6 +2545,9 @@ class Option(Parameter):
         default: t.Any = None,
         **extra: t.Any,
     ) -> t.Any:
+        prompt_default = default
+        if self.hide_input and default is not None:
+            prompt_default = "******"
         return prompt(
             prompt_string,
             default=prompt_default,
EOF
echo "[ORACLE] Solution patch successfully applied."
