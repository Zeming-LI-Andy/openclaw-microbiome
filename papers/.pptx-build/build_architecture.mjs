import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const SKILL_DIR = "/Users/lizeming/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const workspaceDir = "/Users/lizeming/Documents/Codes/openclaw-microbiome";
const TMP_DIR = path.join(workspaceDir, "papers/.pptx-build");
const FINAL_PPTX = path.join(workspaceDir, "papers/figures/microbioagent-architecture-v5-editable-v4.pptx");
const RUNTIME_PYTHON = "/Users/lizeming/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";

const { resolvePresentationFont, finalizePresentation } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href,
);
const family = resolvePresentationFont();

const W = 1840;
const H = 855;
const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const slide = presentation.slides.add();
slide.background.fill = "#FFFFFF";

const C = {
  navy: "#092E73",
  blue: "#087FE8",
  blue2: "#1D93F4",
  paleBlue: "#EAF6FF",
  paleBlue2: "#F5FAFF",
  teal: "#008E8B",
  paleTeal: "#E6FAF7",
  orange: "#F26A00",
  paleOrange: "#FFF3E6",
  purple: "#7D35B2",
  palePurple: "#F4EAFE",
  ink: "#09265D",
  muted: "#536A8A",
  line: "#B9D7EE",
  white: "#FFFFFF",
};

function shape(geometry, x, y, w, h, fill = "none", stroke = "none", sw = 0, radius = 0) {
  return slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: stroke, width: sw },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function textBox(text, x, y, w, h, opts = {}) {
  const s = shape("textbox", x, y, w, h, opts.fill ?? "none", opts.stroke ?? "none", opts.sw ?? 0, opts.radius ?? 0);
  s.text = text;
  s.text.style = {
    typeface: family,
    fontSize: opts.size ?? 18,
    bold: opts.bold ?? false,
    color: opts.color ?? C.ink,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
    autoFit: opts.autoFit ?? "shrinkText",
    wrap: "square",
    insets: opts.insets ?? { top: 4, right: 7, bottom: 4, left: 7 },
  };
  return s;
}

function panel(x, y, w, h, fill, stroke, letter, title) {
  shape("roundRect", x, y, w, h, fill, stroke, 1.6, 16);
  textBox(letter, x + 12, y + 4, 30, 40, { size: 27, bold: true, color: C.navy, align: "center", insets: { top: 0, right: 0, bottom: 0, left: 0 } });
  textBox(title, x + 48, y + 4, w - 58, 40, { size: 25, bold: true, color: C.navy, insets: { top: 0, right: 0, bottom: 0, left: 0 } });
}

function header(text, x, y, w, h, fill, size = 23) {
  return textBox(text, x, y, w, h, { fill, color: C.white, bold: true, size, align: "center", radius: 10, insets: { top: 3, right: 5, bottom: 3, left: 5 } });
}

function badge(label, x, y, d, fill, size = 16) {
  const s = shape("ellipse", x, y, d, d, fill, "none", 0);
  s.text = label;
  s.text.style = { typeface: family, fontSize: size, bold: true, color: C.white, alignment: "center", verticalAlignment: "middle", autoFit: "shrinkText", insets: { top: 1, right: 1, bottom: 1, left: 1 } };
  return s;
}

function divider(x, y, w, color = C.line, sw = 1) {
  return shape("line", x, y, w, 0, "none", color, sw);
}

function connect(a, b, opts = {}) {
  const c = slide.shapes.connect(a, b, {
    kind: opts.kind ?? "straight",
    fromSide: opts.fromSide ?? "right",
    toSide: opts.toSide ?? "left",
    line: { style: "solid", fill: opts.color ?? C.navy, width: opts.width ?? 2 },
    tail: { type: "triangle", width: "sm", length: "sm" },
  });
  c.bringToFront();
  return c;
}

function stepBox(label, x, y, w, h, color, fill) {
  return textBox(label, x, y, w, h, { fill, stroke: color, sw: 1.4, radius: 8, size: 14, bold: true, align: "center", color: C.ink, insets: { top: 4, right: 3, bottom: 4, left: 3 } });
}

function lane(title, x, y, w, h, border, fill, labels, widths) {
  shape("roundRect", x, y, w, h, fill, border, 1.5, 12);
  textBox(title, x + 12, y + 5, w - 24, 34, { size: 22, bold: true, color: C.ink, insets: { top: 0, right: 0, bottom: 0, left: 0 } });
  const gap = 14;
  const total = widths.reduce((a, b) => a + b, 0) + gap * (labels.length - 1);
  let sx = x + (w - total) / 2;
  const nodes = [];
  for (let i = 0; i < labels.length; i++) {
    const n = stepBox(labels[i], sx, y + 50, widths[i], h - 62, border, C.white);
    nodes.push(n);
    sx += widths[i] + gap;
  }
  for (let i = 0; i < nodes.length - 1; i++) connect(nodes[i], nodes[i + 1], { color: C.navy, width: 1.6 });
  return { frame: { x, y, w, h }, nodes };
}

