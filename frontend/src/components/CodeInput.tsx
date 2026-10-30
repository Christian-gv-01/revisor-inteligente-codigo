import type { AnalysisInput, InputKind } from "../types/analysis";
import { Icon } from "./Icon";
const choices = [
  { id: "codigo", label: "Pegar código", icon: "code" },
  { id: "python", label: "Archivo .py", icon: "file" },
  { id: "zip", label: "Proyecto .zip", icon: "folder" },
  { id: "github", label: "GitHub", icon: "github" },
] as const;
interface Props {
  input: AnalysisInput;
  disabled: boolean;
  onKind: (kind: InputKind) => void;
  onName: (name: string) => void;
  onUrl: (url: string) => void;
  onFile: (file: File) => void;
}
export function CodeInput({
  input,
  disabled,
  onKind,
  onName,
  onUrl,
  onFile,
}: Props) {
  return (
    <>
      <div className="input-tabs" role="group" aria-label="Tipo de entrada">
        {choices.map((choice) => (
          <button
            key={choice.id}
            type="button"
            disabled={disabled}
            aria-pressed={input.tipo === choice.id}
            className={input.tipo === choice.id ? "active" : ""}
            onClick={() => onKind(choice.id)}
          >
            <Icon name={choice.icon} size={17} />
            {choice.label}
          </button>
        ))}
      </div>
      <div className="input-details">
        {input.tipo === "codigo" && (
          <label className="filename-label">
            Nombre del archivo
            <input
              aria-label="Nombre del archivo"
              value={input.archivo}
              maxLength={255}
              disabled={disabled}
              onChange={(e) => onName(e.target.value)}
              spellCheck={false}
            />
          </label>
        )}
        {(input.tipo === "python" || input.tipo === "zip") && (
          <label
            className={`dropzone ${disabled ? "disabled" : ""}`}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              if (!disabled && event.dataTransfer.files[0])
                onFile(event.dataTransfer.files[0]);
            }}
          >
            <Icon name="upload" size={24} />
            <span>
              <strong>
                {input.fichero?.name || "Selecciona o arrastra un archivo"}
              </strong>
              <small>
                {input.tipo === "python"
                  ? "Python · hasta 48 KB y 12.000 caracteres"
                  : "ZIP · hasta 5 MB y 5 archivos Python"}
              </small>
            </span>
            <input
              aria-label={
                input.tipo === "python"
                  ? "Seleccionar archivo Python"
                  : "Seleccionar archivo ZIP"
              }
              type="file"
              accept={input.tipo === "python" ? ".py" : ".zip"}
              disabled={disabled}
              onChange={(e) => {
                if (e.target.files?.[0]) onFile(e.target.files[0]);
                e.target.value = "";
              }}
            />
          </label>
        )}
        {input.tipo === "github" && (
          <label className="url-label">
            Repositorio público de GitHub
            <input
              type="url"
              placeholder="https://github.com/usuario/repositorio"
              value={input.url}
              disabled={disabled}
              onChange={(e) => onUrl(e.target.value)}
              spellCheck={false}
            />
            <small>La descarga del repositorio corresponde al backend.</small>
          </label>
        )}
      </div>
    </>
  );
}
