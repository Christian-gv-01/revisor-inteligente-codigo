import { createRoot } from "react-dom/client";
import { Preview } from "./SourcesPreview";
import "../src/styles/global.css";

createRoot(document.getElementById("root")!).render(<Preview />);
