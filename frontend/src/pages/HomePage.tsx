import { useEffect, useRef, useState } from "react";
import { CodeEditor } from "../components/CodeEditor";
import { CodeInput } from "../components/CodeInput";
import { FindingsPanel } from "../components/FindingsPanel";
import { Icon } from "../components/Icon";
import { EvidenceTrace } from "../components/EvidenceTrace";
import {
  analyzeCode,
  AnalysisError,
  validateFile,
  validateInput,
} from "../services/api";
import { analyzeDemo, SQL_EXAMPLE_CODE } from "../services/demo";
import { createReport } from "../services/report";
import type {
  AnalysisInput,
  AnalysisResult,
  Finding,
  InputKind,
  Mode,
  Scenario,
} from "../types/analysis";
const initial: AnalysisInput = {
  tipo: "codigo",
  archivo: "usuarios.py",
  codigo: SQL_EXAMPLE_CODE,
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
      setSelected(response.hallazgos[0] ?? null);
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
    const report = createReport(result);
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
      <a className="skip-link" href="#workspace">Ir al analizador</a>
      <header className="project-header">
        <a className="project-brand" href="#workspace" aria-label="Inicio del revisor">
          <span className="project-mark"><Icon name="shieldCode" size={40} /></span>
          <div><h1>Revisor Inteligente de Código Seguro</h1><span className="project-subtitle">Python · Análisis asistido por IA</span></div>
        </a>
        <div className="academic-brand"><strong>UNIANDES</strong><span>Proyecto de titulación</span></div>
      </header>
      <div className="workflow-bar">
        <nav className="workflow" aria-label="Etapas de la revisión">
          <a href="#source-panel" aria-current={!result ? "step" : undefined}><span>01</span> Código fuente</a>
          <Icon name="chevron" size={16} />
          <a href="#results-title" aria-current={result ? "step" : undefined}><span>02</span> Revisión de hallazgos</a>
          <Icon name="chevron" size={16} />
          <a href="#evidence-title"><span>03</span> Evidencia documental</a>
        </nav>
        <span className={`mode-pill ${mode}`}><span className="small-dot" />{mode === "demo" ? "Modo demostración" : "Modo API"}</span>
      </div>
      <main id="workspace">
        <section className={`mode-banner ${mode}`} aria-label="Configuración de análisis">
          <Icon name="info" size={17} />
          <p>{mode === "demo" ? "Datos de ejemplo · Simulación local sin IA. Las referencias son ilustrativas." : "Análisis mediante el backend del proyecto. El código se analiza sin ejecutarlo."}</p>
          <div className="mode-switch" role="group" aria-label="Modo de análisis">
            <button disabled={busy} aria-pressed={mode === "demo"} onClick={() => { clearResult(); setMode("demo"); }}>Demo</button>
            <button disabled={busy} aria-pressed={mode === "api"} onClick={() => { clearResult(); setMode("api"); }}>API real</button>
          </div>
        </section>
        <div className="workspace-grid">
          <section id="source-panel" className="panel source-panel" aria-labelledby="source-title">
            <div className="panel-heading">
              <div><Icon name="file" size={22} /><h2 id="source-title">Código Python</h2></div>
              <button className="text-button" disabled={busy} onClick={() => { clearResult(); setInput(initial); }}><Icon name="folder" size={18} />Cargar ejemplo</button>
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
                        ? "Se analizarán hasta 5 archivos Python de un repositorio público, con un máximo de 12.000 caracteres en total."
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
                        : "El código se analiza sin ejecutarlo."}
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
                    disabled={busy}
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
            onExport={result ? exportReport : undefined}
            onSelect={(finding) => { setActiveFile(finding.archivo); setSelected({ ...finding }); }}
          />
        </div>
        <EvidenceTrace result={result} selected={selected} loading={status === "loading"} />
        <details id="guide" className="usage-guide">
          <summary><Icon name="info" size={16} />Cómo revisar tu código</summary>
          <ol><li>Pega código Python o selecciona un archivo.</li><li>Ejecuta el análisis y selecciona un hallazgo para localizar su línea.</li><li>Revisa la corrección y consulta las referencias documentales.</li></ol>
        </details>
        <footer className="footer"><span><strong>Revisión asistida:</strong> valida las sugerencias en el contexto de tu proyecto.</span><span>{mode === "demo" ? "Demostración · Sin conexión a IA" : "UNIANDES · Proyecto de titulación"}</span></footer>
      </main>
    </div>
  );
}
