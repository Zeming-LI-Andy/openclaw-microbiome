import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const source = "/Users/lizeming/Documents/Codes/openclaw-microbiome/papers/figures/microbioagent-architecture-v5-editable-v4.pptx";
const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const result = presentation.help("*", {
  search: "shape delete remove shapes.delete deleteAll slide.shapes",
  include: ["index", "examples", "notes"],
  maxChars: 15000,
});
console.log(result.ndjson);
