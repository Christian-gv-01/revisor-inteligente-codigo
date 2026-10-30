import { useEffect, useRef, useState } from "react";
import { CodeEditor } from "../components/CodeEditor";
import { CodeInput } from "../components/CodeInput";
import { FindingsPanel } from "../components/FindingsPanel";
import { Icon } from "../components/Icon";
import {
  analyzeCode,
  AnalysisError,
  validateFile,
  validateInput,
} from "../services/api";
import { analyzeDemo, EXAMPLE_CODE } from "../services/demo";
import type {
  AnalysisInput,
  AnalysisResult,
  Finding,
  InputKind,
  Mode,
  Scenario,
} from "../types/analysis";
import { SEVERITIES, SEVERITY_LABELS } from "../types/analysis";
const initial: AnalysisInput = {
  tipo: "codigo",
  archivo: "ejemplo.py",
  codigo: EXAMPLE_CODE,
  url: "",
  fichero: null,
};
export function HomePage() {
  const [input, setInput] = useState<AnalysisInput>(initial);
  const [mode, setMode] = useState<Mode>("demo");
  const [scenario, setScenario] = useState<Scenario>("hallazgos");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selected, setSelected] = useState<Finding | null>(null);
  const [activeFile, setActiveFile] = useState("");
  const [status, setStatus] = useState<
    "idle" | "reading" | "loading" | "done" | "cancelled"
  >("idle");
  const [error, setError] = useState<AnalysisError | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const request = useRef<AbortController | null>(null);
  const busy = status === "loading" || status === "reading";
  const project = input.tipo === "zip" || input.tipo === "github";
  const currentFile =
    result?.archivos.find((f) => f.nombre === activeFile) ??
    result?.archivos[0];
  const filename = currentFile?.nombre ?? input.archivo;
  const code = currentFile ? currentFile.codigo : project ? null : input.codigo;
  const markers = result?.hallazgos ?? [];
  useEffect(() => () => request.current?.abort(), []);
  function clearResult() {
    setResult(null);
    setSelected(null);
    setActiveFile("");
    setError(null);
    setStatus("idle");
  }
  function update(partial: Partial<AnalysisInput>) {
    clearResult();
    setInput((previous) => ({ ...previous, ...partial }));
  }
  function changeKind(tipo: InputKind) {
    update({
      tipo,
      fichero: null,
      archivo: "ejemplo.py",
      codigo: tipo === "codigo" ? input.codigo : "",
    });
  }
  async function chooseFile(file: File) {
    if (busy) return;
    clearResult();
    setInput((previous) => ({
      ...previous,
      fichero: null,
      codigo: "",
      archivo: "ejemplo.py",
    }));
    setStatus("reading");
    try {
      const kind = input.tipo === "python" ? "python" : "zip";
      validateFile(file, kind);
      let text = "";
      if (kind === "python") {
        try {
          text = new TextDecoder("utf-8", { fatal: true }).decode(
            await file.arrayBuffer(),
          );
        } catch {
          throw new AnalysisError(
            "entrada",
            "No se pudo leer el archivo como texto UTF-8.",
          );
        }
      } else {
        const signature = new Uint8Array(await file.slice(0, 4).arrayBuffer());
        if (
          signature[0] !== 80 ||
          signature[1] !== 75 ||
          !(
            (signature[2] === 3 && signature[3] === 4) ||
            (signature[2] === 5 && signature[3] === 6) ||
            (signature[2] === 7 && signature[3] === 8)
          )
        )
          throw new AnalysisError(
            "entrada",
            "El archivo no tiene una cabecera ZIP válida.",
          );
      }
      const next = {
        ...input,
        fichero: file,
        archivo: file.name,
        codigo: text,
      };
      validateInput(next);
      setInput(next);
    } catch (err) {
      setError(
        err instanceof AnalysisError
          ? err
          : new AnalysisError(
              "entrada",
              "No se pudo leer el archivo seleccionado.",
            ),
      );
    } finally {
      setStatus("idle");
    }
  }
  async function analyze() {
    if (busy) return;
    clearResult();
    const controller = new AbortController();
    request.current = controller;
    const start = performance.now();
    try {
      validateInput(input);
      setStatus("loading");
      const response =
        mode === "demo"
          ? await analyzeDemo(input, scenario, controller.signal)
          : await analyzeCode(input, controller.signal);
      if (controller.signal.aborted) return;
      setResult(response);
      setActiveFile(response.archivos[0]?.nombre ?? "");
      setElapsed((performance.now() - start) / 1000);
      setStatus("done");
    } catch (err) {
      if (controller.signal.aborted) return;
      setError(
        err instanceof AnalysisError
          ? err
          : new AnalysisError(
              "servidor",
              "Ocurrió un error inesperado. Inténtalo de nuevo.",
            ),
      );
      setStatus("idle");
    }
  }
  function exportReport() {
    if (!result) return;
    const report = {
  modo: result.demo ? "demostracion_sin_ia" : "backend",
  fecha: new Date().toISOString(),
  archivos: result.archivos.map((f) => f.nombre),
  fuentes: result.fuentes ?? [],
  hallazgos: result.hallazgos,
};
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }),
    );
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = result.demo
      ? "informe-demostracion.json"
      : "informe-seguridad.json";
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return (
    <div className="app-shell">
      <a className="skip-link" href="#workspace">
        Ir al analizador
      </a>
      <aside className="sidebar">
        <a href="#" className="brand" aria-label="Inicio del revisor">
          <span className="brand-icon">
            <Icon name="shield" size={25} />
          </span>
          <span>
            CODE<span className="brand-accent">GUARD</span>
            <small>REVISOR DE CÓDIGO SEGURO</small>
          </span>
        </a>
        <div className="nav-caption">ESPACIO DE TRABAJO</div>
        <a className="nav-item active" href="#workspace">
          <Icon name="code" />
          Analizador de código
          <span className="nav-dot" />
        </a>
        <a className="nav-item" href="#guide">
          <Icon name="info" />
          Guía de uso
        </a>
        <div className="sidebar-project">
          <span className="project-symbol">U</span>
          <div>
            <strong>Proyecto de grado</strong>
            <small>UNIANDES · Caso 10</small>
          </div>
        </div>
        <div className="sidebar-bottom">
          <span className="small-dot" />
          Entorno de desarrollo<small>Python · Análisis de seguridad</small>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            Espacio de trabajo <span>/</span> <strong>Analizador</strong>
          </div>
          <span className={`mode-pill ${mode}`}>
            <span className="small-dot" />
            {mode === "demo" ? "Modo demostración" : "Modo API"}
          </span>
        </header>
        <main id="workspace">
          <div className="page-heading">
            <div>
              <div className="eyebrow">SEGURIDAD DESDE LA PRIMERA LÍNEA</div>
              <h1>
                Revisor Inteligente
                <br className="mobile-break" /> de Código Seguro<span>.</span>
              </h1>
              <p>
                Explora los riesgos de tu código Python y encuentra cómo
                corregirlos.
              </p>
            </div>
            <span className="python-tag">
              <Icon name="code" size={17} /> Python
            </span>
          </div>
          <section
            className="mode-banner"
            aria-label="Configuración de análisis"
          >
            <Icon name={mode === "demo" ? "info" : "shield"} size={22} />
            <div>
              <strong>
                {mode === "demo"
                  ? "Prueba el flujo, conoce los hallazgos."
                  : "Conecta tu código con el backend."}
              </strong>
              <p>
                {mode === "demo"
                  ? "Simulación local sin IA: reconoce tres patrones de ejemplo. No es una revisión de seguridad real."
                  : "El análisis se envía a la API del proyecto. El frontend no ejecuta tu código."}
              </p>
            </div>
            <div
              className="mode-switch"
              role="group"
              aria-label="Modo de análisis"
            >
              <button
                disabled={busy}
                aria-pressed={mode === "demo"}
                onClick={() => {
                  clearResult();
                  setMode("demo");
                }}
              >
                Demo
              </button>
              <button
                disabled={busy}
                aria-pressed={mode === "api"}
                onClick={() => {
                  clearResult();
                  setMode("api");
                }}
              >
                API real
              </button>
            </div>
          </section>
          <div className="stats-grid">
            {SEVERITIES.map((severity) => (
              <div className={`stat-card stat-${severity}`} key={severity}>
                <div>
                  <span className="severity-dot" />
                  {SEVERITY_LABELS[severity]}
                </div>
                <strong>
                  {result
                    ? result.hallazgos
                        .filter((f) => f.severidad === severity)
                        .length.toString()
                        .padStart(2, "0")
                    : "—"}
                </strong>
                <span>hallazgos</span>
              </div>
            ))}
          </div>
          <div className="workspace-grid">
            <section
              className="panel source-panel"
              aria-labelledby="source-title"
            >
              <div className="panel-heading">
                <div>
                  <span className="step-number">01</span>
                  <h2 id="source-title">Código fuente</h2>
                </div>
                <button
                  className="text-button"
                  disabled={busy}
                  onClick={() => {
                    clearResult();
                    setInput(initial);
                  }}
                >
                  Cargar ejemplo
                </button>
              </div>
              <CodeInput
                input={input}
                disabled={busy}
                onKind={changeKind}
                onName={(archivo) => update({ archivo })}
                onUrl={(url) => update({ url })}
                onFile={(file) => void chooseFile(file)}
              />
              {project && (
                <div className="integration-note">
                  <Icon name="info" size={16} />
                  <span>
                    {mode === "demo"
                      ? "En demo se muestran archivos ficticios. El ZIP o repositorio seleccionado no se analiza."
                      : input.tipo === "github"
                        ? "El backend disponible aún no tiene una ruta para descargar repositorios."
                        : "El backend analiza hasta 5 archivos Python y 12.000 caracteres en total. Devuelve hallazgos por archivo; la vista del código espera contenido del backend."}
                  </span>
                </div>
              )}
              <div className="editor-shell">
                <div className="editor-toolbar">
                  <span>
                    <Icon name="file" size={15} />
                    {project && !currentFile
                      ? "Vista previa del proyecto"
                      : filename}
                  </span>
                  <span className="editor-language">PYTHON</span>
                </div>
                {result && result.archivos.length > 1 && (
                  <label className="file-selector">
                    Archivo
                    <select
                      value={activeFile}
                      onChange={(e) => {
                        setActiveFile(e.target.value);
                        setSelected(null);
                      }}
                    >
                      {result.archivos.map((file) => (
                        <option key={file.nombre} value={file.nombre}>
                          {file.nombre}
                        </option>
                      ))}
                    </select>
                  </label>
                )}
                {code === null ? (
                  <div className="project-placeholder">
                    <Icon name="folder" size={36} />
                    <strong>
                      {currentFile
                        ? "Código fuente no incluido"
                        : "Un proyecto, una vista clara"}
                    </strong>
                    <p>
                      {currentFile
                        ? "El backend devolvió el informe de este archivo, pero no su contenido. Puedes consultar los hallazgos y sus números de línea en el panel de resultados."
                        : "Los archivos aparecerán aquí cuando estén disponibles."}
                    </p>
                  </div>
                ) : (
                  <CodeEditor
                    code={code}
                    filename={filename}
                    findings={markers}
                    selected={selected}
                    readOnly={busy || project}
                    onChange={(codigo) => update({ codigo })}
                  />
                )}
                <div className="editor-footer">
                  <span>
                    {code === null
                      ? "Sin vista previa de código"
                      : `${code.split("\n").length} líneas · ${Array.from(code).length.toLocaleString("es")} caracteres`}
                  </span>
                  <span>UTF-8</span>
                </div>
              </div>
              {mode === "demo" && (
                <div className="demo-controls">
                  <label htmlFor="scenario">Escenario de demostración</label>
                  <select
                    id="scenario"
                    disabled={busy}
                    value={scenario}
                    onChange={(e) => {
                      clearResult();
                      setScenario(e.target.value as Scenario);
                    }}
                  >
                    <option value="hallazgos">
                      Detectar patrones de ejemplo
                    </option>
                    <option value="vacio">Sin hallazgos (simulado)</option>
                    <option value="servidor">
                      Error del servidor (simulado)
                    </option>
                    <option value="conexion">
                      Error de conexión (simulado)
                    </option>
                  </select>
                </div>
              )}
              {error && (
                <div className="error-notice" role="alert">
                  <Icon name="alert" />
                  <div>
                    <strong>
                      {
                        {
                          entrada: "Revisa tu entrada",
                          servidor: "Error del servidor",
                          conexion: "Error de conexión",
                          contrato: "Respuesta no válida",
                          pendiente: "Integración pendiente",
                        }[error.kind]
                      }
                    </strong>
                    <p>{error.message}</p>
                  </div>
                </div>
              )}
              <div className="analyze-actions">
                <span
                  className="analysis-status"
                  role="status"
                  aria-live="polite"
                >
                  {status === "loading" ? (
                    <>
                      <span className="spinner" />
                      Analizando…
                    </>
                  ) : status === "reading" ? (
                    "Leyendo archivo…"
                  ) : status === "done" ? (
                    <>
                      <Icon name="check" size={16} />
                      Completado en {elapsed.toFixed(1)} s
                    </>
                  ) : status === "cancelled" ? (
                    "Análisis cancelado"
                  ) : (
                    <>
                      <Icon name="shield" size={16} />
                      {mode === "demo"
                        ? "Sin conexión a IA"
                        : "Listo para analizar"}
                    </>
                  )}
                </span>
                {status === "loading" ? (
                  <button
                    className="secondary-button"
                    onClick={() => {
                      request.current?.abort();
                      setStatus("cancelled");
                    }}
                  >
                    Cancelar
                  </button>
                ) : (
                  <button
                    className="primary-button"
                    disabled={
                      busy || (mode === "api" && input.tipo === "github")
                    }
                    onClick={() => void analyze()}
                  >
                    {mode === "demo" ? "Probar análisis" : "Analizar código"}
                    <Icon name="arrow" size={18} />
                  </button>
                )}
              </div>
            </section>
            <FindingsPanel
              key={result ? "result" : "empty"}
              result={result}
              loading={status === "loading"}
              selectedId={selected?.id}
              onSelect={(finding) => {
                setActiveFile(finding.archivo);
                setSelected({ ...finding });
              }}
            />
          </div>
          {result && (
            <div className="report-row">
              <p>
                <Icon name="check" size={16} />
                {result.demo
                  ? "Informe de demostración"
                  : "Informe del backend"}{" "}
                · {result.archivos.length} archivo(s) ·{" "}
                {result.hallazgos.length} hallazgo(s)
              </p>
              <button className="secondary-button" onClick={exportReport}>
                <Icon name="download" size={16} />
                Descargar informe JSON
              </button>
            </div>
          )}
          <section id="guide" className="guide">
            <div>
              <span className="eyebrow">UNA REVISIÓN, TRES PASOS</span>
              <h2>Del código a la corrección.</h2>
            </div>
            <div>
              <span>01</span>
              <strong>Introduce tu código</strong>
              <p>Pega Python o selecciona un archivo para empezar.</p>
            </div>
            <div>
              <span>02</span>
              <strong>Explora los hallazgos</strong>
              <p>Filtra por severidad y localiza cada línea señalada.</p>
            </div>
            <div>
              <span>03</span>
              <strong>Revisa la sugerencia</strong>
              <p>Evalúa la corrección en el contexto de tu aplicación.</p>
            </div>
          </section>
          <footer className="footer">
            <span>
              UNIANDES <b>·</b> Proyecto de grado — Caso 10
            </span>
            <span>Revisión asistida. Criterio humano.</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
