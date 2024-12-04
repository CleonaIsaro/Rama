-- Identify Missing Data in a Table
SELECT * FROM table_name WHERE column_name IS NULL;


-- Standardize Location Names to Uppercase
UPDATE location SET name = UPPER(name);


-- Trim Whitespace and Standardize Employer Names
UPDATE employer SET name = INITCAP(TRIM(name));

-- List Facility Types
SELECT
 e.enumlabel AS facility_type
FROM
 pg_type t
 JOIN pg_enum e ON t.oid = e.enumtypid
WHERE
 t.typname = 'facility_type_enum';


-- Extract Comprehensive Data for Analysis
SELECT
 m.id AS member_id,
 m."firstName" AS member_first_name,
 m."lastName" AS member_last_name,
 m.gender AS member_gender,
 m."dateOfBirth" AS member_date_of_birth,
 pv.id AS patient_visit_id,
 pv."treatmentDate",
 pv."status" AS visit_status,
 pv."totalCost" AS visit_total_cost,
 p.id AS prescription_id,
 p."cost" AS prescription_cost,
 p."patientContribution",
 p."prescribedAt",
 p.status AS prescription_status,
 f.id AS facility_id,
 f.name AS facility_name,
 f.type AS facility_type,
 f.category AS facility_category,
 lp.name AS province_name,
 ld.name AS district_name,
 ls.name AS sector_name,
 lc.name AS cell_name,
 lv.name AS village_name,
 pr."firstName" AS practitioner_first_name,
 pr."lastName" AS practitioner_last_name,
 pr."practitionerLicenseNumber",
 prd.name AS product_name,
 prd.type AS product_type,
 prd.category AS product_category,
 t.price AS tariff_price,
 t.status AS tariff_status
FROM
 public.member m
INNER JOIN
 public.patient_visit pv ON m.id = pv."patientId"
INNER JOIN
 public.prescription p ON pv.id = p."patientVisitId"
INNER JOIN
 public.facility f ON pv."dispensingFacilityId" = f.id
LEFT JOIN
 public.location lp ON f."provinceId" = lp.id
LEFT JOIN
 public.location ld ON f."districtId" = ld.id
LEFT JOIN
 public.location ls ON f."sectorId" = ls.id
LEFT JOIN
 public.location lc ON f."cellId" = lc.id
LEFT JOIN
 public.location lv ON f."villageId" = lv.id
LEFT JOIN
 public.practitioner pr ON pv."practitionerId" = pr.id
LEFT JOIN
 public.product prd ON p."productId" = prd.id
LEFT JOIN
 public.tariff t ON p."tariffId" = t.id;

-- Membership Distribution by Province
SELECT
 lp.name AS province_name,
 COUNT(DISTINCT m.id) AS member_count
FROM
 public.member m
LEFT JOIN
 public.patient_visit pv ON m.id = pv."patientId"
LEFT JOIN
 public.facility f ON pv."dispensingFacilityId" = f.id
LEFT JOIN
 public.location lp ON f."provinceId" = lp.id
WHERE
 UPPER(lp.type) = 'PROVINCE'
GROUP BY
 lp.name
ORDER BY
 member_count DESC;


-- Top 10 Costliest Prescriptions
SELECT
 prd.name AS prescription_name,
 SUM(p."cost") AS total_claim_amount
FROM
 public.prescription p
LEFT JOIN
 public.product prd ON p."productId" = prd.id
GROUP BY
 prd.name
ORDER BY
 total_claim_amount DESC
LIMIT 10;


-- Cost Trends of Top Prescriptions Over Time
SELECT
 prd.name AS prescription_name,
 DATE_TRUNC('month', p."prescribedAt") AS month,
 SUM(p."cost") AS monthly_total
FROM
 public.prescription p
LEFT JOIN
 public.product prd ON p."productId" = prd.id
WHERE
 prd.name IN (
 SELECT
 prd.name
 FROM
 public.prescription p
 LEFT JOIN
 public.product prd ON p."productId" = prd.id
 GROUP BY
 prd.name
 ORDER BY
 SUM(p."cost") DESC
 LIMIT 10
 )
GROUP BY
 prd.name, month
ORDER BY
 month, prescription_name;


-- Total Cost of Top Prescriptions by Province
SELECT
 lp.name AS province_name,
 prd.name AS prescription_name,
 SUM(p."cost") AS total_cost
FROM
 public.prescription p
LEFT JOIN
 public.product prd ON p."productId" = prd.id
LEFT JOIN
 public.patient_visit pv ON p."patientVisitId" = pv.id
LEFT JOIN
 public.facility f ON pv."dispensingFacilityId" = f.id
LEFT JOIN
 public.location lp ON f."provinceId" = lp.id
WHERE
 UPPER(lp.type) = 'PROVINCE' AND
 prd.name IN (
 SELECT
 prd.name
 FROM
 public.prescription p
 LEFT JOIN
 public.product prd ON p."productId" = prd.id
 GROUP BY
 prd.name
 ORDER BY
 SUM(p."cost") DESC
 LIMIT 10
 )
GROUP BY
 lp.name, prd.name
ORDER BY
 total_cost DESC;


-- Generic vs. Brand Medication Costs
SELECT
 CASE 
 WHEN prd.name LIKE '%||%' THEN 'Brand' 
 ELSE 'Generic' 
 END AS medication_type,
 SUM(p."cost") AS total_cost,
 COUNT(p.id) AS prescription_count
FROM
 public.prescription p
LEFT JOIN
 public.product prd ON p."productId" = prd.id
WHERE
 prd."type" = 'DRUG' AND prd.category = 'MEDICINE'
GROUP BY
 medication_type
ORDER BY
 total_cost DESC;


-- Estimate Potential Savings by Switching to Generics
WITH generic_medications AS (
 SELECT
 TRIM(BOTH FROM prd.name) AS generic_name,
 AVG(p."cost") AS average_generic_cost
 FROM
 public.prescription p
 LEFT JOIN
 public.product prd ON p."productId" = prd.id
 WHERE
 prd."type" = 'DRUG' AND prd.category = 'MEDICINE'
 AND prd.name NOT LIKE '%||%' -- Generic medications
 GROUP BY
 generic_name
),
brand_medications AS (
 SELECT
 TRIM(BOTH FROM split_part(prd.name, '||', 1)) AS generic_name,
 TRIM(BOTH FROM split_part(prd.name, '||', 2)) AS brand_name,
 SUM(p."cost") AS total_brand_cost,
 COUNT(p.id) AS brand_prescription_count,
 AVG(p."cost") AS average_brand_cost
 FROM
 public.prescription p
 LEFT JOIN
 public.product prd ON p."productId" = prd.id
 WHERE
 prd."type" = 'DRUG' AND prd.category = 'MEDICINE'
 AND prd.name LIKE '%||%' -- Brand medications
 GROUP BY
 generic_name, brand_name
)
SELECT
 bm.brand_name AS brand_medication_name,
 bm.generic_name,
 bm.total_brand_cost,
 bm.brand_prescription_count,
 bm.average_brand_cost,
 gm.average_generic_cost,
 (bm.total_brand_cost - (bm.brand_prescription_count * 
gm.average_generic_cost)) AS potential_savings
FROM
 brand_medications bm
LEFT JOIN
 generic_medications gm ON bm.generic_name = gm.generic_name
WHERE
 gm.average_generic_cost IS NOT NULL
ORDER BY
 potential_savings DESC;


