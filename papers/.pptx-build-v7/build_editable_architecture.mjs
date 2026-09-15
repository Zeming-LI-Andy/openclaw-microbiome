import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { icons } from "lucide";

const SKILL_DIR = "/Users/lizeming/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const workspaceDir = "/Users/lizeming/Documents/Codes/openclaw-microbiome/papers";
const TMP_DIR = path.join(workspaceDir, ".pptx-build-v7");
const FINAL_PPTX = path.join(workspaceDir, "figures", "microbioagent-architecture-v7-editable-v2.pptx");
const RUNTIME_PYTHON = "/Users/lizeming/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const FONT = "Arial";

const { finalizePresentation } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href,
);

await fs.mkdir(TMP_DIR, { recursive: true });

const W = 1840;
const H = 855;
const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const slide = presentation.slides.add();
slide.background.fill = "#FFFFFF";

const C = {
  navy: "#062B6F",
  blue: "#087CE5",
  blueDark: "#153E75",
  blueLine: "#1888E9",
  bluePale: "#EAF6FF",
  bluePanel: "#E8F4FC",
  coralPanel: "#FFF5F2",
  orange: "#F46B08",
  orangePale: "#FFF1E5",
  teal: "#008E8A",
  tealPale: "#E8FBF8",
  aquaPale: "#EAF9F8",
  purple: "#7B2CBF",
  purplePale: "#F1E7FA",
  green: "#07968D",
  greenPale: "#EBFAF7",
  white: "#FFFFFF",
  line: "#C7DAEA",
  text: "#062B6F",
  lightText: "#385A7C",
};

function addShape(x, y, w, h, fill, line = C.line, radius = 12, geometry = "roundRect") {
  return slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: 1.5 },
    ...(geometry === "roundRect" || geometry === "rect" ? { borderRadius: radius } : {}),
  });
}

function styleText(shape, { size = 18, bold = false, color = C.text, align = "left", valign = "middle" } = {}) {
  shape.text.style = {
    typeface: FONT,
    fontSize: size,
    bold,
    color,
    autoFit: "shrinkText",
  };
  shape.text.alignment = align;
  shape.text.verticalAlignment = valign;
  shape.text.autoFit = "shrinkText";
  return shape;
}

function addText(text, x, y, w, h, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  return styleText(shape, opts);
}

