export default {
  columns: {
    caluma: ["dossierNr", "caseDocumentFormName", "intent", "caseStatus"],
    "camac-ng": [
      "dossierNr",
      "instanceFormDescription",
      "locationSZ",
      "builderSZ",
      "intentSZ",
      "instanceStateDescription",
    ],
  },
  activeFilters: {
    caluma: ["dossierNumberSZ", "intent", "caseStatus", "caseDocumentFormName"],
    "camac-ng": [
      "instanceIdentifier",
      "instanceStateDescription",
      "locationSZ",
      "responsibleServiceUser",
      "addressSZ",
      "intentSZ",
      "plotSZ",
      "builderSZ",
      "landownerSZ",
      "applicantSZ",
      "submitDateAfterSZ",
      "submitDateBeforeSZ",
      "serviceSZ",
      "formSZ",
    ],
  },
  formFields: [
    "bauherrschaft",
    "bauherrschaft-v2",
    "bauherrschaft-v3",
    "bauherrschaft-override",
    "bezeichnung",
    "bezeichnung-override",
  ],
  order: {
    caluma: [{ meta: "dossier-number" }],
    "camac-ng": ["instance__identifier"],
  },
};
