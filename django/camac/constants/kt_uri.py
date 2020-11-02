KOOR_BG_SERVICE_ID = 1
KOOR_NP_SERVICE_ID = 87
KOOR_BD_SERVICE_ID = 302

CIRCULATION_STATE_RUN = 1
CIRCULATION_STATE_OK = 2
CIRCULATION_STATE_IDLE = 21
CIRCULATION_STATE_NFD = 41

ROLE_MUNICIPALITY = 6  # Sekretariat der Gemeindebaubehörde

INSTANCE_STATE_COMM = 21
INSTANCE_STATE_EXT = 22
INSTANCE_STATE_EXT_GEM = 32
INSTANCE_STATE_CIRC = 23
INSTANCE_STATE_REDAC = 24
INSTANCE_STATE_DONE = 25
INSTANCE_STATE_ARCH = 26
INSTANCE_STATE_DEL = 27
INSTANCE_STATE_NEW = 1
INSTANCE_STATE_NEW_PORTAL = 28
INSTANCE_STATE_CONTROL = 34

# TODO theoretically, we'd like to hide COMM as well, but instances can be sent
# "back" into "COMM" if the canton didn't do a circulation
INSTANCE_STATES_HIDDEN_FOR_KOOR = [INSTANCE_STATE_NEW, INSTANCE_STATE_NEW_PORTAL]

# Question identifiers (Chapter/Question/Item) for various information that we need
# Format: List of 3-tuples to implement fallback
CQI_FOR_PROPOSAL = [(21, 97, 1)]
CQI_FOR_PROPOSAL_DESCRIPTION = [(21, 98, 1)]
CQI_FOR_PARZELLE = [(21, 91, 1), (101, 91, 1), (102, 91, 1)]
CQI_FOR_STREET = [(21, 93, 1), (101, 93, 1), (102, 93, 1)]
CQI_FOR_APPLICANT_NAME = [(1, 23, 1)]
CQI_FOR_APPLICANT_ORGANISATION = [(1, 221, 1)]
CQI_FOR_APPLICANT_STREET = [(1, 61, 1)]
CQI_FOR_APPLICANT_ZIP_CITY = [(1, 62, 1)]
CQI_FOR_NFD_COMPLETION_DATE = (41, 243, 1)


NOTIFICATION_TEMPLATE_DEADLINE_DATE_FACHSTELLE = (
    "aktivierung-deadline-überzogen-fachstelle"  # 1448
)
NOTIFICATION_TEMPLATE_COMPLETION_DATE_FACHSTELLE = (
    "aktivierung-nfd-vollständig-überzogen-fachstelle"  # 1449
)
NOTIFICATION_TEMPLATE_DEADLINE_DATE_LEITBEHOERDE = (
    "aktivierung-deadline-überzogen-leitbehoerde"  # 1450
)
NOTIFICATION_TEMPLATE_COMPLETION_DATE_LEITBEHOERDE = (
    "aktivierung-nfd-vollständig-überzogen-leitbehoerde"  # 1451
)
CQI_FOR_GESUCHSTELLER = [(1, 23, 1)]

