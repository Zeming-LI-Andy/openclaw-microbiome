import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "/Users/lizeming/Documents/Codes/openclaw-microbiome/papers/figures/microbioagent-architecture-v5-editable-v4.pptx";
const outDir = "/Users/lizeming/Documents/Codes/openclaw-microbiome/papers/.pptx-build-v7";
const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 30000,
});
await fs.writeFile(`${outDir}/existing.inspect.ndjson`, snapshot.ndjson);
for (let i = 0; i < presentation.slides.items.length; i += 1) {
  const slide = presentation.slides.items[i];
  const preview = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(`${outDir}/existing-slide-${i + 1}.png`, new Uint8Array(await preview.arrayBuffer()));
}
console.log(JSON.stringify({ slides: presentation.slides.items.length, inspect: `${outDir}/existing.inspect.ndjson` }));
