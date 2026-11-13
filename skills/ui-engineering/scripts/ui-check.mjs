#!/usr/bin/env node
// Quick UI check: load a page at phone and desktop width, save screenshots,
// and report console errors, horizontal overflow, controls without an
// accessible name, images without alt or size, and the keyboard focus order.
//
// Usage (from the project root, against your own dev or preview server):
//   node <skill-dir>/scripts/ui-check.mjs http://localhost:5173/settings [--out .ui-check]
//
// Uses Playwright from the project (playwright or playwright-core), falling
// back to a global install. With playwright-core it drives the installed
// Google Chrome. Exit code 0 = checks ran (read the report), 2 = could not run.
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { join, resolve } from "node:path";

const args = process.argv.slice(2);
const url = args.find((a) => /^https?:\/\/|^file:\/\//.test(a));
const outIndex = args.indexOf("--out");
const out = resolve(outIndex >= 0 ? args[outIndex + 1] : ".ui-check");
if (!url) {
  console.error("usage: node ui-check.mjs <url> [--out dir]");
  process.exit(2);
}

function loadPlaywright() {
  const requireFromProject = createRequire(join(process.cwd(), "noop.js"));
  for (const name of ["playwright", "playwright-core"]) {
    try {
      return requireFromProject(name);
    } catch {}
  }
  return null;
}

const pw = loadPlaywright();
if (!pw) {
  console.error("Playwright not found in this project. Install it with `npm i -D playwright-core` " +
    "(uses your installed Chrome) or `npm i -D playwright && npx playwright install chromium`, then re-run.");
  process.exit(2);
}

async function launch() {
  try {
    return await pw.chromium.launch();
  } catch (first) {
    try {
      return await pw.chromium.launch({ channel: "chrome" });
    } catch {
      throw first;
    }
  }
}

mkdirSync(out, { recursive: true });
const browser = await launch();
const report = [];
try {
  for (const width of [375, 1280]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const errors = [];
    page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });
    page.on("pageerror", (err) => errors.push(String(err.message || err)));
    page.on("requestfailed", (req) => errors.push(`request failed: ${req.url()}`));
    await page.goto(url, { waitUntil: "load" });
    await page.waitForTimeout(500);
    const shot = join(out, `page-${width}.png`);
    await page.screenshot({ path: shot, fullPage: true });

    const facts = await page.evaluate(() => {
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none";
      };
      const describe = (el) => {
        const tag = el.tagName.toLowerCase();
        const id = el.id ? `#${el.id}` : "";
        const cls = typeof el.className === "string" && el.className.trim()
          ? "." + el.className.trim().split(/\s+/).slice(0, 2).join(".") : "";
        return `${tag}${id}${cls}`;
      };
      const name = (el) => {
        const labelledby = el.getAttribute("aria-labelledby");
        const fromIds = labelledby ? labelledby.split(/\s+/).map((i) => document.getElementById(i)?.textContent || "").join(" ") : "";
        const labels = el.labels ? [...el.labels].map((l) => l.textContent).join(" ") : "";
        const img = el.querySelector?.("img[alt]")?.getAttribute("alt") || "";
        return (el.getAttribute("aria-label") || fromIds || labels || el.textContent || img ||
          el.getAttribute("title") || el.getAttribute("placeholder") || el.value || "").trim();
      };
      const controls = [...document.querySelectorAll(
        "button, a[href], input:not([type=hidden]), select, textarea, [role=button], [role=link], [role=tab], [role=checkbox], [role=switch]")]
        .filter(visible);
      const unnamed = controls.filter((el) => !name(el)).map(describe);
      const clickDivs = [...document.querySelectorAll("div[onclick], span[onclick], li[onclick]")].map(describe);
      const images = [...document.querySelectorAll("img")].filter(visible);
      const noAlt = images.filter((img) => !img.hasAttribute("alt")).map((img) => img.getAttribute("src"));
      const noSize = images.filter((img) => !img.getAttribute("width") || !img.getAttribute("height")).map((img) => img.getAttribute("src"));
      const overflowBy = document.documentElement.scrollWidth - window.innerWidth;
      const wide = overflowBy > 0 ? [...document.querySelectorAll("body *")]
        .filter((el) => el.getBoundingClientRect().right > window.innerWidth + 1).slice(0, 5).map(describe) : [];
      return {
        title: document.title, lang: document.documentElement.lang, h1: document.querySelectorAll("h1").length,
        controls: controls.length, unnamed, clickDivs, noAlt, noSize, overflowBy, wide,
      };
    });

    const focus = [];
    if (width === 1280) {
      for (let i = 0; i < 25; i++) {
        await page.keyboard.press("Tab");
        const step = await page.evaluate(() => {
          const el = document.activeElement;
          if (!el || el === document.body) return null;
          const s = getComputedStyle(el);
          const ring = (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== "none";
          const label = (el.getAttribute("aria-label") || el.textContent || el.getAttribute("placeholder") || el.tagName).trim().slice(0, 40);
          return { label, ring };
        });
        if (!step) break;
        if (focus.length && focus[0].label === step.label && i > 1) break;
        focus.push(step);
      }
    }
    report.push({ width, screenshot: shot, errors, ...facts, focus });
    await page.close();
  }
} finally {
  await browser.close();
}

for (const r of report) {
  console.log(`\n== ${r.width}px  ${url}`);
  console.log(`screenshot: ${r.screenshot}  (open it and look)`);
  console.log(`title: ${JSON.stringify(r.title)}  lang: ${r.lang || "MISSING"}  h1 count: ${r.h1}  controls: ${r.controls}`);
  console.log(`console/page errors: ${r.errors.length ? "\n  - " + r.errors.join("\n  - ") : "none"}`);
  console.log(`horizontal overflow: ${r.overflowBy > 0 ? `${r.overflowBy}px, widest: ${r.wide.join(", ")}` : "none"}`);
  console.log(`controls without an accessible name: ${r.unnamed.length ? r.unnamed.join(", ") : "none"}`);
  console.log(`clickable div/span/li: ${r.clickDivs.length ? r.clickDivs.join(", ") : "none"}`);
  console.log(`images without alt: ${r.noAlt.length ? r.noAlt.join(", ") : "none"}`);
  console.log(`images without width/height: ${r.noSize.length ? r.noSize.join(", ") : "none"}`);
  if (r.focus.length) {
    console.log("keyboard focus order (Tab):");
    r.focus.forEach((f, i) => console.log(`  ${i + 1}. ${f.label}${f.ring ? "" : "   <- no visible focus style"}`));
  }
}
