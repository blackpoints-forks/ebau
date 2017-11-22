ALTER TABLE "IR_EDITCIRCULATION" ADD COLUMN "CIRCULATION_EMAIL_ACTION_ID" integer;

ALTER TABLE "IR_EDITCIRCULATION" ADD CONSTRAINT "FKIR_EDITCIR466073" FOREIGN KEY ("CIRCULATION_EMAIL_ACTION_ID") REFERENCES "ACTION" ("ACTION_ID");

CREATE SEQUENCE "ACTIVATION_LOG_SEQ";

-- TODO enter appropriate next value
SELECT setval("ACTIVATION_LOG_SEQ_id_seq", 4, true);
