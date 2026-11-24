#!/bin/bash
set -uo pipefail
echo "=========================================="
echo "Harbor v0.25.x Verifier: click-paramtype-custom-formatting"
echo "=========================================="
mkdir -p /logs/verifier
REWARD_FILE="/logs/verifier/reward.txt"
DETAILS_FILE="/logs/verifier/reward.json"
cd /workspace/click
# Activate task environment
source /workspace/venv/bin/activate
# Execute task verifier test suite
echo "[VERIFIER] Running verification test suite..."
pytest /workspace/tests/test_verifier.py -v --tb=short > /logs/verifier/pytest.log 2>&1
TEST_EXIT_CODE=$?
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1.0" > "$REWARD_FILE"
    echo '{"reward": 1.0, "status": "PASSED", "message": "All verification tests passed"}' > "$DETAILS_FILE"
    echo "[VERIFIER] Task completed successfully. Reward: 1.0"
    exit 0
else
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "status": "FAILED", "message": "Verification test failed. Check /logs/verifier/pytest.log"}' > "$DETAILS_FILE"
    echo "[VERIFIER] Task verification failed. Reward: 0.0"
    cat /logs/verifier/pytest.log | tail -n 25
    exit 1
fi
