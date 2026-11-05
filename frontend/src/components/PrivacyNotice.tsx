import { Icon } from "./Icon";

// Aviso aportado en feature/frontend-semana4, integrado sin reemplazar HomePage.
export function PrivacyNotice() {
  return (
    <div className="integration-note privacy-notice" role="note" aria-label="Aviso de privacidad y uso de inteligencia artificial">
      <Icon name="shield" size={20} />
      <div>
        <strong>Privacidad y uso de inteligencia artificial</strong>
        <p>Al utilizar el modo API real, el código que proporciones, los archivos que subas o el código Python recuperado de un repositorio público serán procesados por nuestro backend y enviados a Google Gemini para realizar el análisis. También se enviarán fragmentos documentales relevantes de nuestra base de conocimiento.</p>
        <p>El sistema analiza el código como texto: no lo ejecuta ni lo importa.</p>
        <p><strong>Importante:</strong> no incluyas contraseñas, claves API, tokens, datos personales ni información confidencial en los archivos que envíes.</p>
        <p>El tratamiento de los datos por parte del proveedor de IA está sujeto a las condiciones del servicio utilizado por el proyecto.</p>
      </div>
    </div>
  );
}
