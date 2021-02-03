import pandas as pd
import numpy as np
import re
import requests
from lxml import html
from IPython.display import display, display_pretty, Javascript, HTML

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
# Main Web Scraping Bot 2020
#################################################
def api_2020():

    # # Flow
    # 
    # - [Process county-level results](#New-York-Times-data)
    # - [Process county-level geographies](#Census-geographies)
    # - [Combine datasets](#Combine-data)
    # - [Export county-level results](#Export-data)
    # - [Visualize](#Visualize)

    # ## New York Times data

    # connect to data

    election_url = "https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/national-map-page/national/president.json"

    # make an http request for the page
    election_request = requests.request(
        method='GET', 
        url=election_url,
        headers={ "Accept": "application/json" }
    )

    election_response = election_request.json()

    election_data = election_response['data']['races']

    ## parse response into dataframe, and select and rename final columns
    election_data_df = pd.DataFrame(election_data)[['state_name', 'counties']].rename(columns={"state_name": "t_state_name"})

    # after https://stackoverflow.com/a/49962887
    # unnest 'counties' column, turning object keys in dataframe columns and object values into rows, select certain keys from each array, and rename those keys (columns)
    election_data_df = pd.DataFrame(
        [
            dict(y, t_state_name=i) for i, x in zip(
                election_data_df['t_state_name'],
                election_data_df['counties']
            ) for y in x
        ]
    )[['fips', 'name', 'votes', 't_state_name', 'results']].rename(columns={"fips": "geoid", "votes": "total_votes", "name": "t_county_name"})

    # after https://stackoverflow.com/a/38231651
    ## unravel dictionary (JSON object) into other columns, choose final columns, rename them, and cast their data types
    election_data_df = pd.concat(
        [
            election_data_df.drop(['results'], axis=1), 
            election_data_df['results'].apply(pd.Series)
        ], 
        axis=1
    )[['geoid', 't_county_name', 'total_votes', 't_state_name', 'trumpd', 'bidenj']].rename(columns={"trumpd": "votes_gop", "bidenj": "votes_dem"}).astype({'votes_gop': 'int64', 'votes_dem': 'int64'})

    # create state FIPS codes from the 5-digit 'geoid'
    election_data_df['state_fips'] = election_data_df['geoid'].str[:2]

    print(election_data_df.shape, election_data_df.dtypes)
    # election_data_df.head(10)

    # ## Census geographies

    # get state geography data

    # read state file csv and create dataframe
    census_states = pd.read_csv(
        'https://www2.census.gov/geo/docs/reference/state.txt',
        delimiter='|',
        header=0,
        usecols=[0,1,2],
        names=['state_fips', 'state_abbr', 'c_state_name'],
        dtype=str
    )

    # define a list of FIPS codes of the internally-autonomous entities the U.S. has some control over
    suzerainty_fips = ['60','66','69','72','74','78']

    # filter out these Suzerainty entities
    census_states = census_states[~census_states.state_fips.isin(suzerainty_fips)]

    print(census_states.shape, '\n', census_states.dtypes)
    #census_states.tail(7)

    # get county geography data

    # base_url where all the county gazetteer files live
    gazetteer_url = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2019_Gazetteer/"

    # make an http request for the page
    page = requests.request(
        method='GET', 
        url=gazetteer_url,
        headers={ "Accept": "application/json" }
    )

    # parse the page and return a DOM tree
    tree = html.fromstring(page.content)

    # use XPath to return a list of link texts ('a' elements within the 'table' element) from the DOM
    gazatteer_files = tree.xpath('//td/a/text()')

    # filter the list to return only county file names
    county_files = [c for c in gazatteer_files if re.match(r'.*counties.*\.txt', c)]

    # county_files

    # read each county file csv
    census_county_files = [
        pd.read_csv(
            gazetteer_url + county_file,
            delimiter='\t',
            lineterminator='\n',
            header=0,
            usecols=[1,3],
            names=['geoid', 'c_county_name'],
            dtype=str
        ) for county_file in county_files]

    # combine into a dataframe
    census_counties = pd.concat(census_county_files, ignore_index=True)

    # create state FIPS codes from the 5-digit 'geoid'
    census_counties['state_fips'] = census_counties['geoid'].str[:2]

    print(census_counties.shape, '\n', census_counties.dtypes)
    #census_counties.tail(10)

    # merge state and county geography data
    census_geographies = census_states.merge(
        census_counties, 
        on='state_fips',
        how="left"
    )

    # drop and rename duplicate keys
    census_geographies = census_geographies.drop(['state_fips', 'state_abbr'], axis=1)

    print(census_geographies.shape, '\n', census_geographies.dtypes)
    #census_geographies.tail(10)

    # ## Combine data

    # merge county election data with county geographies

    ## merge to county geography files on county FIPS code
    election_results = election_data_df.merge(
        right=census_geographies,
        on="geoid",
        how="left"
    )

    ## create authoritative state and county name columns provided by Census
    election_results['state_name'] = np.where(
        pd.isnull(election_results['c_state_name']), 
        election_results['t_state_name'], 
        election_results['c_state_name']
    )

    election_results['county_name'] = np.where(
        pd.isnull(election_results['c_county_name']), 
        election_results['t_county_name'], 
        election_results['c_county_name']
    )

    ## replace Alaska District names
    election_results['county_name'].replace('(ED )','District ', inplace=True, regex=True)

    election_results = election_results.drop(["t_county_name", "t_state_name", "c_county_name", "c_state_name"], axis=1)

    ## filter dataframe to exclude Washington, D.C.
    other_results = election_results[election_results['state_fips'] != '11']

    ### filter dataframe to just Washington, D.C. results
    dc_results = election_results[election_results['state_fips'] == '11']

    ## rollup Washington, D.C. ward-level results to the state level
    ### aggregate votes and pluck first names
    dc_results_aggregates = dc_results.groupby('state_fips', as_index=False).agg(
        { 'geoid': 'min', 'state_name': 'min', 'county_name': 'min', 'total_votes': 'sum', 'votes_gop': 'sum', 'votes_dem': 'sum' }
    )

    ## combine DC and other county results, rename columns to match column names historically used in this repo
    county_level_final = other_results.append(
        dc_results_aggregates, sort=True
    ).reset_index(
        drop=True
    ).drop(
        ['state_fips'], axis=1
    ).rename(
        columns={'geoid': 'county_fips'}
    ).sort_values(
        by='county_fips'
    ).reindex(
        columns=['state_name','county_fips','county_name','votes_gop','votes_dem','total_votes','diff','per_gop','per_dem','per_point_diff']
    )

    ## add other metrics, including percentage of total votes captured by the GOP candidate, percentage of total votes captured by the DEM candidate, total difference between the two, and the percentage point difference
    county_level_final['per_gop'] = np.where(
        county_level_final['total_votes'] == 0, 
        0, 
        county_level_final['votes_gop'] / county_level_final['total_votes']
    )

    county_level_final['per_dem'] = np.where(
        county_level_final['total_votes'] == 0, 
        0, 
        county_level_final['votes_dem'] / county_level_final['total_votes']
    )

    county_level_final['diff'] = county_level_final['votes_gop'] - county_level_final['votes_dem']
    county_level_final['per_point_diff'] = county_level_final['per_gop'] - county_level_final['per_dem']

    print(county_level_final.shape, '\n', county_level_final.dtypes)
    #county_level_final.tail(15)

    county_level_final.to_csv(
        '2020_US_County_Level_Presidential_Results_init.csv',
        sep=',',
        index=False
    )

if __name__ == "__main__":
    print(api_2020())