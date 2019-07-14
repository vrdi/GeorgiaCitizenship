
---
title: Georgia Citizenship Project
author: 
- Kat Henneberger
- Maira Khan
- Brian Morris
- Jasmine Noory
- Qi Wan Sim
- Bri White
- Sarah Cannon (adviser)
- Lee Hachadoorian (adviser)
date: July 12, 2019
---

# Introduction
This week our group had three main objectives. These goals included constructing a data-set for both blocks and Census tracts, testing how party leaning and minority opportunity districts could be constructed, and streamlining the data-generating process for others who wish to use our code. 
1. Data Collection
2. District Construction- Partison Leanings & Minority-Opportunity
3. Generalizable Code

Georgia is a state with dynamic political opportunity. The party split is currently evenly between Republican-leaning and Democrat-leaning voters, though Republicans do control the General Assembly. The recent 2018 gubernatorial election resulted in record numbers of voters registered, and the state narrowly missed electing its first African-American female governor. Republicans are currently the majority in the state, but a growing Latino population and newly registered African-Americans have resulted in a state that has shifting political allegiances. 

# National Apportionment
Details here

#Prisoner Reallocation
Summary: Research was conducted on the availability of prisoner's origins and their current residence. Prisoner reallocation varies across states, with California randomly reassigning prisoners across geographies. In Georgia, inmates are counted towards the population count of the district/county they are incarcerated in, not their county of origin. In 2010, there were 20,213 inmates in the Department of Corrections. The American Community Survey does not provide county of origin for the incarcerated population, so pulling together different data sources was necessary.

Data on prisoner origins is made available on the county level by the Georgia Department of Corrections(GDC). 

Data Source(2010): http://www.dcor.state.ga.us/sites/all/files/pdf/Research/Annual/Profile_inmate_admissions_CY2010.pdf

#Pg.11- Home County
#Re: County of Origin & Inmate Processing 
County of Origin- 
1. Fulton County(2,160 inmates)  12.3% of total inmate population
2. Dekalb County (1,157 inmates)	6.50%	of total inmate population
3. Cobb County (1,075	inmates) 6.04%	of total inmate population

** 2,401		unreported counties of origin

Almost a quarter of the prison population within the state of Georgia derive from two central counties- Fulton & Dekalb County. Both of these counties have Georgia's highest African-American population, at 59%. Prison-based gerrymandering moves minority voting power away from the community, and places it in districts that are usually white, and rural. 

# Sources of Citizenship Data
ACS
Census special tabulation
Investigation of Administrative sources

# Data Preparation
Before running chains on both the census tract and block group level we first obtained the necessary demographic data from the Census Bureau's American Community Survey (ACS). This demographic data incudes population counts across races, hispanic ethnicity, sex, citizenship and age. We then joined this data with the block group tigerline Georgia shapefile and census tract tigerline Georgia shapefile separately. Our goal within this data prepraration process was to generalize our code so that future research could easily be conducted using different demographic data or by analyzing another state.
## Census Tracts

## Block Groups
Citizenship data was collected at the block group level from the Census special tabulation method: the ACS 5 year estimates. Of particular interest is the tabulations by race and ethnicity since Georgia has a sizeable immigrant population, landing at 10%. The following groups of interest were considered in our tabulation: Hispanic and Non-Hispanic (alone), as well as White alone, Black alone, Asian alone, American Indian and Native Alaskan alone, Native Hawaiian and Pacific Islander alone, and 2 or more races. One advantage of using block groups with which to aggregating precinct partisan information is the resolution of our analysis. We transformed this data from the original csv, in which each observation is a ethnicity within a block group, to citizen voting age counts by by block groups. 


# Question 1 and results
How does minority representation look along four variables- Total Population, Voting Age Population, Citizen Population, and Citizen Age Population? This question becomes even more crucial when considering the upcoming 2020 Census, and the continued debate on whether a citizenship question should be included on the form. Georgia has the highest growing Latino population in the country, and while not uniform, African-Americans and Latinos do tend to vote in a consensus, especially in key elections. 
We conducted runs on U.S Congressional districts- Georgia currently has 14. We also found that if districts are conducted based on citizenship or citizenship voting age population, Georgia would lose 1 Congressional seat. 

Results 

# Question 2 and results


