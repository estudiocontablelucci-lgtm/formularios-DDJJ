# Formularios DDJJ — Lucci & Asociados

Cuestionarios HTML autocontenidos que los clientes completan para que el estudio
liquide impuestos en ARCA o haga un trámite. **Relevan datos, no liquidan ni
constituyen nada.**

**Se trabaja acá.** Este repo tiene los HTML, git y el historial. Las specs, los
prompts de diseño y los workflows de n8n viven en `Ecosistema/formularios-dev/`.

| Ruta | Formulario |
|---|---|
| `/` | Landing |
| `/mono/` | Inscripción Monotributo |
| `/bp/` | Bienes Personales (Ley 23.966) |
| `/iigg/` | Ganancias Personas Humanas (Ley 20.628) |
| `/sas/` | Constitución de SAS — societario, no impositivo |

Deploy: GitHub Pages desde `main` → **formularios.estudiolucci.com.ar**.
Push a `main` publica; el build tarda ~50s.

> **Todo lo que entra a este repo queda en internet dos veces**: el repo es público
> *y* Pages sirve el árbol completo, no sólo los HTML. `/CLAUDE.md`, `/README.md` y
> `/scripts/*.py` responden 200 en el dominio — verificado. Nada de credenciales,
> workflows de n8n, datos de clientes ni specs internas acá; esas viven en
> `Ecosistema/formularios-dev/`, que no se publica. Es la razón por la que las dos
> carpetas siguen separadas.

```bash
python -m http.server 8123     # probar en local
gh api repos/estudiocontablelucci-lgtm/formularios-DDJJ/pages/builds/latest --jq .status
```

---

## Design system

Tema claro desde ago 2026, con los tokens de `Pagina web/pagina-web/app/globals.css`
(`.theme-light`) — los mismos del Dashboard Macro. No es estético: el cliente entra
desde estudiolucci.com.ar y antes la tinta cambiaba de temperatura al cruzar el
link. **Si cambia la paleta de la web, cambiar acá también.**

```
/* Banda superior (header + progress) — oscura, como el nav de la web */
--navy: #162032   --navy-text: #EEEEE8   --navy-muted: #b4b4ac
--navy-border: rgba(255,255,255,0.07)

/* Cuerpo claro */
--bg: #F4F2EC        --card: #FBFAF6      --card-hover: #EFEBE3
--surface: #EFECE4   /* inputs */         --text: #16202F
--muted: #5A6472     --border: rgba(22,32,47,0.10)
--border2: rgba(22,32,47,0.16)
--accent: #00C896       /* SOLO fills sobre navy: la barra de progreso */
--accent-text: #007A5E  /* texto, iconos, bordes y foco sobre claro */

/* Propios del formulario: la web no tiene campos y no los define */
--border-input: #7a7e84   --placeholder: #5A6472   --mid: #7a7e84
--danger: #c0392b         --success: #007A5E
--accent-veil: rgba(0,122,94,.07)
```

### Reglas de color que no son negociables

Los tokens propios existen porque copiar la paleta de la web al pie de la letra
rompe los formularios. Ratios calculados, no elegidos a ojo:

- **Foco y teal de texto usan `--accent-text`, nunca `--accent`.** El #00C896
  sobre un input claro da **1.83:1**: el anillo de foco desaparece.
