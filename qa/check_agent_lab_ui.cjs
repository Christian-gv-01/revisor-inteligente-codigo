"use strict";

// Regression smoke test for the inline JavaScript of Agent Mission Control.
// Uses only Node built-ins. Does not require Gemini, ChromaDB or a browser.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const htmlPath = path.join(__dirname, "..", "backend", "app", "static", "agent_lab.html");
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)];
assert.equal(scripts.length, 1, "Agent Lab must contain exactly one inline script");
const script = scripts[0][1];

// Critical: fail CI on any SyntaxError, even if all Python tests pass.
const compiled = new vm.Script(script, { filename: "agent_lab_inline.js" });

class Element {
  constructor(id = "") {
    this.id = id;
    this.textContent = "";
    this.value = "";
    this.dataset = {};
    this.children = [];
    this.listeners = {};
    this.disabled = false;
    this.classList = {
      add: () => {},
      remove: () => {},
      toggle: () => {},
    };
  }
  addEventListener(event, listener) { this.listeners[event] = listener; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = [...children]; }
}

const nodes = new Map();
const getElementById = (id) => {
  if (!nodes.has(id)) nodes.set(id, new Element(id));
  return nodes.get(id);
};
const examples = ["eval", "sql", "clean"].map((example) => {
  const node = new Element();
  node.dataset.example = example;
  return node;
});
const calls = [];
const document = {
  getElementById,
  createElement: (tag) => new Element(tag),
  querySelectorAll: (selector) => {
    assert.equal(selector, "[data-example]");
    return examples;
  },
};

const context = vm.createContext({
  document,
  navigator: { clipboard: { writeText: async () => {} } },
  performance: { now: () => 1000 },
  AbortController,
  URL,
  alert: (message) => { throw new Error("Unexpected alert: " + message); },
  fetch: async (url, options) => {
    calls.push({ url, options });
    return {
      ok: true,
      json: async () => ({
        archivo: JSON.parse(options.body).archivo,
        modo: "inspeccion_local",
        pasos: [],
        informe: { archivo: "demo_eval.py", estado: "abstenido", hallazgos: [], fuentes: [] },
      }),
    };
  },
});

async function main() {
  getElementById("mode").value = "local";
  getElementById("steps").value = "3";
  compiled.runInContext(context);

  // The sample buttons must actually load code and update the counter.
  assert.match(getElementById("code").value, /eval\(/);
  assert.equal(getElementById("filename").value, "demo_eval.py");
  assert.match(getElementById("counter").textContent, /[1-9][0-9]* caracteres/);

  examples[1].listeners.click();
  assert.match(getElementById("code").value, /sqlite3/);
  assert.equal(getElementById("filename").value, "demo_sql.py");

  examples[2].listeners.click();
  assert.match(getElementById("code").value, /calcular_area/);

  examples[0].listeners.click();
  assert.match(getElementById("code").value, /eval\(/);

  // Iniciar misión must register a click handler and send valid JSON.
  assert.equal(typeof getElementById("run").listeners.click, "function");
  await getElementById("run").listeners.click();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "/api/v1/agente/previsualizar");
  assert.equal(JSON.parse(calls[0].options.body).max_pasos, 3);
  assert.match(JSON.parse(calls[0].options.body).codigo, /eval\(/);

  // Trace rendering must not throw when Gemini planned steps then failed.
  context.render({
    archivo: "demo_eval.py",
    modo: "degradado",
    fase_error: "informe",
    analisis_estatico: {
      archivo: "demo_eval.py",
      estado: "completo",
      herramientas: [
        { herramienta: "ruff", estado: "ok", hallazgos: 0 },
        { herramienta: "bandit", estado: "ok", hallazgos: 1 },
      ],
      hallazgos: [{
        herramienta: "bandit", regla: "B307", tipo: "seguridad",
        linea: 3, severidad: "media", descripcion: "Posible eval inseguro",
      }],
    },
    decisiones: [
      { numero: 1, herramienta: "detectar_llamadas_sensibles", estado: "ejecutada", motivo: "Revisar eval" },
    ],
    pasos: [
      {
        numero: 1, herramienta: "inspeccionar_estructura", origen: "automatico",
        motivo: "Primera inspección", resultado: { sintaxis_valida: true },
      },
      {
        numero: 2, herramienta: "detectar_llamadas_sensibles", origen: "gemini",
        motivo: "Revisar eval", resultado: { indicadores: [{ linea: 3, llamada: "eval" }] },
      },
    ],
    informe: {
      archivo: "demo_eval.py", estado: "parcial",
      mensaje: "Informe contextual no disponible", hallazgos: [], fuentes: [],
    },
  }, 0.5);
  const textOf = (root) => [
    root.textContent,
    ...root.children.flatMap(textOf),
  ].filter(Boolean).join(" ");
  const displayed = textOf(getElementById("output"));
  assert.match(displayed, /Decisiones registradas del planificador/);
  assert.match(displayed, /ELEGIDO POR GEMINI/);
  assert.match(displayed, /Informe contextual no disponible/);
  assert.match(displayed, /Ruff \+ Bandit/);
  assert.match(displayed, /B307/);
  assert.match(displayed, /1 observaciones/);

  console.log("Agent Lab: JS sintácticamente válido, ejemplos y botón funcionales, traza renderizada.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
