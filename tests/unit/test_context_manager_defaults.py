from harness.context_managers import build_context_manager
from harness.context_managers.external_memory import ScratchpadStrategy


def _scratchpad_strategy(manager):
    if manager is None:
        return None
    for strategy in manager.strategies:
        if isinstance(strategy, ScratchpadStrategy):
            return strategy
    return None


def test_default_scratchpad_opt_in_uses_3000_tokens(monkeypatch):
    monkeypatch.delenv("CM_SCRATCHPAD", raising=False)
    monkeypatch.delenv("CM_SCRATCHPAD_MAX_TOKENS", raising=False)

    manager = build_context_manager(default_scratchpad=True)
    scratchpad = _scratchpad_strategy(manager)

    assert scratchpad is not None
    assert scratchpad.max_tokens == 3000


def test_cm_scratchpad_env_can_disable_default(monkeypatch):
    monkeypatch.setenv("CM_SCRATCHPAD", "0")

    manager = build_context_manager(default_scratchpad=True)

    assert _scratchpad_strategy(manager) is None


def test_cm_scratchpad_max_tokens_env_still_overrides(monkeypatch):
    monkeypatch.delenv("CM_SCRATCHPAD", raising=False)
    monkeypatch.setenv("CM_SCRATCHPAD_MAX_TOKENS", "4096")

    manager = build_context_manager(default_scratchpad=True)
    scratchpad = _scratchpad_strategy(manager)

    assert scratchpad is not None
    assert scratchpad.max_tokens == 4096
