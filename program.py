import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# Database connection setup
try:
    engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/postgres')
    print("Database engine created successfully.")
except Exception as e:
    print(f"Error creating database engine: {e}")
    exit()

# SQL Query
query = r"""
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
"""

# Fetch data into DataFrame
try:
    with engine.connect() as conn:
        generic_df = pd.read_sql(sql=query, con=conn)
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error while loading data: {e}")
    exit()

# Plotting
plt.figure(figsize=(8, 6))
sns.barplot(x='medication_type', y='total_cost', data=generic_df, palette='Set2')
plt.title('Total Cost by Medication Type')
plt.xlabel('Medication Type')
plt.ylabel('Total Cost')
plt.tight_layout()
plt.show()



# # # Read data into DataFrame
# query = """
# -- SQL Query: Average prescription cost per practitioner
# SELECT
#     pr.id AS practitioner_id,
#     CONCAT(pr."firstName", ' ', pr."lastName") AS practitioner_name,
#     pt.type AS practitioner_type,
#     AVG(p."cost") AS average_prescription_cost,
#     COUNT(p.id) AS prescription_count
# FROM
#     public.prescription p
# LEFT JOIN
#     public.patient_visit pv ON p."patientVisitId" = pv.id
# LEFT JOIN
#     public.practitioner pr ON pv."practitionerId" = pr.id
# LEFT JOIN
#     public.practitioner_type pt ON pr."practitionerTypeId" = pt.id
# GROUP BY
#     pr.id, practitioner_name, pt.type
# HAVING
#     COUNT(p.id) >= 50  -- Consider practitioners with at least 50 prescriptions
# ORDER BY
#     average_prescription_cost DESC;
# """
# # Read data into DataFrame
# performance_df = pd.read_sql(query, engine)

# # Plotting
# plt.figure(figsize=(14, 8))
# sns.scatterplot(
#     x='prescription_count',
#     y='average_prescription_cost',
#     hue='practitioner_type',
#     data=performance_df,
#     palette='deep',
#     s=100,
#     alpha=0.7,
#     edgecolor='k'
# )
# plt.title('Practitioner Performance Analysis')
# plt.xlabel('Prescription Count')
# plt.ylabel('Average Prescription Cost')
# plt.legend(title='Practitioner Type', bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.tight_layout()
# plt.show()

# # Read data into DataFrame
# query = """
# -- SQL Query: Prescriptions by practitioner type and medication
# SELECT
#     pt.type AS practitioner_type,
#     prd.name AS medication_name,
#     COUNT(p.id) AS prescription_count,
#     SUM(p."cost") AS total_cost
# FROM
#     public.prescription p
# LEFT JOIN
#     public.patient_visit pv ON p."patientVisitId" = pv.id
# LEFT JOIN
#     public.practitioner pr ON pv."practitionerId" = pr.id
# LEFT JOIN
#     public.practitioner_type pt ON pr."practitionerTypeId" = pt.id
# LEFT JOIN
#     public.product prd ON p."productId" = prd.id
# GROUP BY
#     pt.type, prd.name
# ORDER BY
#     prescription_count DESC;

# """

# prescribing_df = pd.read_sql(query, engine)

# # Data Preparation
# # Let's focus on the top 10 medications for visualization
# top_medications = prescribing_df['medication_name'].value_counts().head(10).index
# filtered_df = prescribing_df[prescribing_df['medication_name'].isin(top_medications)]

# # Pivot data for heatmap
# pivot_df = filtered_df.pivot_table(
#     values='prescription_count',
#     index='medication_name',
#     columns='practitioner_type',
#     aggfunc='sum',
#     fill_value=0
# )

# # Plotting
# plt.figure(figsize=(12, 8))
# sns.heatmap(pivot_df, annot=True, fmt="d", cmap='YlGnBu')
# plt.title('Prescription Counts by Practitioner Type and Medication')
# plt.xlabel('Practitioner Type')
# plt.ylabel('Medication Name')
# plt.tight_layout()
# plt.show()

