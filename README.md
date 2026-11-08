Requisitos
    1. Instalar pytesseract https://github.com/UB-Mannheim/tesseract/wiki

    2. Instalar las librerias necesesarias usando el siguiente comando:
        pip install shiny PyMuPDF pytesseract pillow pdfplumber

    3. En esta linea:
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            Se debe de colocar la ruta de tesserract.exe, generalmente se instala por defecto ahi mismo
            en la que ya esta 

 
Cómo ejecutar el código?
    1. En su editor de preferencia, en este caso se utilizó Visual Studio Code hacer el siguiente 
    convinación de teclas Ctrl + shift + ñ, sino vaya a terminal > nueva terminal

    2. Escribir el siguiente comando shiny run <nombre de su app>.py
        NOTA: Aquí debe eliminar desde "<" hasta ">" y colocar el nombre de su app

    3. Presionar Enter

    4. Le desplegará un link http://127.0.0.1:8000, solo deberá copiarlo 
	    y pegarlo en el navegador de su preferencia o ponga su mouse arriba del link, precione Ctrl y de click,
        esto abrirá la aplicación en el navegador que usted tenga por defecto en su computadora
