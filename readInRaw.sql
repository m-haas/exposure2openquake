-----------------------------------------------------------------------------------------------
-- JORDAN
-----------------------------------------------------------------------------------------------
--table containing Censusdata of Jordan with material/floors
CREATE TABLE jor_census_mat_floors(
  adm0 varchar(100),
  adm1 varchar(100),
  n_buildings int,
  construction_mat varchar(100),
  n_floors int,
  rural_urban varchar(100),
  census_year int 
);
--populate
COPY jor_census_mat_floors 
FROM '/home/mhaas/Desktop/PhD/DESERVE/Data/Exposure/csv/Jordan/JOR_mat_floors.csv' 
CSV HEADER; 

--table containing Censusdata of Jordan with age/floors
CREATE TABLE jor_census_age_floors(
  adm0 varchar(100),
  adm1 varchar(100),
  n_buildings int,
  n_floors int,
  rural_urban varchar(100),
  built_after int,
  built_before int,
  census_year int 
);
--populate
COPY jor_census_age_floors 
FROM '/home/mhaas/Desktop/PhD/DESERVE/Data/Exposure/csv/Jordan/JOR_age_floors.csv' 
CSV HEADER;
-----------------------------------------------------------------------------------------------
-- PALESTINE
-----------------------------------------------------------------------------------------------
--table containing Censusdata of Palestine with material
CREATE TABLE pse_census_mat(
  adm0 varchar(100),
  adm1 varchar(100),
  n_buildings int,
  construction_mat varchar(100),
  gaza_westbank varchar(100),
  census_year int 
);
--populate
COPY pse_census_mat 
FROM '/home/mhaas/Desktop/PhD/DESERVE/Data/Exposure/csv/Palestine/PSE_mat.csv' 
CSV HEADER; 

--table containing Censusdata of Palestine with age
CREATE TABLE pse_census_age(
  adm0 varchar(100),
  adm1 varchar(100),
  n_buildings int,
  gaza_westbank varchar(100),
  built_after int,
  built_before int,
  census_year int 
);
--populate
COPY pse_census_age 
FROM '/home/mhaas/Desktop/PhD/DESERVE/Data/Exposure/csv/Palestine/PSE_age.csv' 
CSV HEADER;

--table containing Censusdata of Palestine with age
CREATE TABLE pse_census_floors(
  adm0 varchar(100),
  n_buildings int,
  n_floors int,
  gaza_westbank varchar(100),
  census_year int 
);
--populate
COPY pse_census_floors 
FROM '/home/mhaas/Desktop/PhD/DESERVE/Data/Exposure/csv/Palestine/PSE_floors.csv' 
CSV HEADER;
