import { useEffect, useRef, useState } from "react";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor/editor/editor.api.js";
import "monaco-editor/languages/definitions/python/register.js";
import EditorWorker from "monaco-editor/editor/editor.worker.js?worker";
import type { Finding } from "../types/analysis";

// Recursos locales: el editor no descarga scripts de una CDN.
self.MonacoEnvironment = { getWorker: () => new EditorWorker() };
loader.config({ monaco });
monaco.editor.defineTheme("codeguard-night", {
  base: "vs-dark",
  inherit: true,
  rules: [
    { token: "keyword", foreground: "C8A6EF" },
    { token: "string", foreground: "F3CF7E" },
    { token: "number", foreground: "82DCCF" },
    { token: "comment", foreground: "8094B5" },
  ],
  colors: {
    "editor.background": "#10192C",
    "editor.foreground": "#E4ECF8",
    "editorLineNumber.foreground": "#8299BA",
    "editorLineNumber.activeForeground": "#F4B65B",
    "editor.lineHighlightBackground": "#17243B",
    "editorCursor.foreground": "#19C8BB",
    "editor.selectionBackground": "#224967",
    "editorIndentGuide.background1": "#25334A",
  },
});
interface Props {
  code: string;
  filename: string;
  findings: Finding[];
  selected: Finding | null;
  readOnly: boolean;
  onChange: (value: string) => void;
}
export function CodeEditor({
  code,
  filename,
  findings,
  selected,
  readOnly,
  onChange,
}: Props) {
  const editor = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const model = editor.current?.getModel();
    if (!ready || !model) return;
    const valid = findings.filter(
      (f) => f.archivo === filename && f.linea <= model.getLineCount(),
    );
    monaco.editor.setModelMarkers(
      model,
      "security",
      valid.map((f) => ({
        startLineNumber: f.linea,
        startColumn: 1,
        endLineNumber: f.linea,
        endColumn: model.getLineMaxColumn(f.linea),
        message: `${f.titulo}\n${f.correccion_sugerida}`,
        severity:
          f.severidad === "critica"
            ? monaco.MarkerSeverity.Error
            : monaco.MarkerSeverity.Warning,
      })),
    );
    const decorations = editor.current!.createDecorationsCollection(
      valid.map((f) => ({
        range: new monaco.Range(f.linea, 1, f.linea, 1),
        options: {
          isWholeLine: true,
          className: `code-line-${f.severidad}`,
          glyphMarginClassName: `code-glyph-${f.severidad}`,
        },
      })),
    );
    return () => {
      decorations.clear();
      if (!model.isDisposed())
        monaco.editor.setModelMarkers(model, "security", []);
    };
  }, [ready, filename, findings, code]);
  useEffect(() => {
    const instance = editor.current;
    if (!ready || !instance || !selected || selected.archivo !== filename)
      return;
    if (selected.linea > (instance.getModel()?.getLineCount() ?? 0)) return;
    instance.revealLineInCenter(selected.linea);
    instance.setPosition({ lineNumber: selected.linea, column: 1 });
    instance.focus();
  }, [selected, filename, ready]);
  return (
    <Editor
      height="380px"
      language="python"
      theme="codeguard-night"
      value={code}
      loading={
        <div className="editor-loading">Preparando editor de Python…</div>
      }
      onMount={(instance) => {
        editor.current = instance;
        setReady(true);
      }}
      onChange={(value) => {
        if (!readOnly && value !== code) onChange(value ?? "");
      }}
      options={{
        readOnly,
        minimap: { enabled: false },
        fontSize: 14,
        lineHeight: 25,
        fontFamily: "Consolas, monospace",
        padding: { top: 20, bottom: 20 },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        lineNumbers: "on",
        glyphMargin: true,
        renderLineHighlight: "line",
        wordWrap: "on",
        tabSize: 4,
        ariaLabel: `Código Python: ${filename}`,
        accessibilitySupport: "on",
        quickSuggestions: false,
        stickyScroll: { enabled: false },
        tabFocusMode: true,
      }}
    />
  );
}
