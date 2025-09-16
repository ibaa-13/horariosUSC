const plantillaId = '1ObvPFAO4ihGtGAhqC8Gdyxr2KsznEaFosZAwrLfNvic';
const datasetId = "1djb9S0Dj1cFAvNZoZTtmEwLbqRhNHPLi";
const folderId = "1t0MuWKpEcvZZgJrSrFVwh9wVg8fRClC3"

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

function onFormSubmit(e) {
  const correo = e.namedValues["Dirección de correo electrónico"][0];
  Logger.log(Object.entries(e.namedValues));
  // Load the dataset
  const dataset = importCSVfromDrive(datasetId);

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
  let copia = archivoOriginal.makeCopy('Horario');
  let doc = DocumentApp.openById(copia.getId());

  // Replace placeholders in the document
  replacePlaceholders(finalDic, doc);

  // Export as PDF and save to Drive
  Logger.log("Exportando en pdf.");
  const blobPDF = copia.getAs(MimeType.PDF).setName('Horario');
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