function databaseIcon(x, y, w, h, color) {
  shape("can", x, y, w, h, color, "none", 0);
}

function monitorIcon(x, y, w, h, color) {
  shape("roundRect", x, y, w, h * 0.68, "none", color, 4, 5);
  shape("line", x + w * 0.5, y + h * 0.67, 0, h * 0.20, "none", color, 4);
  shape("line", x + w * 0.30, y + h * 0.87, w * 0.40, 0, "none", color, 4);
}

function resultRow(icon, label, x, y, w, h, color) {
  badge(icon, x + 8, y + 5, h - 10, color, 14);
  textBox(label, x + h + 8, y, w - h - 14, h, { size: 19, bold: false, color: C.ink, insets: { top: 2, right: 2, bottom: 2, left: 4 } });
}

// Main panels
panel(18, 18, 382, 694, C.paleBlue, "#83C8F4", "a", "Agent orchestration");
panel(414, 18, 420, 694, "#FFF8F4", "#E5C6C1", "b", "Dynamic resource selection");
panel(844, 18, 540, 694, "#F1FBFA", C.teal, "c", "Local end-to-end analysis");
panel(1394, 18, 428, 694, C.paleBlue, "#83C8F4", "d", "Results and provenance");

// Panel a: user input
const userX = 30, userY = 72, userW = 168, userH = 626;
shape("roundRect", userX, userY, userW, userH, C.white, C.navy, 1.4, 12);
header("User input", userX, userY, userW, 54, "#214B79", 23);
const userRows = [
  ["Q", "Research\nquestion", 132],
  ["R", "Raw reads\n(FASTQ, etc.)", 242],
  ["M", "Metadata\n(sample info,\nphenotypes, etc.)", 374],
  ["F", "User feedback\n(requests,\nclarifications, etc.)", 540],
];
for (const [ic, label, yy] of userRows) {
  badge(ic, userX + 13, yy + 13, 34, C.blue, 15);
  textBox(label, userX + 53, yy, userW - 62, ic === "M" || ic === "F" ? 91 : 76, { size: 17, bold: ic === "Q", color: C.ink, insets: { top: 3, right: 2, bottom: 3, left: 2 } });
  if (yy < 530) divider(userX + 14, yy + 91, userW - 28);
}

// Panel a: OpenClaw workflow
const flowX = 208, flowW = 180;
shape("roundRect", flowX, 72, flowW, 626, C.white, C.blue, 1.5, 12);
textBox("OpenClaw\nagent workflow", flowX + 7, 74, flowW - 14, 62, { size: 24, bold: true, color: C.navy, align: "center", insets: { top: 2, right: 2, bottom: 2, left: 2 } });
textBox("orchestration runtime\nwithin MicroBioAgent", flowX + 10, 134, flowW - 20, 54, { size: 16, color: C.ink, align: "center", insets: { top: 0, right: 1, bottom: 0, left: 1 } });
const load = stepBox("Load workspace\nprompts", flowX + 8, 190, flowW - 16, 60, C.blue, C.white);
const docs = stepBox("AGENTS.md\nCODING.md\nTOOLS.md", flowX + 18, 260, flowW - 36, 96, C.blue, "#F4FAFF");
const job = stepBox("Create / reuse\njob", flowX + 8, 382, flowW - 16, 64, C.blue, C.white);
const reason = stepBox("Plan and reason", flowX + 8, 476, flowW - 16, 64, C.blue, C.white);
const agent = stepBox("Agent pipeline", flowX + 8, 574, flowW - 16, 64, C.blue, C.white);
connect(load, docs, { fromSide: "bottom", toSide: "top", color: C.navy });
connect(docs, job, { fromSide: "bottom", toSide: "top", color: C.navy });
connect(job, reason, { fromSide: "bottom", toSide: "top", color: C.navy });
connect(reason, agent, { fromSide: "bottom", toSide: "top", color: C.navy });
connect(shape("ellipse", userX + userW - 2, 343, 4, 4, "none", "none", 0), job, { color: C.navy });

