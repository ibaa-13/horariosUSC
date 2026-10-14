const plantillaId = PropertiesService.getScriptProperties().getProperty('PLANTILLA_ID');
const datasetId = PropertiesService.getScriptProperties().getProperty('DATASET_ID');
const folderId = PropertiesService.getScriptProperties().getProperty('FOLDER_ID');
const nombre_columna_correo = "Dirección de correo electrónico"; // Nombre de la columna del excel que guarda los correos electrónicos

function importCSVfromDrive(fileId) {
  let file = DriveApp.getFileById(fileId);
  let csvContent = file.getBlob().getDataAsString();

  // Split into rows and filter empty lines
  let rows = csvContent.split("\n").filter(r => r.trim() !== "");

  // Split each row into cells and trim whitespace
  let data = rows.map(row => row.split(";").map(cell => cell.trim()));

  // Extract headers
  let headers = data.shift();

  // Convert rows to array of objects
  let objects = data.map(row => {
    let obj = {};
    row.forEach((cell, i) => {
      obj[headers[i]] = cell;
    });
    return obj;
  });

  Logger.log('CSV imported successfully');
  return objects;
}

function createSlotDictionary(objects) {
  let slotDict = {};

  objects.forEach(row => {
    let slot = row.Slot.trim();
    if (!(slot in slotDict)) {
      slotDict[slot] = [];
    }
  });

  Logger.log("Diccionario creado");
  return slotDict;
}

function pasteDic(dic) {
  let newDic = {};
  for (let slot in dic) {
    newDic[slot] = dic[slot].join(""); // concatenate all strings
  }
  return newDic;
}

function replacePlaceholders(dic, doc) {
  let body = doc.getBody();
  for (let key in dic) {
    // Escape any regex characters in key
    let escapedKey = key.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    body.replaceText(escapedKey, dic[key]);
  }
  doc.saveAndClose();
}

function assertCSVHeaders(objects, requiredHeaders) {
  if (!objects || objects.length === 0) {
    throw new Error("El CSV está vacío o no contiene filas de datos.");
  }

  const headers = Object.keys(objects[0]);

  const missing = requiredHeaders.filter(h => !headers.includes(h));
  if (missing.length > 0) {
    throw new Error(
      "El CSV no tiene las columnas esperadas.\nFaltan: " + missing.join(", ")
    );
  }
}

function onFormSubmit(e) {
  const correo = e.namedValues[nombre_columna_correo][0];

  const usuario = correo.includes("@")
  ? correo.split("@")[0]
  : correo

  Logger.log(Object.entries(e.namedValues));
  // Load the dataset
  const dataset = importCSVfromDrive(datasetId);

  assertCSVHeaders(dataset, [
  "Slot",
  "Asignatura",
  "Grupo",
  "Aula"
  ]);

  // Create the dictionary of slots
  let dic = createSlotDictionary(dataset);

  // Loop over form subjects

  for (let [subject_name, groupValues] of Object.entries(e.namedValues)) {
  if (!groupValues || groupValues.length === 0) continue;

  // Google Forms may return a single string with multiple options joined by comma
  let groups = groupValues[0].split(",").map(g => g.trim().toUpperCase());

  // Filter dataset by subject
  let totalsubject = dataset.filter(row => row.Asignatura.trim() === subject_name.trim());

  // Match any group selected
  let filtered = totalsubject.filter(row =>
    groups.includes(row.Grupo.trim().toUpperCase())
  );

  // Add to dictionary
  filtered.forEach(row => {
    let slot = row.Slot.trim();
    if (dic[slot]) {
      let entry = `${row.Asignatura}\n[${row.Grupo}]\n${row.Aula}\n`;
      dic[slot].push(entry);
    }
  });
}

  Logger.log("Estado final del diccionario: ");
  Logger.log(dic);

  // Collapse the lists into single strings
  let finalDic = pasteDic(dic);

  // Copy template and open the document
  Logger.log("Creando plantilla.");
  const archivoOriginal = DriveApp.getFileById(plantillaId);
  let copia = archivoOriginal.makeCopy('Horario ' + usuario);
  let doc = DocumentApp.openById(copia.getId());

  // Replace placeholders in the document
  replacePlaceholders(finalDic, doc);

  // Export as PDF and save to Drive
  Logger.log("Exportando en pdf.");
  const blobPDF = copia.getAs(MimeType.PDF).setName('Horario ' + usuario);
  const carpetaDestino = DriveApp.getFolderById(folderId);
  const pdfFile = carpetaDestino.createFile(blobPDF);

  // Share the PDF with the student
  Logger.log("Compartiendo archivo con " + correo);
  pdfFile.addViewer(correo);

  // Delete the temporary Google Doc
  DriveApp.getFileById(copia.getId()).setTrashed(true);

  // -----Register the PDF link in the response sheet------
  const hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // Get the headers from the first row
  const headers = hoja.getRange(1, 1, 1, hoja.getLastColumn()).getValues()[0];

  // Check if there is a "Links" column
  let linksCol = headers.indexOf("Links") + 1; // +1 because Sheets are 1-indexed

  if (linksCol === 0) {
    // "Links" column doesn't exist, create it at the end
    linksCol = hoja.getLastColumn() + 1;
    hoja.getRange(1, linksCol).setValue("Links");
  }

  // Write the PDF URL in the row corresponding to the latest submission
  const ultimaFila = hoja.getLastRow();
  hoja.getRange(ultimaFila, linksCol).setValue(pdfFile.getUrl());
}