FORM_VORABKLAERUNG_MIT_KANTON = 21
FORM_BGBB = 41
FORM_MITBERICHT_BG = 42
FORM_GENEHMIGUNG = 43
FORM_BAUGESUCH_MIT_KANTON = 44
FORM_LUFTFAHRT = 45
FORM_MILITAER = 46
FORM_BAUGESUCH_OHNE_KANTON = 47
FORM_VORABKLAERUNG_MIT_KANTON = 21
FORM_VORABKLAERUNG_OHNE_KANTON = 61
FORM_GENEHMIGUNG_TEILREVISION_NP = 101
FORM_VORPRUEFUNG_TEILREVISION_NP = 102
FORM_VORPRUEFUNG_GESAMTREVISION_NP = 103
FORM_GENEHMIGUNG_GESAMTREVISION_NP = 104
FORM_VORPRUERUNG_QGP = 105
FORM_GENEHMIGUNG_QGP = 106
FORM_VORPRUERUNG_QP = 107
FORM_GENEHMIGUNG_QP = 108
FORM_REKLAME = 121
FORM_MELDUNG_SOLARANLAGE = 141
FORM_MITBERICHT_NP = 161
FORM_PGV_KANTONSSTRASSE = 181
FORM_PGV_GEMEINDESTRASSE = 201
FORM_PGV_KORPORATIONSSTRASSE = 221
FORM_PGV_VEREINFACHT = 222
FORM_PGV_OEFFENTLICHE_GEWAESSER = 223
FORM_PGV_PRIVATE_GEWAESSER = 224
FORM_KONZESSION_REGIERUNGSRAT = 225
FORM_KONZESSION_LANDRAT = 241
FORM_KONZESSION_WARME = 242
FORM_PGV_STARKSTROM = 243
FORM_PGV_EISENBAHNGESETZ = 244
FORM_PGV_NATIONALSTRASSE = 245
FORM_BD_KANTONSGEWAESSER = 246
FORM_KANTONSGEBIET = 247
FORM_MITBERICHT_BD = 248
FORM_REKLAME_BD = 249
FORM_PGV_SEILBAHNGESETZ = 250
FORM_MITBERICHT_AFU = 251
FORM_MITBERICHT_UMWELTSCHUTZ = 252
FORM_MITBERICHT_UVP = 253
FORM_MITBERICHT_ALA = 254
FORM_MITBERICHT_ALA_KORPORATION = 255
FORM_MITBERICHT_AFE = 256
FORM_KONZESSION_REGIERUNGSRAT_AFE = 257
FORM_KONZESSION_LANDRAT_AFE = 258
FORM_KONZESSION_WARME_AFE = 259
FORM_MITBERICHT_AFJ = 260
FORM_MELDUNG_OEREB_AFJ = 281
FORM_MELDUNG_OEREB_AFU = 282
FORM_MELDUNG_OEREB_NP = 284
FORM_MELDUNG_OEREB_BD = 285
FORM_LANDERWERB = 286
FORM_MITBERICHT_SD_AFKP = 287
FORM_MITBERICHT_SD = 288
FORM_AFE_KORPORATIONSGEWAESSER = 289
FORM_MELDUNG_VORHABEN = 290
FORM_KANTONSGEBIET_SD = 291
FORM_MITBERICHT_BUNDESSTELLE = 292
FORM_ARCHIV = 293
FORM_ARCHIV_AFJ = 294
FORM_MELDUNG_VORHABEN_AFJ = 295

PORTAL_FORMS = [
    FORM_BAUGESUCH_MIT_KANTON,
    FORM_BAUGESUCH_OHNE_KANTON,
    FORM_VORABKLAERUNG_MIT_KANTON,
    FORM_VORABKLAERUNG_OHNE_KANTON,
    FORM_REKLAME,
    FORM_MELDUNG_SOLARANLAGE,
    FORM_MELDUNG_VORHABEN,
]

RESPONSIBLE_KOORS = {
    KOOR_BD_SERVICE_ID: [FORM_PGV_EISENBAHNGESETZ],
    KOOR_BG_SERVICE_ID: [FORM_PGV_SEILBAHNGESETZ, FORM_MITBERICHT_BUNDESSTELLE],
}


