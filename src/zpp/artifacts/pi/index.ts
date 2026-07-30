import { execFile } from "node:child_process";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

function resolveTraits(cwd: string): Promise<string> {
  return new Promise((resolve, reject) => {
    execFile("zpp", ["resolve"], { cwd, encoding: "utf8" }, (error, stdout) => {
      if (error) {
        reject(error);
        return;
      }
      resolve(stdout);
    });
  });
}

export default function zpp(pi: ExtensionAPI) {
  pi.on("before_agent_start", async (event, ctx) => {
    try {
      const traits = await resolveTraits(event.systemPromptOptions.cwd);
      if (!traits) {
        return;
      }
      return { systemPrompt: `${event.systemPrompt}\n\n${traits}` };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      ctx.ui.notify(`ZPP trait resolution failed: ${message}`, "error");
      return;
    }
  });
}
