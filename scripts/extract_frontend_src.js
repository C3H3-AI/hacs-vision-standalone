// 从 panel.js.map 的 sourcesContent 还原 Vision 前端源码工程
const fs = require("fs");
const path = require("path");

const mapPath = path.join(__dirname, "..", "custom_components", "hacs", "vision", "frontend", "panel.js.map");
const outBase = path.join(__dirname, "..", "custom_components", "hacs", "vision", "frontend_src");

const map = JSON.parse(fs.readFileSync(mapPath, "utf-8"));
const sources = map.sources || [];
const contents = map.sourcesContent || [];

let recovered = 0;
let skipped = 0;
for (let i = 0; i < sources.length; i++) {
  const rel = sources[i];          // 如 ../../../frontend_src/src/api.js
  const content = contents[i];
  if (!content) { skipped++; continue; }
  // 取 "frontend_src/" 之后的部分，落入 frontend_src/
  const marker = "frontend_src/";
  const idx = rel.indexOf(marker);
  const sub = idx >= 0 ? rel.slice(idx + marker.length) : rel.replace(/^(\.\.\/)+/, "");
  const dest = path.join(outBase, sub);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, content, "utf-8");
  recovered++;
  console.log("✓", sub);
}
console.log(`\n还原完成：成功 ${recovered} 个，跳过(空) ${skipped} 个`);
console.log("输出目录：", outBase);