- **El placeholder no usa el `--muted-2` de la web** (#9BA1AC → **2.20:1**).
- **El borde de input va gris sólido.** Ningún alpha de tinta llega a 3:1 sobre
  cream, ni `rgba(22,32,47,0.45)`.
- **Peso mínimo 400.** El 300 se ve lavado en claro y emborronado en oscuro.
- **Nada de texto por debajo de 12px**, menos aún en mayúsculas.
- **`max-width: 62ch` va en el texto suelto, no en las cajas.** La medida de línea
  es correcta para un `.hint` bajo un label, pero dentro de una caja con fondo y
  borde —`.nota`, `.aviso`, `.intro-box`, `.firma-box`— que está al lado de inputs
  que llegan al borde, el corte no se lee como línea corta: se lee como layout
  roto. En esas cajas el ancho lo pone el contenedor.

Al tocar colores, verificar con un cálculo de contraste — no a ojo. Mínimos: 4.5:1
texto, 3:1 bordes y anillos de foco.

### Tipografía

| Rol | Tamaño | Peso |
|---|---|---|
| Título del formulario | 1.6rem | Spectral 600 |
| Título de sección | 1.25rem | Spectral 600 |
| Sub-sección / Conformidad | 1.0625rem | Spectral 600 |
| Marca (header) | 1.35rem | Spectral 600 |
| Labels | 15px | Outfit 400 |
| Hints y notas | 14px | Outfit 400 |

Logo: JPEG base64 embebido, compartido entre los cuatro archivos.

### Formato que se lee como generado por IA — no usar

Lo marcó Agustín en sep 2026 en la web (`pagina-web/CLAUDE.md`, misma sección)
porque le resta credibilidad, y se sacó también de acá: se entra a los
formularios desde la web y son la misma familia visual.

- **Mayúsculas espaciadas** (`uppercase` + `letter-spacing`) en rótulos, badges,
  labels o separadores. Si el rótulo repite el título, se saca; si agrega
  información, va en Outfit, en sentence case, sin tracking y sin línea al
  costado. Las siglas (CUIT, ARCA, IIBB) van en mayúscula porque se escriben así,
  no por CSS. Tamaños: rótulo de sub-sección o de tarjeta (`.sub-title`,
  `.socio-num`, `.jurisdiccion-num`) y separador de bloque, 15px Outfit 500;
  badge 13px; label de firma 14px. Acá solo se cargan Spectral y Outfit: nada
  va en DM Mono.
- **Flechas `→` como viñeta.** La flecha queda en links y botones; una lista
  lleva viñeta común en `--muted`.
- **Aclaraciones con línea al costado o en itálica.** `.nota` es un recuadro con
  borde completo (`--border2`) sobre `--card`, en la letra del cuerpo. Los avisos
  de validación (`.aviso`) llevan el borde completo del color del estado, sin el
  `border-left` grueso.
- **Números decorativos "01, 02, 03".** Las letras de sección (A, B, C…) quedan
  porque el copy las cita ("completá la sección G").
- **Itálica en la palabra de acento de un título.** Sigue en el color de acento,
  derecha.
- **La antítesis "no es X, sino Y"** y sus variantes ("…después, no en el
  medio"): se dice Y. Un "no" que marca un alcance o un criterio ("no van acá",
  "no se declaran") es información, no el patrón. En copy fiscal o normativo se
  puede cambiar el molde, nunca lo que afirma.

---

## Patrones

- **Secciones colapsables**: `<h3 class="section-head"><button aria-expanded aria-controls>`
  — patrón ARIA de disclosure. **No volver a `<div onclick>`**: antes eran `<span>`
  dentro de un div, así que las secciones no existían como encabezados para un
  lector de pantalla y el acordeón no se abría sin mouse. `toggleSection` resuelve
  el cuerpo por `aria-controls` y sincroniza `aria-expanded` con la clase `hidden`.
- **Progressive reveal** (`toggleReveal`/`REVEAL_MAP`): campos hijos visibles sólo
  si la pregunta gatillo lo habilita. Soporta cascada.
- **Slot cards** para bienes repetibles, con textarea de overflow al final.
- **Autoguardado** en localStorage por formulario; `syncAllReveals()` al restaurar.
- **Export XLSX** con estilos vía xlsx-js-style (CDN).
- **Conformidad legal**: checkbox obligatorio (Art. 11 Ley 11.683) + nombre + fecha.
  La fecha es readonly y es la del día: se escribe **después** de restaurar el
  guardado y **después** de `reset()`. En los cuatro la restauración la pisaba con
  la del primer guardado, y "Limpiar" la dejaba en blanco sin forma de corregirla.
- **Envío**: `fetch()` POST al webhook n8n. Hash SHA-256 del payload; la IP la
  captura n8n desde headers de Cloudflare.

## scripts/

Transforman los cuatro formularios a la vez. Todos aceptan `--check` para correr
en seco. Trabajan por selector, no con reemplazos globales: `iigg` tiene un bloque
`.alerta-mono` propio que un search & replace ciego pisaría.

| Script | Qué hace |
|---|---|
| `migrar_tema_claro.py` | Migra la paleta al tema claro |
| `mejorar_titulos.py` | Escala tipográfica y acordeón accesible |
| `arreglar_progreso.py` | Progreso sobre campos aplicables + saca el 62ch de las cajas |

> **Los cuatro formularios no comparten el JS, solo el aspecto.** `mono` y `sas`
> recorren `querySelectorAll` y usan `#progressLabel`; `bp` e `iigg` recorren
> `form.elements` y usan `#progressText`. Y los bloques que se revelan se ocultan
> de dos maneras distintas: `.conditional` sin `.visible` en mono/sas,
> `.reveal-slot` con `display:none` en bp/iigg. Un cambio de comportamiento se
> aplica por su propio ancla en cada archivo — asumir una implementación común es
> lo que hace que un fix "aplicado a los cuatro" toque solo dos.

---

## La barra de progreso mide lo que falta hacer, no cuántos campos hay

Solo cuentan los campos que el cliente tiene que completar. Quedan afuera —**del
numerador y del denominador**— los de un bloque de reveal cerrado y los que el
formulario resuelve solo (`data-autocompletado`: la fecha de firma, la
nacionalidad precargada de `sas`).

Sacar algo de un solo lado vuelve el 100% inalcanzable, que era justo el bug.
Antes de arreglarlo, contando los campos ocultos, un formulario **entero
completo** mostraba:

| | ocultos | marcaba |
|---|---|---|
| `bp` | 94 de 104 | **10 %** |
| `mono` | 18 de 40 | **55 %** |
| `sas` | ~20 de ~70 | **70 %** |

Las secciones **colapsadas del acordeón sí cuentan**: esos campos aplican, solo
están plegados. La distinción es "no aplica" contra "no está a la vista".

> Se descubrió al notar que `sas` arrancaba en 7% recién abierto. El 7% era la
> punta: cinco campos autocompletados. Lo caro estaba del otro lado de la
> fracción, y llevaba meses en producción en los otros tres.

---

## `/sas/` — lo que no tienen los otros tres

Es el único que valida **entre** campos, y por eso su JS no se parece al de los
demás. Bloquea el envío sólo lo que no se puede arreglar leyendo la planilla
después — quiénes son los socios, cómo se reparten el capital y quién administra:

- **Cada tarjeta de socio tiene nombre.** El formulario arranca con dos; en una
  SAS unipersonal la segunda quedaba vacía y viajaba como un socio 2 con
  nacionalidad y nada más (`socios_cantidad: 2`), elegible incluso como suplente.
- **Las participaciones suman 100, y cada una está entre 0 (excluido) y 100.** La
  suma sola no alcanza: 110 y −10 suman 100, y 100 y 0 también. El panel de reparto
  muestra cuánto falta o sobra y, con el capital cargado, cuántos pesos le tocan a
  cada socio.
- **El suplente no puede ser titular.** La designación de suplente es obligatoria,
  así que con un único titular el suplente tiene que ser otra persona.

Y una que **avisa pero no bloquea**:

- **El capital contra el mínimo legal**, que es `CAPITAL_MINIMO` — un solo objeto
  con `monto`, `referencia` y `vigencia`. Son 2 SMVM y **se mueve varias veces al
  año**: el formulario muestra la fecha desde la que rige en vez de afirmar el
  número a secas, y avisa que se confirme si pasaron meses. Al actualizarlo, tocar
  sólo esa constante — está en el XLSX exportado también, para que el expediente
  registre contra qué piso se decidió.

Los administradores se derivan de los socios cargados: los checkboxes de titular y
el select de suplente se repueblan al escribir un nombre. El estado se guarda por
**índice** (`admin_titular_socio_N`), no por nombre, para que sobreviva a que el
socio siga tipeando. La contracara: al eliminar un socio los índices se corren, y
`eliminarSocio` tiene que mover cada designación con su socio. Antes no lo hacía, y
eliminar al titular dejaba titular al socio siguiente — una designación que nadie
hizo, sin aviso y con el envío habilitado.

El capital admite centavos: una coma **al final** con hasta dos dígitos es decimal
(`1.000.000,50`); cualquier otra coma o punto es separador de miles, así que
`1,000,000` tipeado a la norteamericana sigue siendo un millón. Antes la coma se
descartaba y los centavos se pegaban al entero: cien veces el capital.

Los socios son tarjetas dinámicas hasta **5** (`MAX_SOCIOS`), que es el tope de
columnas de la Sheet. Al eliminar uno la lista se **renumera**: se lee el DOM por
`data-campo`, se reconstruye y nunca quedan huecos tipo `socio_1` + `socio_3`.
Subir el tope sin correr `sync-headers.py` hace que el socio 6 se descarte en
silencio.

> La conformidad de este formulario **no cita el Art. 11 de la Ley 11.683**, como
> sí hacen los otros tres. Esa norma es de declaraciones juradas impositivas y acá
> no aplica: el texto declara veracidad de los datos y su transcripción al
> instrumento constitutivo. Copiar la conformidad de otro formulario lo rompe.

---

## Zonas protegidas

- **Los formularios no calculan impuestos.** Sólo relevan datos.
- **Valores normativos** (escalas Art. 94, deducciones Art. 30, topes Art. 85) no
  van acá: van en las planillas de liquidación del estudio.
- **Sin notas técnicas para el cliente**: criterios de valuación y artículos de
  ley los maneja el estudio.
- Si se agregan o quitan campos, la Sheet necesita una columna con ese mismo
  `name`. El nodo de n8n mapea **por nombre de header** (`autoMapInputData`), así
  que un campo sin columna no rompe nada: llega al webhook y se descarta **en
  silencio**. El envío no se corre — se pierde ese dato y nada avisa.
  En `formularios-dev/n8n/`: `sync-headers.py <form>` inserta en la Sheet lo que
  falte del TSV (dry run por defecto, `--apply` para escribir; sólo inserta, nunca
  borra ni reordena, y no toca los envíos ya cargados), y después
  `create-ficha.py <form>` regenera la Ficha.
