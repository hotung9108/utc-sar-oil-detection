// Validate the reviewed draft; keep the draft and final output separate.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const root = process.cwd();
const skill = process.env.PRESENTATIONS_SKILL || 'C:/Users/hotung/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11011/skills/presentations';
const runtime = process.env.ARTIFACT_RUNTIME || 'C:/Users/hotung/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES ??= path.join(runtime,'node/node_modules');
const { finalizePresentation } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const tables = [3,5,8,10,11,12,13,14,19,21];
await fs.mkdir(path.join(root, 'deliverables/presentation'), {recursive:true});
const result = await finalizePresentation({
  workspaceDir:root,
  candidatePath:path.join(root,'.cache/slides-v4/SAR_SOS_draft.pptx'),
  finalPath:path.join(root,'deliverables/presentation/SAR_SOS_review_v4.pptx'),
  pythonExecutable:path.join(runtime,'python/python.exe'),
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],
  explicitTotalSlideCount:21,
  requiredNativeTableOwnerSlides:tables,
  requiredNativeChartOwnerSlides:[],
  fontPolicy:{basis:'design',families:['Arial']},
  verifyArtifactToolImport:true,
  receiptPath:path.join(root,'.cache/slides-v4/final_validation.json'),
});
console.log(JSON.stringify(result));
