import { execFile, spawn } from "node:child_process";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

function resolveTraits(cwd: string): Promise<string> {
  return new Promise((resolve, reject) => {
    execFile("zpp", ["resolve", "--agent", "pi"], { cwd, encoding: "utf8" }, (error, stdout) => {
      if (error) {
        reject(error);
        return;
      }
      resolve(stdout);
    });
  });
}

function guardToolCall(
  cwd: string,
  toolName: string,
  input: unknown,
): Promise<{ block?: boolean; reason?: string }> {
  return new Promise((resolve, reject) => {
    const child = spawn("zpp", ["codespace", "guard", "--agent", "pi"], {
      cwd,
      stdio: ["pipe", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `ZPP codespace guard exited with ${code}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (error) {
        reject(error);
      }
    });
    child.stdin.end(JSON.stringify({ cwd, toolName, input }));
  });
}

export default function zpp(pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    return guardToolCall(ctx.cwd, event.toolName, event.input);
  });

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