# SQL Query to compare tariffs and claim amounts
# tariff_query = """
# -- SQL Query: Compare tariffs to claim amounts for top prescriptions
# SELECT
#     prd.name AS prescription_name,
#     AVG(t.price) AS average_tariff_price,
#     AVG(p."cost") AS average_claim_amount,
#     AVG(p."cost" - t.price) AS average_difference
# FROM
#     public.prescription p
# LEFT JOIN
#     public.product prd ON p."productId" = prd.id
# LEFT JOIN
#     public.tariff t ON p."tariffId" = t.id
# WHERE
#     prd.name IN (
#         SELECT
#             prd.name
#         FROM
#             public.prescription p
#         LEFT JOIN
#             public.product prd ON p."productId" = prd.id
#         GROUP BY
#             prd.name
#         ORDER BY
#             SUM(p."cost") DESC
#         LIMIT 10
#     )
# GROUP BY
#     prd.name
# ORDER BY
#     average_difference DESC;

# """

# # Read data into DataFrame
# tariff_df = pd.read_sql(tariff_query, engine)

# # Data Preparation
# tariff_df['prescription_name'] = tariff_df['prescription_name'].str.strip()

# # Plotting Average Difference
# plt.figure(figsize=(12, 6))
# sns.barplot(x='prescription_name', y='average_difference', data=tariff_df, palette='coolwarm')
# plt.title('Average Difference Between Claim Amount and Tariff Price')
# plt.xlabel('Prescription Name')
# plt.ylabel('Average Difference (Claim Amount - Tariff Price)')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()


# SQL Query to get total cost per province for top prescriptions
# regional_query = """
# -- SQL Query: Total cost per province for top prescriptions
# SELECT
#     lp.name AS province_name,
#     prd.name AS prescription_name,
#     SUM(p."cost") AS total_cost
# FROM
#     public.prescription p
# LEFT JOIN
#     public.product prd ON p."productId" = prd.id
# LEFT JOIN
#     public.patient_visit pv ON p."patientVisitId" = pv.id
# LEFT JOIN
#     public.facility f ON pv."dispensingFacilityId" = f.id
# LEFT JOIN
#     public.location lp ON f."provinceId" = lp.id
# WHERE
#     UPPER(lp.type) = 'PROVINCE' AND
#     prd.name IN (
#         SELECT
#             prd.name
#         FROM
#             public.prescription p
#         LEFT JOIN
#             public.product prd ON p."productId" = prd.id
#         GROUP BY
#             prd.name
#         ORDER BY
#             SUM(p."cost") DESC
#         LIMIT 10
#     )
# GROUP BY
#     lp.name, prd.name
# ORDER BY
#     total_cost DESC;
# """

# # Read data into DataFrame
# regional_df = pd.read_sql(regional_query, engine)

# # Data Preparation
# regional_df['province_name'] = regional_df['province_name'].str.strip().str.title()
# regional_df['prescription_name'] = regional_df['prescription_name'].str.strip()

# # Pivot the DataFrame for Heatmap
# regional_pivot = regional_df.pivot(index='province_name', columns='prescription_name', values='total_cost')

# # Plotting
# plt.figure(figsize=(12, 8))
# sns.heatmap(regional_pivot, annot=True, fmt=".0f", cmap='YlGnBu')
# plt.title('Total Cost of Top Prescriptions by Province')
# plt.xlabel('Prescription Name')
# plt.ylabel('Province')
# plt.tight_layout()
# plt.show()


# SQL Query to get monthly cost data for top prescriptions
# trends_query = """
# SELECT
#     prd.name AS prescription_name,
#     DATE_TRUNC('month', p."prescribedAt") AS month,
#     SUM(p."cost") AS monthly_total
# FROM
#     public.prescription p
# LEFT JOIN
#     public.product prd ON p."productId" = prd.id
# WHERE
#     prd.name IN (
#         SELECT
#             prd.name
#         FROM
#             public.prescription p
#         LEFT JOIN
#             public.product prd ON p."productId" = prd.id
#         GROUP BY
#             prd.name
#         ORDER BY
#             SUM(p."cost") DESC
#         LIMIT 10
#     )
# GROUP BY
#     prd.name, month
# ORDER BY
#     month, prescription_name;
# """

# # Read data into DataFrame
# trends_df = pd.read_sql(trends_query, engine)

# # Convert 'month' to datetime
# trends_df['month'] = pd.to_datetime(trends_df['month'])

# # Sort the DataFrame
# trends_df = trends_df.sort_values(by=['prescription_name', 'month'])