function addBox(text, x, y, w, h, opts = {}) {
  const shape = addShape(x, y, w, h, opts.fill ?? C.white, opts.line ?? C.blueLine, opts.radius ?? 8);
  shape.text = text;
  styleText(shape, {
    size: opts.size ?? 17,
    bold: opts.bold ?? false,
    color: opts.color ?? C.text,
    align: opts.align ?? "center",
    valign: opts.valign ?? "middle",
  });
  return shape;
}

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function iconSvg(name, color = C.blue, strokeWidth = 2.2) {
  const nodes = icons[name];
  if (!nodes) throw new Error(`Missing Lucide icon: ${name}`);
  const parts = nodes.map(([tag, attrs]) => {
    const a = Object.entries(attrs).map(([k, v]) => `${k}="${esc(v)}"`).join(" ");
    return `<${tag} ${a}/>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round">${parts}</svg>`;
}

function addIcon(name, x, y, w, h, color = C.blue, alt = name) {
  const bytes = new TextEncoder().encode(iconSvg(name, color));
  return slide.images.add({
    blob: bytes,
    contentType: "image/svg+xml",
    alt,
    fit: "contain",
    position: { left: x, top: y, width: w, height: h },
  });
}

function addPanel(letter, title, x, w, fill, line) {
  addShape(x, 18, w, 694, fill, line, 16);
  addText(letter, x + 12, 22, 28, 40, { size: 25, bold: true });
  addText(title, x + 48, 22, w - 58, 40, { size: 25, bold: true });
}

function addHeader(text, iconName, x, y, w, h, fill, size = 24) {
  const header = addShape(x, y, w, h, fill, fill, 8);
  if (iconName) addIcon(iconName, x + 18, y + 9, h - 18, h - 18, C.white, `${text} icon`);
  addText(text, x + (iconName ? h + 8 : 10), y + 2, w - (iconName ? h + 20 : 20), h - 4, {
    size,
    bold: true,
    color: C.white,
    align: iconName ? "left" : "center",
  });
  return header;
}

function addRightArrow(x, y, w = 14, h = 12, color = C.navy) {
  return slide.shapes.add({
    geometry: "rightArrow",
    position: { left: x, top: y, width: w, height: h },
    fill: color,
    line: { fill: color, width: 0.5 },
  });
}

function addDownArrow(x, y, w = 11, h = 14, color = C.navy) {
  return slide.shapes.add({
    geometry: "downArrow",
    position: { left: x, top: y, width: w, height: h },
    fill: color,
    line: { fill: color, width: 0.5 },
  });
}

function addDivider(x, y, w, color = C.line) {
  return slide.shapes.add({
    geometry: "line",
    position: { left: x, top: y, width: w, height: 0 },
    fill: "none",
    line: { style: "solid", fill: color, width: 1 },
  });
}

function addProcessRow(title, y, fill, line, items, widths) {
  addShape(856, y, 516, y === 244 ? 132 : y === 390 ? 146 : 148, fill, line, 10);
  addText(title, 868, y + 5, 492, 34, { size: 21, bold: true });
  const start = y + 50;
  const h = y === 244 ? 68 : y === 390 ? 78 : 82;
  let x = 866;
  const nodes = [];
  for (let i = 0; i < items.length; i += 1) {
    const node = addBox(items[i], x, start, widths[i], h, { fill: C.white, line, size: 13, bold: false });
    nodes.push(node);
    if (i < items.length - 1) addRightArrow(x + widths[i] + 2, start + h / 2 - 6, 10, 12, C.navy);
    x += widths[i] + 14;
  }
  return nodes;
}

// Main panels
addPanel("a", "Agent orchestration", 18, 382, C.bluePanel, "#A7D4F2");
addPanel("b", "Dynamic resource selection", 414, 420, C.coralPanel, "#E8CCD0");
addPanel("c", "Local end-to-end analysis", 844, 540, "#F2FBFA", C.teal);
addPanel("d", "Results and provenance", 1394, 428, C.bluePanel, "#A7D4F2");

// Panel a: user input
addShape(30, 72, 168, 626, C.white, C.blueDark, 10);
addHeader("User input", null, 30, 72, 168, 54, C.blueDark, 24);
const userItems = [
  ["MessageSquareMore", "Research\nquestion", 145],
  ["FileText", "Raw reads\n(FASTQ, etc.)", 255],
  ["TableProperties", "Metadata\n(sample info,\nphenotypes, etc.)", 387],
  ["UserRound", "User feedback\n(requests,\nclarifications, etc.)", 553],
];
for (const [icon, label, y] of userItems) {
  addIcon(icon, 43, y, 36, 36, C.blue, `${label.replaceAll("\n", " ")} icon`);
  addText(label, 85, y - 14, 102, 72, { size: 16.5, bold: label.startsWith("Research") });
}
addDivider(44, 223, 140);
addDivider(44, 333, 140);
addDivider(44, 465, 140);

// Panel a: prompts and Harness
addShape(208, 72, 180, 154, C.white, C.blueLine, 10);
addText("Local workspace\nprompts", 216, 77, 164, 52, { size: 21, bold: true, align: "center" });
const promptRows = [["AGENTS.md", 137], ["CODING.md", 165], ["TOOLS.md", 193]];
for (const [label, y] of promptRows) {
  addIcon("FileCode2", 232, y, 20, 20, C.navy, `${label} icon`);
  addText(label, 260, y - 3, 112, 26, { size: 16.5, bold: true });
}
addDownArrow(293, 228, 12, 15);

addShape(208, 247, 180, 451, "#EAF5FF", C.blueLine, 10);
addHeader("Harness", null, 208, 247, 180, 42, C.blue, 24);
const harness = [
  ["Link2", "Job binding", "Create / reuse job directory", 297],
  ["SearchCheck", "Skill discovery\n& review", "", 370],
  ["BrainCircuit", "Plan and reason", "", 443],
  ["GitFork", "Step dispatcher", "", 516],
  ["Cog", "Executor", "", 589],
];
for (let i = 0; i < harness.length; i += 1) {
  const [icon, label, sub, y] = harness[i];
  addShape(216, y, 164, 62, C.white, C.blueLine, 8);
  addIcon(icon, 226, y + 14, 32, 32, C.blue, `${label.replaceAll("\n", " ")} icon`);
  addText(label, 266, y + (sub ? 4 : 5), 106, sub ? 28 : 50, { size: sub ? 17 : 17.5, bold: true, align: "center" });
  if (sub) addText(sub, 262, y + 33, 112, 22, { size: 11.5, color: C.lightText, align: "center" });
  if (i < harness.length - 1) addDownArrow(293, y + 63, 11, 10);
}
addRightArrow(194, 366, 14, 16);
addRightArrow(388, 624, 26, 18);

// Panel b: tool repository
addShape(432, 72, 384, 310, C.white, C.orange, 10);
addHeader("Tool repository", "Wrench", 432, 72, 384, 46, C.orange, 24);
const toolRows = [
  ["16S", "QIIME 2, DADA2, PICRUSt2", 119, 34],
  ["Read-based", "KneadData, MetaPhlAn,\nHUMAnN", 153, 44],
  ["Assembly / MAG", "Aviary, CheckM2, GTDB-Tk", 197, 34],
  ["Annotation", "eggNOG-mapper, Bakta,\nRGI, VFDB, gapseq,\nantiSMASH, gutSMASH", 231, 66],
  ["Statistics &\nvisualization", "MaAsLin 3, scikit-bio,\nggplot2, Matplotlib,\nPython, R", 297, 76],
];
for (const [cat, list, y, h] of toolRows) {
  addText(cat, 442, y, 134, h, { size: 16.5, bold: true });
  addText(list, 578, y, 228, h, { size: 15.3 });
  if (y + h < 373) addDivider(440, y + h, 368, "#E8D6C7");
}
addText("Dynamic tool and\ndatabase selection", 556, 386, 182, 48, { size: 17, bold: true, align: "center" });
addDownArrow(596, 415, 12, 17);
addRightArrow(410, 414, 20, 14, C.navy);
addRightArrow(824, 414, 20, 14, C.navy);

// Panel b: reference repository
addShape(432, 438, 384, 260, C.white, C.purple, 10);
addHeader("Reference database repository", "Database", 432, 438, 384, 43, C.purple, 21.5);
const dbs = ["SILVA", "MetaPhlAn / ChocoPhlAn", "HUMAnN ChocoPhlAn / UniRef", "EggNOG", "GTDB / CheckM2", "CARD / VFDB / Bakta", "KEGG / MetaCyc", "gapseq / antiSMASH / gutSMASH"];
dbs.forEach((db, i) => addBox(db, 450, 486 + i * 26, 348, 24, { fill: C.purplePale, line: C.purplePale, size: 15, align: "left", radius: 5 }));

// Panel c: local security row
addShape(856, 72, 516, 160, "#DDF8F4", "#DDF8F4", 10);
const security = [
  ["ShieldCheck", "User-controlled\ninfrastructure", 888, 864, 144],
  ["MonitorCog", "Local tools\nand databases", 1050, 1008, 126],
  ["Database", "Raw sequencing\ndata remain local", 1214, 1172, 142],
];
for (const [icon, label, ix, tx, tw] of security) {
  addIcon(icon, ix, 88, 72, 72, C.teal, `${label.replaceAll("\n", " ")} icon`);
  addText(label, tx, 166, tw, 52, { size: 17, bold: true, align: "center" });
}

addProcessRow("16S amplicon", 244, C.bluePale, C.blueLine,
  ["QC", "ASV\ninference", "Taxonomy &\nphylogeny", "Diversity", "Functional\nprediction"],
  [58, 82, 108, 84, 90]);
addProcessRow("Reference-based metagenomics", 390, C.aquaPale, C.teal,
  ["QC & host\ndepletion", "Taxonomic\nprofiling", "Gene families\n& pathways", "Statistics &\nvisualization"],
  [94, 103, 118, 112]);
addProcessRow("Assembly-based metagenomics", 550, C.orangePale, C.orange,
  ["QC", "Assembly", "Binning / MAG\nreconstruction", "Quality &\ntaxonomy", "Gene / metabolic /\nBGC annotation"],
  [45, 84, 128, 90, 93]);

// Panel d: results
addShape(1412, 72, 392, 326, C.white, C.blueLine, 10);
addHeader("User-facing results", "ChartNoAxesColumn", 1412, 72, 392, 54, C.blue, 25);
const resultRows = [
  ["ChartNoAxesColumn", "Figures", 137],
  ["Table2", "Tables", 201],
  ["FileText", "Reports", 265],
  ["Lightbulb", "Biological interpretation", 329],
];
for (const [icon, label, y] of resultRows) {
  addIcon(icon, 1438, y, 51, 51, C.blue, `${label} icon`);
  addText(label, 1502, y - 5, 276, 61, { size: 21, bold: false });
  if (y < 329) addDivider(1430, y + 56, 356);
}

addShape(1412, 412, 392, 286, C.white, C.green, 10);
addHeader("Reproducibility record", "FileCheck2", 1412, 412, 392, 52, C.green, 24);
const recordRows = [
  ["Files", "Intermediate files", 475],
  ["CodeXml", "Generated code", 520],
  ["Settings", "Parameters", 565],
  ["ScrollText", "Logs", 610],
  ["Database", "Tool & database versions", 655],
];
for (const [icon, label, y] of recordRows) {
  addIcon(icon, 1438, y, 34, 34, C.blue, `${label} icon`);
  addText(label, 1484, y - 5, 294, 43, { size: 18.5, bold: false });
  if (y < 655) addDivider(1430, y + 38, 356);
}
addRightArrow(1378, 252, 30, 18, C.navy);
addRightArrow(1378, 582, 30, 18, C.navy);

// Human feedback route
slide.shapes.add({ geometry: "line", position: { left: 294, top: 731, width: 1334, height: 0 }, fill: "none", line: { style: "solid", fill: C.purple, width: 4 } });
slide.shapes.add({ geometry: "line", position: { left: 294, top: 651, width: 0, height: 80 }, fill: "none", line: { style: "solid", fill: C.purple, width: 4 } });
slide.shapes.add({ geometry: "line", position: { left: 1628, top: 698, width: 0, height: 33 }, fill: "none", line: { style: "solid", fill: C.purple, width: 4 } });
slide.shapes.add({ geometry: "triangle", position: { left: 284, top: 641, width: 20, height: 18 }, fill: C.purple, line: { fill: C.purple, width: 1 }, rotation: 0 });
addShape(688, 718, 536, 27, C.white, C.white, 0, "rect");
addText("Human feedback during long-running analysis", 688, 718, 536, 27, { size: 17.5, bold: true, color: C.purple, align: "center" });

// Bottom handoff strip
const strip = addShape(24, 756, 1792, 80, C.white, C.blueDark, 10);
strip.line = { style: "dashed", fill: C.blueDark, width: 1.5 };
addText("Long-running task handoff and resumption", 620, 760, 600, 23, { size: 18, bold: true, align: "center" });
const bottomNodes = [
  ["Play", "exec", 304, 242, C.bluePale, C.blueLine, C.blue],
  ["LoaderCircle", "session_yield", 610, 276, C.bluePale, C.blueLine, C.blue],
  ["MessageSquareMore", "user message or\ncompletion event", 952, 328, C.purplePale, C.purple, C.purple],
  ["RotateCcw", "resume", 1346, 242, C.greenPale, C.green, C.green],
];
for (const [icon, label, x, w, fill, line, iconColor] of bottomNodes) {
  addShape(x, 789, w, 36, fill, line, 8);
  addIcon(icon, x + 18, 796, 22, 22, iconColor, `${label.replaceAll("\n", " ")} icon`);
  addText(label, x + 52, 790, w - 62, 34, { size: 16.5, bold: true, align: "center" });
}
addRightArrow(550, 801, 56, 12, C.navy);
addRightArrow(890, 801, 58, 12, C.navy);
addRightArrow(1284, 801, 58, 12, C.navy);

slide.speakerNotes.textFrame.setText(
  "Editable reconstruction of MicroBioAgent system architecture v7. Diagram text, panels, workflow boxes and arrows are native PowerPoint objects. Icons are embedded Lucide SVG vectors for resolution-independent rendering.",
);

const draftPath = path.join(TMP_DIR, "microbioagent-architecture-v7-editable.candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(draftPath);

const preview = await presentation.export({ slide, format: "png", scale: 1 });
await fs.writeFile(path.join(TMP_DIR, "microbioagent-architecture-v7-editable.preview.png"), new Uint8Array(await preview.arrayBuffer()));
const layout = await slide.export({ format: "layout" });
await fs.writeFile(path.join(TMP_DIR, "microbioagent-architecture-v7-editable.layout.json"), await layout.text());

const requirements = {
  explicitTotalSlideCount: 1,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
};
const fontPolicy = { basis: "design", families: [FONT] };
const expectedSlideSizeEmu = "17526000,8143875";
const stagingDir = path.join(workspaceDir, ".codex-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });

const result = await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath: draftPath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", expectedSlideSizeEmu,
    "--validate-heading-fit",
  ],
  requiredNativeTableOwnerSlides: [],
  fontPolicy,
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "microbioagent-architecture-v7-editable-v2.validation.json"),
});

console.log(JSON.stringify({ final: FINAL_PPTX, draft: draftPath, result }, null, 2));
