// Global toast helper with queue support
const _panelMap = new WeakMap();
const _toastQueue = [];
let _toastShowing = false;

export function registerPanel(panel) { _panelMap.set(panel, true); }

export function showToast(msg, type = 'info') {
  let panel = null;
  try {
    const candidates = document.querySelectorAll('hacs-vision-panel');
    for (const c of candidates) {
      if (_panelMap.has(c)) { panel = c; break; }
    }
    if (!panel) panel = candidates[0];
  } catch(e) { /* ignore */ }
  const container = panel?.shadowRoot?.querySelector('#toast-container');
  if (!container) {
    // Fallback: try HA's built-in notification system
    try {
      const hass = panel?.hass || document.querySelector('home-assistant')?.hass;
      if (hass?.callService) {
        hass.callService('persistent_notification', 'create', {
          title: `HACS Vision - ${type === 'error' ? '错误' : '提示'}`,
          message: msg,
          notification_id: `hacs_vision_toast_${Date.now()}`,
        });
        return;
      }
    } catch(e) { /* ignore */ }
    // Last resort: console
    console.warn('Toast container not found:', msg);
    return;
  }

  _toastQueue.push({ msg, type });
  if (!_toastShowing) _showNextToast(container);
}

function _showNextToast(container) {
  if (_toastQueue.length === 0) { _toastShowing = false; return; }
  _toastShowing = true;
  const { msg, type } = _toastQueue.shift();

  const toast = document.createElement('div');
  toast.className = 'toast';
  if (type) toast.classList.add(type);
  toast.textContent = msg;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      toast.remove();
      _showNextToast(container);
    }, 350);
  }, 3000);
}