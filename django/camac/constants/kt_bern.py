#!/usr/bin/env python3

"""
Adaptation of Custom_Constants from PHP.

Only contains the constants that we actually need
"""

# Instance states
INSTANCE_STATE_NEW = 1

INSTANCE_STATE_EBAU_NUMMER_VERGEBEN = 20000

INSTANCE_STATE_IN_PROGRESS = 120001
INSTANCE_STATE_IN_PROGRESS_INTERNAL = 120002
INSTANCE_STATE_KOORDINATION = 20005
INSTANCE_STATE_VERFAHRENSPROGRAMM_INIT = 20003
INSTANCE_STATE_ZIRKULATION = 20004

INSTANCE_STATE_CORRECTION_IN_PROGRESS = 20007
INSTANCE_STATE_CORRECTED = 20008

INSTANCE_STATE_SB1 = 20011
INSTANCE_STATE_SB2 = 20013

INSTANCE_STATE_TO_BE_FINISHED = 20014
INSTANCE_STATE_FINISHED = 20010
INSTANCE_STATE_REJECTED = 10000
INSTANCE_STATE_ARCHIVED = 20009
INSTANCE_STATE_DONE = 120000
INSTANCE_STATE_DONE_INTERNAL = 120003


# Deprecated instance states
INSTANCE_STATE_DOSSIERPRUEFUNG = 20006
INSTANCE_STATE_ALLGEMEINE_INFORMATIONEN = 20001  # replaced by new
INSTANCE_STATE_AUSWAHL_SPEZIALFORMULARE = 80003  # replaced by new
INSTANCE_STATE_BAUWERK = 80002  # replaced by new
INSTANCE_STATE_BESTAETIGUNG = 110_002  # replaced by new
INSTANCE_STATE_DOKUMENTE = 110_000  # replaced by new
INSTANCE_STATE_FREIGABEQUITTUNG = 40000  # replaced by new
INSTANCE_STATE_INFORMATION_UEBER_GRUNDSTUECK = 80001  # replaced by new
INSTANCE_STATE_NUTZUNG_BAUVORHABEN = 80000  # replaced by new
INSTANCE_STATE_VORABKLAERUNG_EINFACH = 110_001  # replaced by new
INSTANCE_STATE_SELBSTDEKLARATION_FREIGABEQUITTUNG = 40001  # replaced by sb1
INSTANCE_STATE_ABSCHLUSS_DOKUMENTE = 40003  # replaced by sb2
INSTANCE_STATE_ABSCHLUSS_FREIGABEQUITTUNG = 40002  # replaced by sb2


# Public instance states
PUBLIC_INSTANCE_STATE_CREATING = "creation"
PUBLIC_INSTANCE_STATE_RECEIVING = "receiving"
PUBLIC_INSTANCE_STATE_COMMUNAL = "communal"
PUBLIC_INSTANCE_STATE_IN_PROGRESS = "in-progress"
PUBLIC_INSTANCE_STATE_SB1 = "sb1"
PUBLIC_INSTANCE_STATE_SB2 = "sb2"
PUBLIC_INSTANCE_STATE_FINISHED = "finished"
PUBLIC_INSTANCE_STATE_REJECTED = "rejected"
PUBLIC_INSTANCE_STATE_CORRECTED = "corrected"
PUBLIC_INSTANCE_STATE_ARCHIVED = "archived"
PUBLIC_INSTANCE_STATE_DONE = "done"


# ServiceGroups
SERVICE_GROUP_SERVICE = 1
SERVICE_GROUP_LEITBEHOERDE_GEMEINDE = 2
SERVICE_GROUP_BAUKONTROLLE = 3
SERVICE_GROUP_RSTA = 20000

# Groups
CAMAC_ADMIN_GROUP = 1
CAMAC_SUPPORT_GROUP = 10000

# Forms
DASHBOARD_FORM_SLUG = "dashboard"

