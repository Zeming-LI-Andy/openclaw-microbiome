declare module "openclaw/plugin-sdk/plugin-entry" {
  export type PluginLogger = Pick<Console, "info" | "warn" | "error" | "debug">;

  export type PluginToolContext = {
    workspaceDir?: string;
    agentId?: string;
    sessionKey?: string;
    /** Ephemeral conversation UUID; regenerated on /new and /reset. */
    sessionId?: string;
  };

  export type PluginAgentTool = {
    name: string;
    description: string;
    parameters: unknown;
    execute: (
      id: string,
      params: Record<string, unknown>,
    ) => Promise<{
      content: Array<{ type: "text"; text: string }>;
      details?: unknown;
    }>;
  };

  export type PluginRegisterApi = {
    pluginConfig?: unknown;
    logger?: PluginLogger;
    registerTool: (
      tool: PluginAgentTool | ((ctx: PluginToolContext) => PluginAgentTool | null | undefined),
      opts?: { optional?: boolean; name?: string },
    ) => void;
    /** Typed lifecycle hooks (e.g. gateway_start). */
    on?: (
      event: string,
      handler: (
        event: unknown,
        ctx: { workspaceDir?: string; config?: unknown; port?: number },
      ) => void | Promise<void>,
    ) => void;
  };

  export function definePluginEntry(def: {
    id: string;
    name: string;
    description: string;
    configSchema?: unknown;
    register: (api: PluginRegisterApi) => void | Promise<void>;
  }): {
    id: string;
    name: string;
    description: string;
    configSchema?: unknown;
    register: (api: PluginRegisterApi) => void | Promise<void>;
  };
}
