import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

root = Path(__file__).resolve().parents[4]
BASE = '65675e27fd996a7e71a926336dba6dffb5e539e2'
def git(*args):
    return subprocess.check_output(['git', *args], cwd=root).decode('utf-8').splitlines()

paths = sorted(set(git('diff', BASE, '--name-only') + git('ls-files', '--others', '--exclude-standard')))
markdown = [root / p for p in paths if p.endswith('.md')]
errors = []
link_count = 0
for file in markdown:
    content = file.read_text(encoding='utf-8-sig')
    if '\ufffd' in content:
        errors.append(f'UTF8 replacement: {file.relative_to(root)}')
    if content.count('```') % 2:
        errors.append(f'Unclosed code fence: {file.relative_to(root)}')
    content = re.sub(r'```.*?```', '', content, flags=re.S)
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', content):
        if re.match(r'^[a-zA-Z][\w+.-]*:', target) or target.startswith('#'):
            continue
        local = unquote(target.split('#')[0].split('?')[0].strip('<>'))
        link_count += 1
        if not (file.parent / local).exists():
            errors.append(f'Broken link: {file.relative_to(root)} -> {target}')

manifest = json.loads((root / 'data/raw/fuentes.json').read_text(encoding='utf-8-sig'))
for item in manifest['fuentes']:
    file = root / 'data/raw' / item['archivo']
    raw = file.read_bytes()
    if hashlib.sha256(raw).hexdigest() != item['sha256'] or len(raw) != item['bytes']:
        errors.append('Source hash/size mismatch: ' + item['id'])
    if item['http_status'] != 200 or b'<html' not in raw.lower():
        errors.append('Invalid downloaded source: ' + item['id'])

requirements = (root / 'docs/02-requisitos.md').read_text(encoding='utf-8')
stories = set(re.findall(r'\| (HU-\d+)\.', requirements))
questions = set(re.findall(r'\| (L\d+) \|', (root / 'docs/levantamiento.md').read_text(encoding='utf-8')))
if len(stories) < 8 or len(questions) < 15:
    errors.append('Insufficient stories/questions')

archives = {}
for current, historical in [('03-arquitectura.md', '03-arquitectura-revision2.md'), ('09-decisiones.md', '09-decisiones-revision2.md')]:
    original = subprocess.check_output(['git','show',f'{BASE}:docs/{current}'], cwd=root).decode('utf-8').replace('\r\n','\n')
    preserved = (root / 'docs/historico' / historical).read_text(encoding='utf-8-sig')
    archives[historical] = original == preserved
    if original != preserved:
        errors.append('Historical content changed: ' + historical)

report = {
    'fecha_utc': datetime.now(timezone.utc).isoformat(),
    'base_git': BASE,
    'alcance': 'Validacion documental local: enlaces relativos de Markdown editados/nuevos, UTF-8, cercas, historias, preguntas, hashes y copias historicas. Sin pruebas nuevas del producto, Gemini o produccion.',
    'markdown_revisados': len(markdown), 'enlaces_relativos_comprobados': link_count,
    'fuentes_html_con_hash_correcto': len(manifest['fuentes']) if not any('Source' in e or 'source' in e for e in errors) else None,
    'historias': len(stories), 'preguntas_instrumento_no_aplicado': len(questions),
    'historicos_conservados': archives,
    'errores': errors, 'resultado': 'aprobado' if not errors else 'fallido',
    'observacion_evidencia': 'La imagen reinicio-railway-20261105.png fue inspeccionada visualmente: muestra el comparador de citas, no logs del reinicio o montaje del volumen. Se corrigieron las descripciones sin modificar la evidencia original.'
}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