# # Plotting
# plt.figure(figsize=(14, 8))
# sns.lineplot(data=trends_df, x='month', y='monthly_total', hue='prescription_name', marker='o')
# plt.title('Cost Trends Over Time for Top Prescriptions')
# plt.xlabel('Month')
# plt.ylabel('Total Monthly Cost')
# plt.legend(title='Prescription Name', bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.tight_layout()
# plt.show()




# # SQL Query to find top 10 costliest prescriptions
# query = """
# SELECT
#     prd.name AS prescription_name,
#     SUM(p."cost") AS total_claim_amount
# FROM
#     public.prescription p
# LEFT JOIN
#     public.product prd ON p."productId" = prd.id
# GROUP BY
#     prd.name
# ORDER BY
#     total_claim_amount DESC
# LIMIT 10;
# """

# # Read data into DataFrame
# top_prescriptions_df = pd.read_sql(query, engine)

# # Verify the DataFrame
# print("Top 10 Costliest Prescriptions:")
# print(top_prescriptions_df)

# # Plotting
# plt.figure(figsize=(12, 6))
# sns.barplot(x='total_claim_amount', y='prescription_name', data=top_prescriptions_df, palette='viridis')
# plt.title('Top 10 Costliest Prescriptions')
# plt.xlabel('Total Claim Amount')
# plt.ylabel('Prescription Name')
# plt.tight_layout()
# plt.show()

# # SQL Query to get member counts by province
# query = """
# SELECT
#     lp.name AS province_name,
#     COUNT(DISTINCT m.id) AS member_count
# FROM
#     public.member m
# LEFT JOIN
#     public.patient_visit pv ON m.id = pv."patientId"
# LEFT JOIN
#     public.facility f ON pv."dispensingFacilityId" = f.id
# LEFT JOIN
#     public.location lp ON f."provinceId" = lp.id
# WHERE
#     UPPER(lp.type) = 'PROVINCE'  -- Ensure case matches
# GROUP BY
#     lp.name
# ORDER BY
#     member_count ASC;
# """

# # Read data into DataFrame
# # Use a connection object
# with engine.connect() as conn:
#     member_counts_df  = pd.read_sql(query, conn)

# # Standardize province names for consistency
# member_counts_df['province_name'] = member_counts_df['province_name'].str.strip().str.title()

# # Verify the DataFrame
# print(member_counts_df)

# # Plotting
# plt.figure(figsize=(10, 6))
# sns.barplot(x='province_name', y='member_count', data=member_counts_df, palette='viridis')
# plt.title('Membership Counts by Province')
# plt.xlabel('Province')
# plt.ylabel('Number of Members')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# # Query to get member counts by province
# query = """
# SELECT
#     lp.name AS province_name,
#     COUNT(DISTINCT m.id) AS member_count
# FROM
#     public.member m
# LEFT JOIN
#     public.patient_visit pv ON m.id = pv."patientId"
# LEFT JOIN
#     public.facility f ON pv."dispensingFacilityId" = f.id
# LEFT JOIN
#     public.location lp ON f."provinceId" = lp.id
# WHERE
#     UPPER(lp.type) = 'PROVINCE'  -- Ensure case matches
# GROUP BY
#     lp.name
# ORDER BY
#     member_count DESC;
# """

# Use a connection object
# with engine.connect() as conn:
#     membership_df  = pd.read_sql(query, conn)



# facility_sql_query = """
# SELECT
#     lp.name AS province_name,
#     COUNT(DISTINCT f.id) AS facility_count
# FROM
#     public.facility f
# LEFT JOIN
#     public.location lp ON f."provinceId" = lp.id
# WHERE
#     UPPER(lp.type) = 'PROVINCE'
# GROUP BY
#     lp.name
# ORDER BY
#     facility_count ASC;
# """

# visit_sql_query = """
# SELECT
#     lp.name AS province_name,
#     COUNT(pv.id) AS patient_visit_count
# FROM
#     public.patient_visit pv
# LEFT JOIN
#     public.facility f ON pv."dispensingFacilityId" = f.id
# LEFT JOIN
#     public.location lp ON f."provinceId" = lp.id
# WHERE
#     lp.type = 'PROVINCE'
# GROUP BY
#     lp.name
# ORDER BY
#     patient_visit_count DESC;
# """
# # Read data into DataFrames
# # Use a connection object
# with engine.connect() as conn:
#     facility_df = pd.read_sql(facility_sql_query, conn)
#     visit_df = pd.read_sql(visit_sql_query, conn)

