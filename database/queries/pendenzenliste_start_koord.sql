SELECT
	"INSTANCE"."INSTANCE_ID"   AS "INSTANCE_ID",
	"ANSWER_DOK_NR"."ANSWER"   AS "DOSSIER_NR",
	"FORM"."NAME"              AS "FORM",
	"LOCATION"."NAME"          AS "COMMUNITY",
	"USER"."USERNAME"          AS "USER",
	"ANSWER_PETITION"."ANSWER" AS "PETITION",
	(
		SELECT
			LISTAGG("ANSWER_LIST"."NAME", ', ') WITHIN GROUP (ORDER BY "ANSWER_LIST"."NAME")
		FROM
			table(json_unserialize((
					SELECT
						"ANSWER" as "ANSW"
					FROM
						"ANSWER"
					WHERE
						"ANSWER"."INSTANCE_ID" = "INSTANCE"."INSTANCE_ID"
						AND
						"QUESTION_ID" = 97
						AND
						"CHAPTER_ID" = 21
						AND
						"ITEM" = 1
					))
				)
		JOIN "ANSWER_LIST" ON (
			"VAL" = "VALUE"
		)
	) AS "INTENT",
	"ANSWER_CITY"."ANSWER"     AS "CITY",
	"INSTANCE_STATE"."NAME"    AS "STATE"
FROM
	"INSTANCE"
JOIN
	"INSTANCE_LOCATION" ON (
		"INSTANCE"."INSTANCE_ID" = "INSTANCE_LOCATION"."INSTANCE_ID"
	)
JOIN 
	"LOCATION" ON (
	 "INSTANCE_LOCATION"."LOCATION_ID" = "LOCATION"."LOCATION_ID"
	)
JOIN
	FORM ON (
		"INSTANCE"."FORM_ID" = "FORM"."FORM_ID"
)
JOIN
	"USER" ON (
		"INSTANCE"."USER_ID" = "USER"."USER_ID"
)
JOIN
	"ANSWER" "ANSWER_DOK_NR" ON (
		"INSTANCE"."INSTANCE_ID" = "ANSWER_DOK_NR"."INSTANCE_ID"
		AND
		"ANSWER_DOK_NR"."QUESTION_ID" = 6
		AND
		"ANSWER_DOK_NR"."CHAPTER_ID" = 2
		AND
		"ANSWER_DOK_NR"."ITEM" = 1
	)
LEFT JOIN
	"ANSWER" "ANSWER_PETITION" ON (
		"INSTANCE"."INSTANCE_ID" = "ANSWER_PETITION"."INSTANCE_ID"
		AND
		"ANSWER_PETITION"."QUESTION_ID" = 23
		AND
		"ANSWER_PETITION"."CHAPTER_ID" = 1
		AND
		"ANSWER_PETITION"."ITEM" = 1
	)
LEFT JOIN
	"ANSWER" "ANSWER_CITY" ON (
		"INSTANCE"."INSTANCE_ID" = "ANSWER_CITY"."INSTANCE_ID"
		AND
		"ANSWER_CITY"."QUESTION_ID" = 63
		AND
		"ANSWER_CITY"."CHAPTER_ID" = 1
		AND
		"ANSWER_CITY"."ITEM" = 1
	)
JOIN 
	"INSTANCE_STATE" ON (
	"INSTANCE_STATE"."NAME" = 'ext'
)
WHERE
	"INSTANCE"."INSTANCE_STATE_ID" = "INSTANCE_STATE"."INSTANCE_STATE_ID"
