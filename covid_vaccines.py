import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import json
import pandas as pd
import numpy as np
import base64
from io import BytesIO

st.title("Covid Vaccine availability")

dist_codes = pd.read_csv("district_names_Id.csv",low_memory=False)
dist_names = dist_codes['district_name'].unique()

dist_name = st.selectbox('Select district', dist_names)
dist_id = dist_codes[dist_codes['district_name']==dist_name]['district_id'].iloc[0]
date = st.date_input('Select date:')
date = date.strftime("%d-%m-%Y")
def find_availability(distr_id, date):
    dates_list = [date]
    mstr = pd.DataFrame(columns = ["center_id"       ,
                                    "Center Name"            ,
                                    "state_name"      ,
                                    "district_name"   ,
                                    "block_name"      ,
                                    "pincode"         ,
                                    "lat"             ,
                                    "long"            ,
                                    "from"            ,
                                    "to"              ,
                                    "fee_type"        ,
                                    "vaccine_fees"    ,
                                    "session_id"         ,
                                    "date"               ,
                                    "available_capacity" ,
                                    "min_age_limit"      ,
                                    "vaccine"            ,
                                    "slots"    ])
    
    for INP_DATE in dates_list:
        URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(distr_id, INP_DATE)
        response = requests.get(URL)
        if response.ok:
            resp_json = response.json()

        for center in resp_json["centers"]:
          for session in center["sessions"]:

            mstr = mstr.append({
                   "center_id"     : center["center_id"      ],
                   "Center Name"          : center["name"           ],
                   "state_name"    : center["state_name"     ],
                   "district_name" : center["district_name"  ],
                   "block_name"    : center["block_name"     ],
                   "pincode"       : center["pincode"        ],
                   "lat"           : center["lat"            ],
                   "long"          : center["long"           ],
                   "from"          : center["from"           ],
                   "to"            : center["to"             ],
                   "fee_type"      : center["fee_type"   ], 
                   "session_id"         : session["session_id"           ], 
                   "date"               : session["date"                 ],
                   "available_capacity" : session["available_capacity"   ],
                   "min_age_limit"      : session["min_age_limit"        ],
                   "vaccine"            : session["vaccine"              ],
                   "slots"              : session["slots"                ]
                    }, ignore_index = True)
    return mstr.loc[mstr.astype(str).drop_duplicates().index]
res = find_availability(dist_id,date)

age_limit = st.selectbox('Select Age Group',res.min_age_limit.unique())
df = res[res.min_age_limit==age_limit]

#pincode = st.selectbox('',df.pincode.unique())
#df = df[df.pincode==pincode]

block_name = st.selectbox('Select Area',['All']+list(df.block_name.unique()))
if block_name!='All':
    df = df[df.block_name==block_name]
    
center_name = st.selectbox('Select Center Name',['All']+list(df['Center Name'].unique()))
if center_name!='All':
    df = df[df['Center Name']==center_name]
    
df1 = pd.DataFrame(df['slots'].to_list(), columns=['slot1','slot2', 'slot3', 'slot4'])
df.drop(['slots'],axis=1,inplace=True)
df.reset_index(drop=True,inplace=True)
df = pd.concat([df,df1],axis=1)
st.dataframe(df)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc

st.markdown(get_table_download_link(df), unsafe_allow_html=True)
