import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Performance KPIs", page_icon=":bar_chart:")

st.title('Performance KPI')

DATA_URL = './demo.csv'
DATE_COLUMN = 'cv_sent_dt'
KPI = [ 'cv_to_interv', 'interv_to_offer', 'offer_to_place']

def date_diff(first, later):
    return (later-first).dt.days


def filter_df(df, filter, filter_val, col_list):
    df_new = df[df[filter]==filter_val]
    df_new = df_new[col_list]

    return df_new 


def column_df(df, col_list):
    df_new = df[col_list]

    return df_new


def avg_groupby(df, groupby):
    df_new = df.groupby(groupby).mean().reset_index()
    df_new = df_new.set_index(groupby)

    return df_new


# https://www.geeksforgeeks.org/create-a-new-column-in-pandas-dataframe-based-on-the-existing-columns/?ref=lbp
data = pd.read_csv(DATA_URL, delimiter=';', )

data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN]).dt.date
data['cl_interview_dt'] = pd.to_datetime(data['cl_interview_dt']).dt.date
data['cl_job_offer_dt'] = pd.to_datetime(data['cl_job_offer_dt']).dt.date
data['placement_dt'] = pd.to_datetime(data['placement_dt']).dt.date

# calc timing in days
data['cv_to_interv'] = date_diff(data['cv_sent_dt'], data['cl_interview_dt']).round(2)
data['interv_to_offer'] = date_diff(data['cl_interview_dt'], data['cl_job_offer_dt']).round(2)
data['offer_to_place'] = date_diff(data['cl_job_offer_dt'], data['placement_dt']).round(2)

# Company Performance KPI
cv_avg_all = data.cv_to_interv.mean().round(2)
interv_avg_all = data.interv_to_offer.mean().round(2)
offer_avg_all = data.offer_to_place.mean().round(2)




# PersB Performance KPI - DataFrame auf gewählten PersB gefiltert
# data auf PARAM PersB filtern
st.sidebar.subheader('Personalberater:in wählen')
persb = st.sidebar.selectbox('Wessen Daten möchten Sie sehen?', data.persb_id.unique())
st.sidebar.write(persb, ' ausgewählt')
persb_data_KPI = ['job_id'] + KPI
persb_data = filter_df(data, 'persb_id', persb, persb_data_KPI)


cv_avg = persb_data.cv_to_interv.mean().round(2)
interv_avg = persb_data.interv_to_offer.mean().round(2)
offer_avg = persb_data.offer_to_place.mean().round(2)
cv_delta = (cv_avg_all - cv_avg).round(2)
interv_delta = (interv_avg_all - interv_avg).round(2)
offer_delta = (offer_avg_all - offer_avg).round(2)

st.header(f'Hallo {persb}, deine KPIs heute:')
cv_interv, interv_offer, cv_offer = st.columns(3)
cv_interv.metric("CV to Interview", cv_avg, cv_delta)
interv_offer.metric("Interview to Offer", interv_avg, interv_delta)
cv_offer.metric("Offer to Placement", offer_avg, offer_delta)

# Personal
# Chart Consultant
st.subheader('KPI deiner offenen Jobs:')

# dein bester Job
persb_jobs = avg_groupby(persb_data, 'job_id')
min_job = persb_jobs.cv_to_interv.min()
st.sidebar.success(f'Dein schnellster CV to Interview hat {min_job} Tage gedauert!')
if st.sidebar.button('High 5!!'):
    st.balloons()

st.bar_chart(persb_jobs)

with st.expander("Details anzeigen"):
    st.dataframe(persb_jobs.style.highlight_max(axis=0).format("{:.2}"))


# Company
# https://docs.streamlit.io/library/api-reference/data/st.metric
st.subheader('Die KPIs der Firma - wo hast du noch Potential?')
cv_interv_all, interv_offer_all, cv_offer_all = st.columns(3)
cv_interv_all.metric("CV to Interview", cv_avg_all, (-cv_delta))
interv_offer_all.metric("Interview to Offer", interv_avg_all, (-interv_delta))
cv_offer_all.metric("Offer to Placement", offer_avg_all, (-offer_delta))


# Chart - Overall
st.subheader("Übersicht nach Standorten")
office_jobs = column_df(data,['persb_loc', 'offer_to_place', 'interv_to_offer', 'cv_to_interv'])
office_jobs = avg_groupby(office_jobs, 'persb_loc')
# https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart
st.bar_chart(office_jobs)
st.dataframe(office_jobs.style.highlight_min(axis=0).format("{:.2}"))

st.subheader("Details zum Standort")
persb_loc = st.selectbox('Welche Standorte möchtest du sehen?', data.persb_loc.unique())
job_loc_by_kpi = ['job_loc'] + KPI
job_loc_by = filter_df(data, 'persb_loc', persb_loc, job_loc_by_kpi)
job_loc_by.set_index('job_loc', inplace=True)
avg_job_loc = job_loc_by.groupby('job_loc').mean()

st.subheader(f"{persb_loc} sucht Job in den Städten:")
st.dataframe(avg_job_loc.style.format("{:.2}"))

st.subheader(f"Berufserfahrung der Kandidaten am Standort {persb_loc}")
job_loc_exp = filter_df(data, 'persb_loc', persb_loc, ['job_loc', 'candidate_lvl'])
job_loc_exp.set_index('job_loc', inplace=True)
job_loc_exp = job_loc_exp.drop_duplicates() 
job_loc_exp




# ---------- HIDE STREAMLIT COMPONENTS ----------#
hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """

st.markdown(hide_st_style, unsafe_allow_html=True)