// Panel b: tool repository
const bx = 432, bw = 384;
shape("roundRect", bx, 72, bw, 310, C.white, C.orange, 1.5, 12);
header("Tool repository", bx, 72, bw, 46, C.orange, 24);
const toolRows = [
  ["16S", "QIIME 2, DADA2, PICRUSt2"],
  ["Read-based", "KneadData, MetaPhlAn,\nHUMAnN"],
  ["Assembly / MAG", "Aviary, CheckM2, GTDB-Tk"],
  ["Annotation", "eggNOG-mapper, Bakta,\nRGI, VFDB, gapseq,\nantiSMASH, gutSMASH"],
  ["Statistics &\nvisualization", "MaAsLin 3, scikit-bio,\nggplot2, Matplotlib,\nPython, R"],
];
let ty = 119;
const rowHs = [34, 44, 34, 66, 76];
for (let i = 0; i < toolRows.length; i++) {
  const rh = rowHs[i];
  textBox(toolRows[i][0], bx + 10, ty, 134, rh, { size: 15, bold: true, color: C.ink, insets: { top: 2, right: 3, bottom: 2, left: 3 } });
  textBox(toolRows[i][1], bx + 146, ty, bw - 156, rh, { size: 14, color: C.ink, insets: { top: 2, right: 3, bottom: 2, left: 3 } });
  if (i < toolRows.length - 1) divider(bx + 8, ty + rh, bw - 16, "#F1D7C5");
  ty += rh;
}

textBox("Dynamic tool and\ndatabase selection", bx + 124, 386, 182, 48, { size: 17, bold: true, align: "center", color: C.ink, insets: { top: 1, right: 1, bottom: 1, left: 1 } });

// Panel b: reference database repository
shape("roundRect", bx, 438, bw, 260, C.white, C.purple, 1.5, 12);
header("Reference database repository", bx, 438, bw, 43, C.purple, 21);
const dbs = ["SILVA", "MetaPhlAn / ChocoPhlAn", "HUMAnN ChocoPhlAn / UniRef", "EggNOG", "GTDB / CheckM2", "CARD / VFDB / Bakta", "KEGG / MetaCyc", "gapseq / antiSMASH / gutSMASH"];
let dy = 486;
for (const db of dbs) {
  textBox(db, bx + 18, dy, bw - 36, 24, { size: 15, fill: C.palePurple, color: C.ink, radius: 4, insets: { top: 1, right: 8, bottom: 1, left: 12 } });
  dy += 26;
}

// Dynamic selection arrows from agent to resources and resources to panel c
connect(agent, shape("ellipse", bx - 2, 576, 4, 4, "none", "none", 0), { color: C.navy });
shape("line", 400, 421, 432, 0, "none", C.navy, 2);
shape("line", 816, 421, 28, 0, "none", C.navy, 2);

// Panel c security row
shape("roundRect", 856, 72, 516, 160, C.paleTeal, "none", 0, 9);
shape("pentagon", 892, 89, 66, 68, C.teal, "none", 0);
badge("●", 914, 111, 20, C.white, 10);
textBox("User-controlled\ninfrastructure", 864, 166, 144, 52, { size: 17, bold: true, align: "center", color: C.ink, insets: { top: 1, right: 1, bottom: 1, left: 1 } });
monitorIcon(1032, 95, 80, 64, C.teal);
textBox("Local tools\nand databases", 1008, 166, 126, 52, { size: 17, bold: true, align: "center", color: C.ink, insets: { top: 1, right: 1, bottom: 1, left: 1 } });
databaseIcon(1210, 92, 70, 68, C.navy);
badge("L", 1260, 134, 28, C.teal, 14);
textBox("Raw sequencing\ndata remain local", 1172, 166, 142, 52, { size: 17, bold: true, align: "center", color: C.ink, insets: { top: 1, right: 1, bottom: 1, left: 1 } });

lane("16S amplicon", 856, 244, 516, 132, C.blue, "#EAF6FF", ["QC", "ASV\ninference", "Taxonomy", "Phylogeny &\ndiversity", "Functional\nprediction"], [58, 84, 82, 104, 96]);
lane("Reference-based metagenomics", 856, 390, 516, 146, C.teal, C.paleTeal, ["QC & host\ndepletion", "Taxonomic\nprofiling", "Gene families\n& pathways", "Statistics &\nvisualization"], [94, 103, 118, 112]);
lane("Assembly-based metagenomics", 856, 550, 516, 148, C.orange, C.paleOrange, ["QC", "Assembly", "Binning / MAG\nreconstruction", "Quality &\ntaxonomy", "Gene / metabolic /\nBGC annotation"], [45, 84, 130, 78, 103]);

// b-c bidirectional selector cue
const bc1 = shape("ellipse", 818, 205, 5, 5, "none", "none", 0);
const bc2 = shape("ellipse", 846, 205, 5, 5, "none", "none", 0);
const bcLine = slide.shapes.connect(bc1, bc2, { kind: "straight", fromSide: "right", toSide: "left", line: { style: "solid", fill: C.navy, width: 2 }, head: { type: "triangle", width: "sm", length: "sm" }, tail: { type: "triangle", width: "sm", length: "sm" } });
bcLine.bringToFront();

