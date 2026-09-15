import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "/Users/lizeming/Documents/Codes/openclaw-microbiome/papers/figures/microbioagent-architecture-v7-editable-v2.pptx";
const outDir = "/Users/lizeming/Documents/Codes/openclaw-microbiome/papers/.pptx-build-v7";
const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await presentation.inspect({ kind: "slide,textbox,shape,image,notes,layout", maxChars: 40000 });
await fs.writeFile(`${outDir}/final.inspect.ndjson`, snapshot.ndjson);
const slide = presentation.slides.items[0];
const preview = await presentation.export({ slide, format: "png", scale: 1 });
await fs.writeFile(`${outDir}/final-slide-1.png`, new Uint8Array(await preview.arrayBuffer()));
console.log(JSON.stringify({ slides: presentation.slides.items.length, inspect: `${outDir}/final.inspect.ndjson` }));