CALUMA_FORM_MAPPING = {
    FORM_VORABKLAERUNG_MIT_KANTON: "preliminary-clarification-canton",
    FORM_BGBB: "bgbb",
    FORM_MITBERICHT_BG: "mitbericht-bg",
    FORM_GENEHMIGUNG: "genehmigung",
    FORM_BAUGESUCH_MIT_KANTON: "building-permit-canton",
    FORM_LUFTFAHRT: "pgv-luftfahrt",
    FORM_MILITAER: "pgv-militaer",
    FORM_BAUGESUCH_OHNE_KANTON: "building-permit-municipality",
    FORM_VORABKLAERUNG_OHNE_KANTON: "preliminary-clarification-municipality",
    FORM_GENEHMIGUNG_TEILREVISION_NP: "genehmigung-teilrevision-np",
    FORM_VORPRUEFUNG_TEILREVISION_NP: "vorpruefung-teilrevision-np",
    FORM_VORPRUEFUNG_GESAMTREVISION_NP: "vorpruefung-gesamtrevision-np",
    FORM_GENEHMIGUNG_GESAMTREVISION_NP: "gesamtrevision-np",
    FORM_VORPRUERUNG_QGP: "vorpruefung-qgp",
    FORM_GENEHMIGUNG_QGP: "genehmigung-qgp",
    FORM_VORPRUERUNG_QP: "vorpruefung-qp",
    FORM_GENEHMIGUNG_QP: "genehmigung-qp",
    FORM_REKLAME: "commercial-permit",
    FORM_MELDUNG_SOLARANLAGE: "solar-announcement",
    FORM_MITBERICHT_NP: "mitbericht-np",
    FORM_MITBERICHT_AFJ: "mitbericht-afj",
    FORM_MITBERICHT_ALA: "mitbericht-ala",
    FORM_MITBERICHT_ALA_KORPORATION: "mitbericht-ala-korporation",
    FORM_MITBERICHT_AFU: "mitbericht-afu",
    FORM_MITBERICHT_AFE: "mitbericht-afe",
    FORM_MITBERICHT_UMWELTSCHUTZ: "mitbericht-umweltschutz",
    FORM_MITBERICHT_UVP: "mitbericht-uvp",
    FORM_MITBERICHT_SD: "mitbericht-sd",
    FORM_MITBERICHT_SD_AFKP: "mitbericht-sd-afkp",
    FORM_PGV_KANTONSSTRASSE: "pgv-kantonsstrasse",
    FORM_PGV_GEMEINDESTRASSE: "pgv-gemeindestrasse",
    FORM_PGV_KORPORATIONSSTRASSE: "pgv-korporationsstrasse",
    FORM_PGV_NATIONALSTRASSE: "pgv-nationalstrasse",
    FORM_PGV_VEREINFACHT: "pgv-vereinfachtes-verfahren",
    FORM_PGV_OEFFENTLICHE_GEWAESSER: "pgv-oeffentliche-gewaesser",
    FORM_PGV_PRIVATE_GEWAESSER: "pgv-private-gewaesser",
    FORM_PGV_EISENBAHNGESETZ: "pgv-eisenbahn",
    FORM_PGV_SEILBAHNGESETZ: "pgv-seilbahn",
    FORM_PGV_STARKSTROM: "pgv-starkstrom",
    FORM_KONZESSION_REGIERUNGSRAT: "konzession-regierungsrat",
    FORM_KONZESSION_LANDRAT: "konzession-landrat",
    FORM_KONZESSION_WARME: "konzession-warme",
    FORM_KONZESSION_REGIERUNGSRAT_AFE: "konzession-regierungsrat-afe",
    FORM_KONZESSION_LANDRAT_AFE: "konzession-landrat-afe",
    FORM_KONZESSION_WARME_AFE: "konzession-warme-afe",
    FORM_AFE_KORPORATIONSGEWAESSER: "afe-korporationsgewaesser",
    FORM_BD_KANTONSGEWAESSER: "bd-kantonsgewaesser",
    FORM_KANTONSGEBIET: "kantonsgebiet",
    FORM_MITBERICHT_BD: "mitbericht-bd",
    FORM_REKLAME_BD: "reklame-bd",
    FORM_KANTONSGEBIET_SD: "kantonsgebiet-sd",
    FORM_MELDUNG_OEREB_AFJ: "oereb-afj",
    FORM_MELDUNG_OEREB_NP: "oereb-np",
    FORM_MELDUNG_OEREB_BD: "oereb-bd",
    FORM_MELDUNG_OEREB_AFU: "oereb-afu",
    FORM_LANDERWERB: "landerwerb",
    FORM_MELDUNG_VORHABEN: "project-announcement",
    FORM_ARCHIV: "archiv",
    FORM_MELDUNG_VORHABEN_AFJ: "project-announcement-afj",
    FORM_ARCHIV_AFJ: "archiv-afj",
    FORM_MITBERICHT_BUNDESSTELLE: "mitbericht-bundesstelle",
}
