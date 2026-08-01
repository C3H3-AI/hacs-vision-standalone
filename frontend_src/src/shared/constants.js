/**
 * Shared constants for HACS Vision
 */

/**
 * Generate a deterministic HSL color from a string (domain/category name)
 * Falls back to a predefined color if the category is in the static map.
 */
function hashStringToHSL(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
    hash = hash & hash; // Convert to 32bit integer
  }
  const hue = Math.abs(hash % 360);
  return `hsl(${hue}, 55%, 48%)`;
}

/**
 * Richer category color palette — designed for visual distinctiveness
 * across both light and dark themes.
 */
export const CATEGORY_COLORS = {
  integration: '#1565c0',    // Rich blue
  plugin: '#7b1fa2',         // Deep purple
  theme: '#2e7d32',          // Forest green
  appdaemon: '#e65100',      // Burnt orange
  netdaemon: '#00838f',      // Teal
  python_script: '#f9a825',  // Amber
  template: '#6a1b9a',       // Dark magenta
  dashboard: '#f57f17',      // Golden orange
  // Additional categories for broader coverage
  automation: '#c62828',     // Deep red
  addon: '#283593',          // Indigo
  scene: '#00695c',          // Dark teal
  sensor: '#37474f',         // Blue-grey
};

export function getCategoryColor(category) {
  return CATEGORY_COLORS[category] || hashStringToHSL(category || 'default');
}