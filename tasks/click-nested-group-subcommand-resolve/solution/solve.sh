#!/bin/bash
set -euo pipefail
echo "=========================================="
echo "Harbor v0.25.x Oracle Solution: click-nested-group-subcommand-resolve"
echo "=========================================="
cd /workspace/click
# Apply Oracle Solution
cat << 'EOF' | patch -p1
--- a/src/click/core.py
+++ b/src/click/core.py
@@ -1940,6 +1940,10 @@ class Group(MultiCommand):
     def get_command(self, ctx: Context, cmd_name: str) -> t.Optional[Command]:
         if cmd_name in self.commands:
             return self.commands[cmd_name]
+        # Exact match before prefix resolution
+        for name, cmd in self.commands.items():
+            if name == cmd_name:
+                return cmd
         if not ctx.token_normalize_func and not self.ignore_unknown_options:
             matches = [x for x in self.commands if x.startswith(cmd_name)]
             if len(matches) == 1:
EOF
echo "[ORACLE] Solution patch successfully applied."
