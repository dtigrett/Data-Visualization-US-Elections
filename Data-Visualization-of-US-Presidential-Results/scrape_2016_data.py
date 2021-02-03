import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import urllib
from IPython.display import display, display_pretty, Javascript, HTML
from urllib.request import urlopen
import urllib.request

# Import dependencies
import sys
import pandas as pd

import requests
from pprint import pprint
import pandas as pd
import json

import collections
import re, string
import sys
import time

#################################################
# Main Web Scraping Bot 2016
#################################################
def scrape_2016():
    # # Flow
    # 
    # - [Download and preprocess county-level results](#Townhall-data)
    # - [Download and preprocess county-level metadata](#Census-data)
    # - [Combine datasets](#Combine-data)
    # - [Export county-level results](#Export-data)
    # - [Visualize](#Visualize)

    # ## Townhall data

    # each page has a summary table that rolls up results at the state level
    # get rid of it
    def cond(x):
        if x:
            return x.startswith("table ec-table") and not "table ec-table ec-table-summary" in x
        else:
            return False

    # list of state abbreviations
    states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

    # headers for csv export
    data = [['state_abbr', 'county_name', 'party', 'votes_total']]

    # loop through each state's web page http://townhall.com/election/2016/president/%s/county, where %s is the state abbr
    # https://stackoverflow.com/questions/3969726/attributeerror-module-object-has-no-attribute-urlopen
    #siteurl = "http://www.python.org"

    #req = urllib.request.Request(siteurl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'})
    #pageHTML = urllib.request.urlopen(req).read()

    for state in states:
        siteurl = 'http://townhall.com/election/2016/president/' + state + '/county'
        req = urllib.request.Request(siteurl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'})
        pageHTML = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(pageHTML, "html.parser")

        # loop through each <table> tag with .ec-table class
        tables = soup.findAll('table', attrs={'class':cond})

        for table in tables:
            if table.findParent("table") is None:
                table_body = table.find('tbody')

                rows = table_body.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    # first tbody tr has four td
                    if len(cols) == 4:
                        # strip text from each td
                        divs = cols[0].find_all('div')
                        county = divs[0].text.strip()
                        party = cols[1]['class'][0]
                        total_votes = int(cols[2].text.strip().replace(',','').replace('-','0'))
                    # all other tbody tr have three td
                    else:
                        party = cols[1]['class'][0]
                        total_votes = int(cols[1].text.strip().replace(',','').replace('-','0'))
                        
                    #combine each row's results
                    rowData = [state,county,party,total_votes]
                    data.append(rowData)

    townhall = pd.DataFrame(data) # throw results in dataframe
    new_header = townhall.iloc[0] #grab the first row for the header
    townhall = townhall[1:] #take the data less the header row
    townhall.columns = new_header #set the header row as the df header
    townhall['votes_total'] = townhall['votes_total'].astype('float64')
    print(townhall.shape[0])
    # townhall.head()

    # view by state
    townhall[(townhall['state_abbr'] == 'AK')]

    # view special cases
    print(townhall[(townhall['state_abbr'] == 'NV') & (townhall['county_name'] == 'Carson City')])

    # fix townhall county name for Washington DC, Sainte Genevieve, MO, Oglala, SD
    townhall.loc[townhall['state_abbr'] =='DC', 'county_name'] = 'District of Columbia'
    townhall.loc[townhall['county_name'] == 'Sainte Genevieve', 'county_name'] = 'Ste. Genevieve County'
    townhall.loc[townhall['county_name'] == 'Oglala Lakota', 'county_name'] = 'Oglala'
    print(townhall[(townhall['county_name'] == 'District of Columbia') | (townhall['county_name'] == 'Ste. Genevieve County') | (townhall['county_name'] == 'Oglala')])

    # change 'Co.' to 'County' in county_name to match census county name
    townhall['county_name'] = townhall['county_name'].apply(lambda x: x.replace('Co.','County').strip())
    print(townhall[(townhall['state_abbr'] == 'NV') & (townhall['county_name'] == 'Carson City')])

    # combine state and county names
    townhall['combined'] = townhall['state_abbr'] + townhall['county_name'].apply(lambda x: x.replace(' ','').lower())
    print(townhall[(townhall['state_abbr'] == 'NV') & (townhall['county_name'] == 'Carson City')])

    # ## Census data
    # county_fips data from https://www.census.gov/geo/reference/codes/cou.html
    census = pd.read_csv('http://www2.census.gov/geo/docs/reference/codes/files/national_county.txt',sep=',',header=None, dtype=str)
    census.columns = ['state_abbr', 'state_fips', 'county_fips', 'county_name', 'fips_class_code']
    print(census.shape)
    # census.head()

    # view by state
    ak_counties = census[(census['state_abbr'] == 'AK')].shape[0]
    print(ak_counties)
    # census[(census['state_abbr'] == 'AK')]

    # view special cases
    print(census[(census['state_abbr'] == 'NV') & (census['county_name'] == 'Carson City')])

    # change Shannon County, SD to Oglala County, SD
    # http://rapidcityjournal.com/news/local/it-s-official-oglala-lakota-county-replaces-shannon-county-name/article_ac5c2369-3fea-5f94-9898-b007b7ddf22c.html
    # townhall.loc[townhall['county_name'] == 'Sainte Genevieve', 'county_name'] = 'Ste. Genevieve County'
    census.loc[(census['county_name'] == 'Shannon County') & (census['state_abbr'] == 'SD'), 'county_name'] = 'Oglala County'
    # census[(census['state_abbr'] == 'SD')]

    # state of Alaska reports results at the precinct and state level; no county level data available
    # report results as the states level; 
    # ugly fix to get townhall results and census counties to work together
    # future plan: roll up precinct-level results to the county level
    census.loc[(census['state_abbr'] == 'AK'),'county_name'] = 'Alaska'

    # change county_name values in townhall data to match 'county_name' values for C7 fips class code cities
    # get and transform C7 city names
    cities = (census['state_abbr'][(census['fips_class_code'] == 'C7')] + census['county_name'][(census['fips_class_code'] == 'C7')].apply(lambda x: x.replace('city','').replace(' ','').lower()))
    # cities

    # loop through 'combined' column and compare to cities series to add 'city' to H1 fips class code to townhall data
    for i, row in cities.iteritems():
        if row != 'NVcarsoncity':
            townhall.loc[townhall['combined'] == row, 'combined'] = row + 'city'
        
    print(townhall[(townhall['combined'] == 'NVcarsoncity')])

    # remove 'county' from 'combined' column of C7 fips class code counties in townhall
    townhall['combined'] = townhall['combined'].str.replace('county','')
    print(townhall[(townhall['county_name'] == 'Oglala')])

    census['combined'] = census['state_abbr'] + census['county_name'].apply(lambda x: x.replace('County','').replace('Parish','').replace(' ','').lower())
    print(census[(census['state_abbr'] == 'NV') & (census['county_name'] == 'Carson City')])
    # print(census[(census['state_abbr'] == 'VA') & (census['county_name'] == 'Bedford County')])

    # return sum of votes by state and county
    townhall['total_votes'] = townhall['votes_total'].groupby(townhall['combined']).transform('sum')
    townhall_counties = townhall.drop('votes_total',axis=1)

    # view dataset by selected state
    print(townhall_counties[(townhall_counties['state_abbr'] == 'NV') & (townhall_counties['county_name'] == 'Carson City')])

    # ## Combine data
    # join census and townhall data on the 'combined' column
    right = townhall.set_index('combined')
    left = census.set_index('combined')

    combined = left.join(right, lsuffix='', rsuffix='_r')
    combined = combined.reset_index()
    print('Joined dataset has ' + str(combined.shape[0]) + ' items')

    # view data by selected state
    combined[(combined['state_abbr'] == 'NV') & (combined['fips_class_code'] == 'C7')]

    # scale Alaska by number of counties
    combined.loc[(combined['state_abbr'] == 'AK'),'votes_total'] = (combined['votes_total'][combined['state_abbr'] == 'AK']/ak_counties).astype(int)
    #combined[combined['state_abbr'] == 'AK']

    # return unique dataset
    county_level_combined = combined.drop_duplicates()
    print('Combined dataset has ' + str(county_level_combined.shape[0]) + ' total items')
                                                    
    # return only D and R results
    county_level_combined = county_level_combined[(county_level_combined['party'] == 'GOP') | (county_level_combined['party'] == 'DEM')]
    print('Filtered dataset has ' + str(county_level_combined.shape[0]) + ' D and R items')

    # flatten dataset by adding votes by R and D columns
    county_level_combined['votes_dem'] = county_level_combined['votes_total'].where(county_level_combined['party'] == 'DEM',0).astype('float32')
    county_level_combined['votes_gop'] = county_level_combined['votes_total'].where(county_level_combined['party'] == 'GOP',0).astype('float32')

    # drop party and party-level totals and other columns
    county_level_combined.drop(['party','votes_total','state_abbr_r','county_name_r'], axis=1, inplace=True)
    # total_results = county_level_combined.drop(['party','votes_total','fips_class_code','state_abbr_r','county_name_r', 'votes_dem', 'votes_gop'], axis=1, inplace=True)
    county_level_combined[(county_level_combined['state_abbr'] == 'NV') & (county_level_combined['fips_class_code'] == 'C7')]

    # pivot data to consolidate
    party_pivot = pd.pivot_table(county_level_combined,index=["combined"],values=["votes_dem","votes_gop"],aggfunc=np.sum)
    total_pivot = pd.pivot_table(county_level_combined,index=["combined"],values=["total_votes"],aggfunc=np.mean)

    # join party and total pivots
    combined_pivot = party_pivot.join(total_pivot, lsuffix='', rsuffix='_r')
    print('Joined dataset has ' + str(combined_pivot.shape[0]) + ' items')
    # combined_pivot

    # add percentages for each R and D of total votes
    # calculate percentage of total vote per major candidates
    combined_pivot['per_dem'] = combined_pivot['votes_dem'] / combined_pivot['total_votes']
    combined_pivot['per_gop'] = combined_pivot['votes_gop'] / combined_pivot['total_votes']
    # combined_pivot['diff'] = abs(combined_pivot['votes_gop'] - combined_pivot['votes_dem']).map('{:,.0f}'.format)
    combined_pivot['diff'] = abs(combined_pivot['votes_gop'] - combined_pivot['votes_dem'])
    # combined_pivot['per_point_diff'] = abs(combined_pivot['per_dem'] - combined_pivot['per_gop']).map('{:,.2%}'.format)
    combined_pivot['per_point_diff'] = abs(combined_pivot['per_dem'] - combined_pivot['per_gop'])

    # combined_pivot

    # join pivotted and unpivotted data
    right = census.set_index('combined')
    # left = combined_pivot.set_index('combined')

    county_level_final = combined_pivot.join(right, lsuffix='', rsuffix='_r')
    county_level_final = county_level_final.reset_index()
    print('Joined dataset has ' + str(county_level_final.shape[0]) + ' items')
    # county_level_final

    # create FIPS columns for visualizations
    county_level_final['combined_fips'] = county_level_final['state_fips'].apply(lambda x: x.lstrip('0')) + county_level_final['county_fips']
    # county_level_final

    # drop irrelevant columns
    county_level_final = county_level_final.drop(['combined','county_fips','state_fips','fips_class_code'], axis=1)
    print('Final dataset has ' + str(county_level_final.shape[0]) + ' items')
    # county_level_final

    #county_level_final = county_level_final[[state_name,county_fips,county_name,votes_gop,votes_dem,total_votes,diff,per_gop,per_dem,per_point_diff]]

    # state_name,county_fips,county_name,votes_gop,votes_dem,total_votes,diff,per_gop,per_dem,per_point_diff
    # votes_dem,votes_gop,total_votes,per_dem,per_gop,diff,per_point_diff,state_abbr,county_name,combined_fips

    # view data by selected state
    #county_level_final[(county_level_final['state_abbr'] == 'AK')]
    county_level_final.to_csv('2016_US_County_Level_Presidential_Results_init.csv',sep=',',index=False)

if __name__ == "__main__":
    print(scrape_2016())