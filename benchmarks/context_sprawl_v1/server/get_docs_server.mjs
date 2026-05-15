import { stdin, stdout } from "node:process";

const TOOL_NAME = "get_docs";
const PROFILE = process.env.CONTEXT_SPRAW_PROFILE ?? "baseline";

const SIGNAL_ONLY_HTML = `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>MyOrgAPI — Create User Endpoint</title>
  </head>
  <body>
    <main>
      <h1>MyOrgAPI — Create User Endpoint</h1>
      <h2>POST /users</h2>
      <p>The endpoint accepts a JSON payload with the following structure:</p>
      <pre><code>{
  "tenant_id": string,
  "user": {
    "email": string,
    "display_name": string,
    "role": string (optional)
  },
  "metadata": {
    "source": "api",
    "version": integer
  }
}</code></pre>
      <h2>Rules</h2>
      <ol>
        <li>
          The <code>email</code> field must be lowercased before submission,
          except when the <code>tenant_id</code> starts with
          <code>legacy_</code>. Legacy tenants preserve the original casing for
          backwards compatibility.
        </li>
        <li>
          The <code>role</code> field must be omitted from the payload (not set
          to null, not set to any default value) when the tenant is on the free
          plan. Free-plan tenants are identified by <code>tenant_id</code>
          values starting with <code>free_</code>. This rule applies regardless
          of whether the caller provides a <code>role</code> value — any
          provided role is discarded for free-plan tenants. For all other
          tenants, <code>role</code> defaults to <code>"member"</code> if not
          specified by the caller.
        </li>
        <li>
          The <code>display_name</code> field must be trimmed of leading and
          trailing whitespace, with any sequence of internal whitespace
          collapsed to a single space.
        </li>
        <li>
          The <code>metadata.version</code> field must be <code>2</code> by
          default, but <code>1</code> for any tenant whose ID starts with
          <code>archive_</code>.
        </li>
      </ol>
    </main>
  </body>
</html>`;

const PROFILE_TO_DOCUMENT = {
  baseline: SIGNAL_ONLY_HTML,
  "1:0": SIGNAL_ONLY_HTML,
};

function write(message) {
  stdout.write(`${JSON.stringify(message)}\n`);
}

function respond(id, result) {
  write({ jsonrpc: "2.0", id, result });
}

function respondError(id, code, message) {
  write({ jsonrpc: "2.0", id, error: { code, message } });
}

function handleRequest(message) {
  const { id, method, params } = message;

  if (method === "initialize") {
    respond(id, {
      protocolVersion: params?.protocolVersion ?? "2024-11-05",
      capabilities: { tools: {} },
      serverInfo: {
        name: "context-sprawl-docs",
        version: "0.1.0",
      },
    });
    return;
  }

  if (method === "notifications/initialized") {
    return;
  }

  if (method === "tools/list") {
    respond(id, {
      tools: [
        {
          name: TOOL_NAME,
          description: "Retrieve documentation for the MyOrgAPI.",
          inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false,
          },
        },
      ],
    });
    return;
  }

  if (method === "tools/call") {
    if (params?.name !== TOOL_NAME) {
      respondError(id, -32601, `Unknown tool: ${params?.name ?? "<missing>"}`);
      return;
    }

    const document = PROFILE_TO_DOCUMENT[PROFILE];
    if (!document) {
      respondError(
        id,
        -32000,
        `Unsupported CONTEXT_SPRAW_PROFILE: ${PROFILE}. Only baseline signal-only docs are implemented.`,
      );
      return;
    }

    respond(id, {
      content: [{ type: "text", text: document }],
    });
    return;
  }

  if (id !== undefined) {
    respondError(id, -32601, `Method not found: ${method}`);
  }
}

let buffer = "";
stdin.setEncoding("utf8");
stdin.on("data", (chunk) => {
  buffer += chunk;

  let newlineIndex = buffer.indexOf("\n");
  while (newlineIndex >= 0) {
    const line = buffer.slice(0, newlineIndex).trim();
    buffer = buffer.slice(newlineIndex + 1);

    if (line) {
      try {
        handleRequest(JSON.parse(line));
      } catch {
        respondError(null, -32700, "Parse error");
      }
    }

    newlineIndex = buffer.indexOf("\n");
  }
});