# Questions
QUESTION_EBAU_NR_EXISTS = 20034
QUESTION_EBAU_NR = 20035

# Chapters
CHAPTER_EBAU_NR = 20000

# MESSAGE_TYPES
ECH_BASE_DELIVERY = "5200000"
ECH_SUBMIT = "5100000"
ECH_FILE_SUBSEQUENTLY = "5100001"
ECH_WITHDRAW_PLANNING_PERMISSION_APPLICATION = "5100002"
ECH_CLAIM = "5200004"
ECH_ACCOMPANYING_REPORT = "5100004"
ECH_CHANGE_RESPONSIBILITY = "5200005"
ECH_TASK_STELLUNGNAHME = "5200007"
ECH_TASK_SB1_SUBMITTED = "5200008"
ECH_TASK_SB2_SUBMITTED = "5200009"
ECH_STATUS_NOTIFICATION_EBAU_NR_VERGEBEN = "5200030"
ECH_STATUS_NOTIFICATION_ZIRKULATION_GESTARTET = "5200032"
ECH_STATUS_NOTIFICATION_SB1_AUSSTEHEND = "5200033"
ECH_STATUS_NOTIFICATION_ABGESCHLOSSEN = "5200036"
ECH_STATUS_NOTIFICATION_ZURUECKGEWIESEN = "5200037"
ECH_STATUS_NOTIFICATION_IN_KOORDINATION = "5200038"

# Notice Types
NOTICE_TYPE_STELLUNGNAHME = 1
NOTICE_TYPE_NEBENBESTIMMUNG = 20000

# circulation answers
CIRCULATION_ANSWER_ENTWURF = 20000
CIRCULATION_ANSWER_POSITIV = 20001
CIRCULATION_ANSWER_NEGATIV = 20003
CIRCULATION_ANSWER_NICHT_BETROFFEN = 20004
CIRCULATION_ANSWER_NACHFORDERUNG = 20005

CIRCULATION_STATE_WORKING = 1
CIRCULATION_STATE_DONE = 2

CIRCULATION_TYPE_STANDARD = 20000

# decisions
DECISIONS_BEWILLIGT = "accepted"
DECISIONS_ABGELEHNT = "denied"
DECISIONS_ABGESCHRIEBEN = "writtenOff"
VORABKLAERUNG_DECISIONS_BEWILLIGT = "positive"
VORABKLAERUNG_DECISIONS_BEWILLIGT_MIT_VORBEHALT = "conditionallyPositive"
VORABKLAERUNG_DECISIONS_NEGATIVE = "negative"

# ECH 211 judgementType
# Grundsätzliche Beurteilung.
# 1 = Positiv
# 2 = Positiv mit Bedingungen
# 3 = Nicht eintreten
# 4 = abgelehnt
DECISION_JUDGEMENT_MAP = {
    "building-permit": {
        DECISIONS_BEWILLIGT: 1,
        DECISIONS_ABGESCHRIEBEN: 3,
        DECISIONS_ABGELEHNT: 4,
    },
    "preliminary-clarification": {
        VORABKLAERUNG_DECISIONS_BEWILLIGT: 1,
        VORABKLAERUNG_DECISIONS_BEWILLIGT_MIT_VORBEHALT: 2,
        VORABKLAERUNG_DECISIONS_NEGATIVE: 4,
    },
}

# Attachment sections
ATTACHMENT_SECTION_BETEILIGTE_BEHOERDEN = 2
ATTACHMENT_SECTION_ALLE_BETEILIGTEN = 3
ATTACHMENT_SECTION_BEILAGEN_SB1 = 6
ATTACHMENT_SECTION_BEILAGEN_SB2 = 5
ATTACHMENT_SECTION_BEILAGEN_GESUCH = 1

# Notification template slugs
NOTIFICATION_ECH = "03-verfahrensablauf-fachstelle"

# Instance resource
INSTANCE_RESOURCE_ZIRKULATION = 20004