# # Standardize province names
# def standardize_province_name(name):
#     if name:
#         return name.strip().lower()
#     return name

# facility_df['province_name'] = facility_df['province_name'].apply(standardize_province_name)
# visit_df['province_name'] = visit_df['province_name'].apply(standardize_province_name)

# # Merge facility and visit data
# combined_df = facility_df.merge(visit_df, on='province_name', how='inner')

# # Calculate visits per facility
# combined_df['visits_per_facility'] = combined_df['patient_visit_count'] / combined_df['facility_count']

# # Display combined data
# print("Combined Data:")
# print(combined_df)


# # Plotting facility counts by province
# plt.figure(figsize=(10, 6))
# sns.barplot(x='province_name', y='facility_count', data=facility_df)
# plt.title('Facility Counts by Province')
# plt.xlabel('Province')
# plt.ylabel('Number of Facilities')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()


# # Plotting patient visit counts by province
# plt.figure(figsize=(10, 6))
# sns.barplot(x='province_name', y='patient_visit_count', data=visit_df)
# plt.title('Patient Visit Counts by Province')
# plt.xlabel('Province')
# plt.ylabel('Number of Patient Visits')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# # Plotting visits per facility by province
# plt.figure(figsize=(10, 6))
# sns.barplot(x='province_name', y='visits_per_facility', data=combined_df)
# plt.title('Average Visits per Facility by Province')
# plt.xlabel('Province')
# plt.ylabel('Visits per Facility')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()


# # Verify the DataFrame
# print(membership_df.columns)
# print(membership_df.head())

# # Plotting
# plt.figure(figsize=(10, 6))
# sns.barplot(x='province_name', y='member_count', data=membership_df)
# plt.title('Membership Distribution by Province')
# plt.xlabel('Province')
# plt.ylabel('Number of Members')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()


# print(df.head())

# print(df.shape)

# print(df.isnull().sum())

# print(df.describe(include='all'))

# print(df['member_gender'].value_counts())
# print(df['visit_status'].value_counts())
# print(df['facility_type'].value_counts())


# member_by_province = df.groupby('province_name')['member_id'].nunique().reset_index()
# sns.barplot(x='province_name', y='member_id', data=member_by_province)
# plt.xticks(rotation=90)
# plt.title('Membership Distribution by Province')
# plt.show()

# prescription_costs = df.groupby('product_name')['prescription_cost'].sum().reset_index()
# top_10_prescriptions = prescription_costs.sort_values('prescription_cost', ascending=False).head(10)
# sns.barplot(x='product_name', y='prescription_cost', data=top_10_prescriptions)
# plt.xticks(rotation=90)
# plt.title('Top 10 Costliest Prescriptions')
# plt.show()

# # Existing code
# df['prescribedAt'] = pd.to_datetime(df['prescribedAt'])
# df['month'] = df['prescribedAt'].dt.to_period('M')

# # Convert 'month' to string
# cost_trends = df.groupby('month')['prescription_cost'].sum().reset_index()
# cost_trends['month'] = cost_trends['month'].astype(str)

# # Plotting
# sns.lineplot(x='month', y='prescription_cost', data=cost_trends)
# plt.xticks(rotation=45)
# plt.title('Prescription Cost Trends Over Time')
# plt.show()


# facility_visits = df.groupby('facility_type')['patient_visit_id'].nunique().reset_index()
# sns.barplot(x='facility_type', y='patient_visit_id', data=facility_visits)
# plt.xticks(rotation=90)
# plt.title('Facility Visits by Type')
# plt.show()

# practitioner_costs = df.groupby(['practitioner_first_name', 'practitioner_last_name'])['prescription_cost'].sum().reset_index()
# top_practitioners = practitioner_costs.sort_values('prescription_cost', ascending=False).head(10)
# sns.barplot(x='prescription_cost', y='practitioner_first_name', data=top_practitioners)
# plt.title('Top Practitioners by Prescription Costs')
# plt.show()