// Panel d sections
const dx = 1412, dw = 392;
shape("roundRect", dx, 72, dw, 326, C.white, C.blue, 1.5, 12);
header("User-facing results", dx, 72, dw, 54, C.blue, 24);
const resultLabels = [["F", "Figures"], ["T", "Tables"], ["R", "Reports"], ["I", "Biological interpretation"]];
let ry = 132;
for (let i = 0; i < resultLabels.length; i++) {
  resultRow(resultLabels[i][0], resultLabels[i][1], dx + 18, ry, dw - 36, 61, C.blue);
  if (i < resultLabels.length - 1) divider(dx + 18, ry + 61, dw - 36);
  ry += 64;
}

shape("roundRect", dx, 412, dw, 286, C.white, C.teal, 1.5, 12);
header("Reproducibility record", dx, 412, dw, 52, C.teal, 23);
const provLabels = [["D", "Intermediate files"], ["</>", "Generated code"], ["P", "Parameters"], ["L", "Logs"], ["DB", "Tool & database versions"]];
let py = 470;
for (let i = 0; i < provLabels.length; i++) {
  resultRow(provLabels[i][0], provLabels[i][1], dx + 18, py, dw - 36, 43, C.teal);
  if (i < provLabels.length - 1) divider(dx + 18, py + 43, dw - 36);
  py += 45;
}

// c-to-d arrows
connect(shape("ellipse", 1378, 259, 4, 4, "none", "none", 0), shape("ellipse", 1408, 259, 4, 4, "none", "none", 0), { color: C.navy });
connect(shape("ellipse", 1378, 589, 4, 4, "none", "none", 0), shape("ellipse", 1408, 589, 4, 4, "none", "none", 0), { color: C.navy });

// Human feedback line
shape("line", 294, 731, 1334, 0, "none", C.purple, 4);
shape("line", 294, 638, 0, 93, "none", C.purple, 4);
shape("triangle", 284, 628, 20, 18, C.purple, "none", 0);
shape("line", 1628, 698, 0, 33, "none", C.purple, 4);
textBox("Human feedback during long-running analysis", 688, 711, 536, 38, { size: 19, bold: true, align: "center", color: C.purple, fill: C.white, insets: { top: 2, right: 8, bottom: 2, left: 8 } });

// Bottom long-running execution strip
shape("roundRect", 24, 756, 1792, 80, C.white, C.navy, 1.4, 10);
textBox("Long-running task handoff and resumption", 620, 751, 600, 30, { size: 20, bold: true, align: "center", color: C.navy, fill: C.white, insets: { top: 1, right: 5, bottom: 1, left: 5 } });
const exec = stepBox("exec", 304, 789, 242, 36, C.blue, C.paleBlue);
const sy = stepBox("session_yield", 610, 789, 276, 36, C.blue, C.paleBlue);
const event = stepBox("user message or completion event", 952, 789, 328, 36, C.purple, C.palePurple);
const resume = stepBox("resume", 1346, 789, 242, 36, C.teal, C.paleTeal);
slide.shapes.add({ geometry: "triangle", position: { left: 326, top: 798, width: 16, height: 16, rotation: 90 }, fill: C.blue, line: { style: "solid", fill: "none", width: 0 } });
for (const [cx, cy, d] of [[632, 797, 7], [643, 802, 7], [632, 807, 7]]) shape("ellipse", cx, cy, d, d, C.blue2, "none", 0);
badge("M", 969, 796, 22, C.purple, 11);
badge("R", 1364, 796, 22, C.teal, 11);
connect(exec, sy, { color: C.navy, width: 2 });
connect(sy, event, { color: C.navy, width: 2 });
connect(event, resume, { color: C.navy, width: 2 });

slide.speakerNotes.textFrame.setText("Editable reconstruction of the MicroBioAgent system architecture figure. All diagram boxes, labels, connectors and icons are native PowerPoint objects.");

await fs.mkdir(TMP_DIR, { recursive: true });
const preview = await presentation.export({ slide, format: "png", scale: 1 });
await fs.writeFile(path.join(TMP_DIR, "microbioagent-architecture-v5-editable-preview.png"), new Uint8Array(await preview.arrayBuffer()));
const layout = await slide.export({ format: "layout" });
await fs.writeFile(path.join(TMP_DIR, "microbioagent-architecture-v5-editable.layout.json"), await layout.text());

const stagingDir = path.join(TMP_DIR, "finalizer");
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const requirements = {
  explicitTotalSlideCount: 1,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
};
const fontPolicy = { basis: "design", families: [family] };
const expectedSlideSizeEmu = "17526000,8143875";

await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", expectedSlideSizeEmu,
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  requiredNativeTableOwnerSlides: [],
  fontPolicy,
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "microbioagent-architecture-v5-editable-v4.pptx.validation.json"),
});

console.log(JSON.stringify({ family, final: FINAL_PPTX, preview: path.join(TMP_DIR, "microbioagent-architecture-v5-editable-preview.png") }, null, 2));
