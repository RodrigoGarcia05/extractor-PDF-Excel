import fitz  # PyMuPDF #leer texto de pdf
import io  # manejar flujo
import os
import pandas as pd 
import pdfplumber  # leer tablas de pdf
from PIL import Image  # Presentar imagenes
import pytesseract  # OCR #leer texto de imagen

from shiny import App, reactive, render, ui
import tempfile  

pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"


def extraer_texto_directo(page):
  return page.get_text()


def extraer_imagenes_y_ocr(page, doc, contador):
  resultados = []

  for i, img in enumerate(page.get_images(full=True)):
    xref = img[0]
    base_img = doc.extract_image(xref)
    img_bytes = base_img["image"]
    image = Image.open(io.BytesIO(img_bytes))
    texto_ocr = pytesseract.image_to_string(image)
    if texto_ocr.strip():
      resultados.append((contador + i, texto_ocr.strip()))
  return resultados


def extraer_tablas_pdfplumber(path_pdf, pagina_actual):
  tablas_extraidas = []
  with pdfplumber.open(path_pdf) as pdf:
    if pagina_actual < len(pdf.pages):
      page = pdf.pages[pagina_actual]
      tables = page.extract_tables()
      for t in tables:
        tabla_texto = "\n".join([
            "\t".join(cell if cell is not None else "" for cell in fila)
            for fila in t
        ])
        tablas_extraidas.append(tabla_texto)
  return tablas_extraidas


def procesar_pdf_shiny(path_pdf):
  resultados = []
  doc = fitz.open(path_pdf)

  for i, page in enumerate(doc):
    pagina_resultados = {
        "numero": i + 1,
        "tipo": "pdf",
        "texto_directo": "",
        "ocr": [],
        "tablas": [],
    }

    texto = extraer_texto_directo(page)
    if texto.strip():
      pagina_resultados["texto_directo"] = texto.strip()

    resultados_ocr = extraer_imagenes_y_ocr(page, doc, i * 1000)
    for idx, texto_ocr in resultados_ocr:
      pagina_resultados["ocr"].append(f"OCR #{idx}: {texto_ocr}")

    tablas = extraer_tablas_pdfplumber(path_pdf, i)
    for j, tabla in enumerate(tablas):
      pagina_resultados["tablas"].append(f"Tabla #{j+1}:\n{tabla}")

    resultados.append(pagina_resultados)

  doc.close()
  return resultados


def procesar_excel_shiny(path_excel):
  try:
    df_dict = pd.read_excel(path_excel, sheet_name=None)
    resultados = []

    for idx, (nombre_hoja, hoja) in enumerate(df_dict.items()):
      tabla_texto = hoja.to_string(index=False)
      hoja_resultados = {
          "numero": idx + 1,
          "tipo": "excel",
          "nombre_hoja": nombre_hoja,
          "texto_directo": "",
          "ocr": [],
          "tablas": [tabla_texto],
      }
      resultados.append(hoja_resultados)

    return resultados
  except Exception as e:
    return [{
        "numero": 1,
        "tipo": "excel",
        "nombre_hoja": "Error",
        "texto_directo": f"Error al leer el archivo Excel: {e}",
        "ocr": [],
        "tablas": [],
    }]


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.tags.style("""
            .area-subida {
                border: 2px solid #fdfdfd; 
                border-radius: 8px;
                padding: 20px;
                background-color: #f8f9fa;
                text-align: center;
                margin: 15px 0;
            }
            .area-subida:hover {
                background-color: #fff3cd;
            }
        """),
        ui.div(
            ui.h4("Subir Archivo"),
            ui.input_file(
                "archivo",
                "Haz clic para seleccionar archivo (PDF o Excel)",
                accept=[".pdf", ".xlsx", ".xls"],
            ),
            class_="area-subida",
        ),
        ui.output_text("estado"),
        title="Opciones",
        width=400,
    ),
    ui.h2("Extractor de Texto (PDF y Excel)"),
    ui.output_ui("resultados"),
)


def server(input, output, session):

  @output
  @render.text
  def estado():
    if input.archivo() is None:
      return "Esperando archivo..."
    else:
      return f"Procesando: {input.archivo()[0]['name']}"

  @reactive.Calc
  def resultados_archivo():
    if input.archivo() is None:
      return None

    archivo_info = input.archivo()[0]
    archivo_path = archivo_info["datapath"]
    nombre_archivo = archivo_info["name"].lower()

    if nombre_archivo.endswith(".pdf"):
      return procesar_pdf_shiny(archivo_path)
    elif nombre_archivo.endswith((".xlsx", ".xls")):
      return procesar_excel_shiny(archivo_path)
    else:
      return None

  @output
  @render.ui
  def resultados():
    if input.archivo() is None:
      return ui.p("Por favor, sube un archivo PDF o Excel para comenzar.")

    resultados = resultados_archivo()
    if not resultados:
      return ui.p(
          "Formato no compatible o no se pudieron extraer resultados del"
          " archivo."
      )

    contenido = []
    for item in resultados:
      if item.get("tipo") == "excel":
        titulo = (
            f"Hoja de Excel: {item.get('nombre_hoja', 'Sin nombre')} (Parte"
            f" {item['numero']})"
        )
      else:
        titulo = f"Página {item['numero']}"

      contenido.append(ui.h3(titulo))

      if item.get("texto_directo"):
        contenido.append(ui.h4("Texto extraído"))
        contenido.append(ui.pre(item["texto_directo"]))

      if item.get("ocr"):
        contenido.append(ui.h4("Texto desde imágenes (OCR)"))
        for ocr_item in item["ocr"]:
          contenido.append(ui.pre(ocr_item))

      if item.get("tablas"):
        subtitulo = (
            "Contenido de la Hoja"
            if item.get("tipo") == "excel"
            else "Tablas detectadas"
        )
        contenido.append(ui.h4(subtitulo))
        for tabla in item["tablas"]:
          contenido.append(ui.pre(tabla))

      contenido.append(ui.hr())

    return ui.div(*contenido)


# Crear la aplicación Shiny
app = App(app_ui, server)
