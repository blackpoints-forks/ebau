
CREATE TABLE SANCTION
(
  SANCTION_ID NUMBER NOT NULL
, INSTANCE_ID NUMBER NOT NULL
, SERVICE_ID NUMBER NOT NULL
, USER_ID NUMBER NOT NULL
, TEXT VARCHAR2(4000) NOT NULL
, START_DATE DATE NOT NULL
, DEADLINE_DATE DATE
, END_DATE DATE
, NOTICE VARCHAR(500)
, IS_FINISHED NUMBER(1,0) DEFAULT 0 NOT NULL
, CONSTRAINT INSTANCE_FK FOREIGN KEY (INSTANCE_ID) REFERENCES INSTANCE (INSTANCE_ID)
, CONSTRAINT SERVICE_FK FOREIGN KEY (SERVICE_ID) REFERENCES SERVICE (SERVICE_ID)
, CONSTRAINT USER_FK FOREIGN KEY (USER_ID) REFERENCES "USER" (USER_ID)
, CONSTRAINT SANCTION_PK PRIMARY KEY (SANCTION_ID) ENABLE
);

CREATE SEQUENCE SANCTION_SEQ INCREMENT BY 1 START WITH 1 MAXVALUE 9000000 MINVALUE 1 ORDER;
