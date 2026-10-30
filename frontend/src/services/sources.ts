export function safeSourceUrl(value: string): string | null {
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) &&
      !url.username && !url.password ? url.href : null;
  } catch {
    return null;
  }
}
import type { AnalysisResult, Finding, SourceReference } from "../types/analysis";

export function getFindingSources(result: AnalysisResult, finding: Finding): SourceReference[] {
  return finding.fuentes ?? (result.fuentes ?? []).filter((source) => finding.referencias?.includes(source.id));
}
