"""Repo health manager for HACS Vision — A3: proactive invalid-repo detection.

Design:
  - Uses async_track_time_interval for reliable periodic scheduling
  - Non-overlapping runs: skips if a previous cycle is still in progress
  - Scans installed repositories for GitHub-archived or missing (404/renamed)
  - Sends a HA persistent notification when invalid repos are found
  - Manual trigger service (check_invalid_repos) for on-demand checks
"""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_REPO_HEALTH_ENABLED,
    CONF_REPO_HEALTH_INTERVAL,
    CONF_REPO_HEALTH_NOTIFY,
    DEFAULT_REPO_HEALTH_ENABLED,
    DEFAULT_REPO_HEALTH_INTERVAL,
    DEFAULT_REPO_HEALTH_NOTIFY,
)

_LOGGER = logging.getLogger(__name__)

NOTIFICATION_ID = "hacs_vision_repo_health"


class RepoHealthManager:
    """Periodically scans installed repos for archived/missing status on GitHub."""

    def __init__(self, hass: HomeAssistant, operator, data) -> None:
        self.hass = hass
        self.operator = operator
        self.data = data
        self._unsub_interval = None
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_scheduled(self) -> bool:
        return self._unsub_interval is not None

    async def start(self) -> None:
        await self._apply_settings(reschedule=True)
        _LOGGER.info("RepoHealthManager started")

    def stop(self) -> None:
        self._cancel_interval()
        _LOGGER.info("RepoHealthManager stopped")

    async def trigger(self) -> dict:
        """Manual one-shot health check (used by the check_invalid_repos service)."""
        if self._running:
            return {"success": True, "queued": True, "message": "Health check already in progress"}
        return await self._run_check(source="manual")

    async def reload_settings(self) -> None:
        await self._apply_settings(reschedule=True)

    # ── Internal ──

    async def _apply_settings(self, reschedule: bool = False) -> None:
        settings = await self.data.get_settings()
        enabled = settings.get(CONF_REPO_HEALTH_ENABLED, DEFAULT_REPO_HEALTH_ENABLED)
        if not enabled:
            self._cancel_interval()
            _LOGGER.info("Repo health check is disabled in settings")
            return
        if reschedule:
            interval = settings.get(CONF_REPO_HEALTH_INTERVAL, DEFAULT_REPO_HEALTH_INTERVAL)
            self._schedule_interval(interval)

    def _schedule_interval(self, interval_seconds: int) -> None:
        self._cancel_interval()
        interval = timedelta(seconds=max(interval_seconds, 3600))

        async def _first_then_interval(_now=None):
            self._unsub_interval = async_track_time_interval(
                self.hass, self._on_interval, interval
            )
            await self._on_interval(_now)

        self._unsub_interval = self.hass.loop.call_later(
            120, lambda: self.hass.async_create_task(_first_then_interval())
        )
        _LOGGER.info("Repo health scheduled every %d seconds (first cycle in 120s)", interval_seconds)

    def _cancel_interval(self) -> None:
        if self._unsub_interval is not None:
            if hasattr(self._unsub_interval, "cancel"):
                self._unsub_interval.cancel()
            else:
                try:
                    self._unsub_interval()
                except Exception:
                    pass
            self._unsub_interval = None

    async def _on_interval(self, _now) -> None:
        if self._running:
            _LOGGER.debug("Repo health interval: previous cycle still running, skipping")
            return
        if not self.operator.available:
            _LOGGER.debug("Repo health skipped: HACS not available")
            return
        await self._run_check(source="scheduled")

    async def _run_check(self, source: str = "scheduled") -> dict:
        self._running = True
        try:
            invalid = await self.operator.check_invalid_repositories()
            if not invalid:
                _LOGGER.info("Repo health: no invalid repositories found (source=%s)", source)
                return {"success": True, "invalid": [], "source": source}

            _LOGGER.warning(
                "Repo health: found %d invalid repositories (source=%s)", len(invalid), source
            )
            settings = await self.data.get_settings()
            notify = settings.get(CONF_REPO_HEALTH_NOTIFY, DEFAULT_REPO_HEALTH_NOTIFY)
            if notify:
                await self._notify_invalid(invalid)

            return {"success": True, "invalid": invalid, "source": source}
        except Exception as e:
            _LOGGER.error("Repo health check error: %s", e, exc_info=True)
            return {"success": False, "error": str(e), "source": source}
        finally:
            self._running = False

    async def _notify_invalid(self, invalid: list[dict]) -> None:
        archived = [r for r in invalid if r.get("reason") == "archived"]
        missing = [r for r in invalid if r.get("reason") == "missing"]

        lines = ["🔍 HACS Vision - 失效仓库检测", "", f"发现 {len(invalid)} 个失效仓库："]
        if missing:
            lines.append(f"\n❌ 已删除/改名（missing）{len(missing)} 个：")
            for r in missing:
                lines.append(f"  • {r['full_name']}（已装版本 {r.get('installed_version') or '?'}）")
        if archived:
            lines.append(f"\n📦 已被作者归档（archived）{len(archived)} 个：")
            for r in archived:
                lines.append(f"  • {r['full_name']}（已装版本 {r.get('installed_version') or '?'}）")
        lines.append("\n建议：在 HACS 中移除这些仓库，或确认其新地址后重新添加。")

        await self.data.send_persistent_notification(
            "HACS Vision - 失效仓库检测",
            "\n".join(lines),
            notification_id=NOTIFICATION_ID,
        )
