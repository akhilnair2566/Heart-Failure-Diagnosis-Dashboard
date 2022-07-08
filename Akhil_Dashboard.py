import pandas as pd
import plotly.express as px
import streamlit as st
import requests
from streamlit_lottie import st_lottie

# reading csv file
data = pd.read_csv(r"{csv_file_location}")

# replacing the entries in the dataset to make in more readable to us -> changing 0,1 to no,yes etc
data['sex'].replace([0, 1], ['Female', 'Male'], inplace=True)
data['anaemia'].replace([0, 1], ['No', 'Yes'], inplace=True)
data['diabetes'].replace([0, 1], ['No', 'Yes'], inplace=True)
data['high_blood_pressure'].replace([0, 1], ['No', 'Yes'], inplace=True)
data['smoking'].replace([0, 1], ['No', 'Yes'], inplace=True)

# Caltulating age interval from the age feature
data['start-interval'] = (data['age']//10)*10+1
data['start-interval'].replace([1, 11, 21, 31, 41, 51, 61, 71, 81, 91], ['1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100'], inplace=True)

# The tab icon is obtained from this website:
# https://www.webfx.com/tools/emoji-cheat-sheet/

# Setting the Page configurations like icon tittle etc and making the sidebar to show automatically when the page loads
st.set_page_config(
    page_title="Health",
    initial_sidebar_state="auto",
    page_icon=":heartpulse:",
    layout="wide"
)

# Just for easily accessing the start-interval feature
data['start_interval'] = data['start-interval']

# Sidebar CODE
st.sidebar.header("Side Bar")  #Sidebar header
# Setting default values of Sidebar entities
Start_interval = st.sidebar.multiselect(
    "Select the age-group:",
    options=data["start_interval"].unique(),
    default=data["start_interval"].unique()
)
gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=data["sex"].unique(),
    default=data["sex"].unique()
)
Anaemia = st.sidebar.multiselect(
    "Anaemia (yes or no):",
    options=data["anaemia"].unique(),
    default=data["anaemia"].unique()
)
Diabetes = st.sidebar.multiselect(
    "diabetes (yes or no):",
    options=data["diabetes"].unique(),
    default=data["diabetes"].unique()
)
High_blood_pressure = st.sidebar.multiselect(
    "high_blood_pressure (yes or no):",
    options=data["high_blood_pressure"].unique(),
    default=data["high_blood_pressure"].unique()
)
Smoking = st.sidebar.multiselect(
    "smoking (yes or no):",
    options=data["smoking"].unique(),
    default=data["smoking"].unique()
)

# This query will select the data as per the options selected in the sidebar
# and all the calculations done furthur are made on this data selected.

data_selection = data.query(
    "start_interval == @Start_interval & sex == @gender & anaemia == @Anaemia & diabetes == @Diabetes & high_blood_pressure == @High_blood_pressure & smoking == @Smoking"
)

# This function is used to load the animations from the url for the dashboard.
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Main Page CODE
st.title(":heartpulse: Heart Failure Diagnosis Dashboard") # Sets the tittle of home page
st.markdown("##")  # it is for the line break made to separate it.


# This is for the animations which are loaded from the lottiefile website from url using above load_lottieurl function

left_column, right_column = st.columns(2)
with left_column:
    dashboard1 = load_lottieurl("https://assets10.lottiefiles.com/private_files/lf30_ynpn4ffc.json")
    st_lottie(dashboard1, key="Dashboard1", height=400)
with right_column:
    dashboard2 = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_zw7jo1.json")
    st_lottie(dashboard2, key="Dashboard2", height=400)
# st.dataframe(data_selection)
st.markdown("""---""")

# calculating total deaths occured
total_death = data_selection["deaths"].sum()

# Total heart-failures: total entries in the dataset
total_failures = len(data_selection)

# for showing the values calculted above on the dashboard
left_column, right_column = st.columns(2)   # it make two colums: left and right
with left_column:
    st.subheader("Total Heart Failure Cases registered:") #heading of this column
    st.subheader(f"{total_failures}")
with right_column:
    st.subheader("Total Deaths:")
    st.subheader(f"{total_death:,}")
st.markdown("""---""")

# ejection_fraction_count: no of heart failures registered whose ejection fraction was less than 40%
# It is calculated based on the fact that below 40% is not normal in human bodies
ejection_fraction_count = len(data_selection[data_selection['ejection_fraction'] < 40])

# platelets_count: no. of heart failures registered whose platelets count was not in the ranhe of [150000,450000]
# It is calculated based on the fact that range [150000,450000] is normal in human bodies
platelets_count = len(data_selection[(data_selection['platelets'] < 150000) | (data_selection['platelets'] > 450000)])


left_column, right_column = st.columns(2)
with left_column:
    st.subheader("No. of cases registered having ejection fraction less than 40%:")
    st.subheader(f"{ejection_fraction_count:,}")
with right_column:
    st.subheader("No. of cases registered having abnormal platelets count:")
    st.subheader(f"{platelets_count}")
st.markdown("""---""")



# Calculating total no. of deaths occured in different age-intervals.
age_interval_total_deaths = (
    data_selection.groupby(by=["start_interval"]).sum()[["deaths"]]
)
# Making bar graph of age-interval V/s deaths
age_interval_bar = px.bar(
    age_interval_total_deaths,
    y="deaths",
    x=age_interval_total_deaths.index,
    orientation="v",
    labels={'start_interval':'age-interval'},
    title="<b>No. of Deaths in different age intervals:</b>",
    color_discrete_sequence=["cyan"] * len(age_interval_total_deaths),
    template="plotly_dark"
)
#Making the background of the bar graph transparent and hiding the grid.
age_interval_bar.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# This is for calculating the gender ratio
data1 = data_selection["sex"]
cou = {}
key = []
value = []
# it will form a list describing no. of male and female patients
for i in data1:
    if i in cou and i in key:
        cou[i] += 1
    else:
        cou[i] = 1
        key.append(i)
for i in range(len(key)):
    value.append(cou[key[i]])
# keys will be male ,female and values will be the no. of males and females

# Pie chart describing the ration of males and females
fig_pie = px.pie(
    values=value, #it containes no. of males and females
    names=key,  # it contains male and female
    title="<b>Gender ratio:</b>", #tittle of the pie chart
    hole=0.3
)




# Printing the age-interval bar chart and gender ratio pie chart
left_column, right_column = st.columns(2)
left_column.plotly_chart(age_interval_bar, use_container_width=True)
right_column.plotly_chart(fig_pie, use_container_width=True)
st.markdown("##")


# calculating how many heart failure case were registered in particular years
year_of_heart_failure = data_selection.groupby(by=["year"]).count()

# horizontal bar graph of the no. of cases registered V/s years of registeration
year_bar = px.bar(
    year_of_heart_failure,
    x="deaths",
    y=year_of_heart_failure.index,
    orientation="h",
    labels={'deaths':'No. of heart failures occured'}, #the label is change to our desired label.
    title="<b>Time of Heart Failures:</b>",
    color_discrete_sequence=["cyan"] * len(year_of_heart_failure),
    template="plotly_dark"
)
#Making the background of the bar graph transparent and hiding the grid.
year_bar.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# Plotting the yeaar-Bar describing how many cases registered in particular years
st.plotly_chart(year_bar,use_container_width=True)

st.subheader("No. of deaths registered based on different parameters:")

# Calculating no. of died patients who had anaemia and those who didn't.
anaemia_death = (
    data_selection.groupby(by=["anaemia"]).sum()[["deaths"]]
)


# pie-chart of no. of deaths V/s Does they have anaemia or not
ana_pie = px.pie(
    anaemia_death,
    values="deaths",
    names=anaemia_death.index,
    title="<b>anaemia:</b>",
    hole=0.3
)

# Calculating no. of died patients who had diabetes and those who didn't.
diabetes_death = (
    data_selection.groupby(by=["diabetes"]).sum()[["deaths"]]
)
# Horizontal bar graph of No. of deaths registered V/s on the basis that patient had diabetes or not.
diabetes_bar = px.bar(
    diabetes_death,
    x="deaths",
    y=diabetes_death.index,
    orientation="h",
    title="<b>diabetes:</b>",
    color_discrete_sequence=["cyan"] * len(diabetes_death),
    template="plotly_dark"
)
#Making the background of the bar graph transparent and hiding the grid.
diabetes_bar.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)
# Plotting the charts made above on the dashboard
left_column, right_column = st.columns(2)
left_column.plotly_chart(ana_pie, use_container_width=True)
right_column.plotly_chart(diabetes_bar, use_container_width=True)

# Calculating no. of died patients who had high-blood-pressure and those who didn't.
hbp_death = (
    data_selection.groupby(by=["high_blood_pressure"]).sum()[["deaths"]]
)
# bar graph of No. of deaths registered V/s on the basis that patient had high-blood-pressure or not.
hbp_bar = px.bar(
    hbp_death,
    y="deaths",
    x=hbp_death.index,
    orientation="v",
    title="<b>high_blood_pressure:</b>",
    color_discrete_sequence=["cyan"] * len(hbp_death),
    template="plotly_dark"
)
#Making the background of the bar graph transparent and hiding the grid.
hbp_bar.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)
# Calculating no. of died patients who smoked and those who didn't.
smoking_death = (
    data_selection.groupby(by=["smoking"]).sum()[["deaths"]]
)
#pie-chart of no. of deaths V/s Does they smoked or not
smoking_pie = px.pie(
    smoking_death,
    values="deaths",
    names=smoking_death.index,
    title="<b>Smoking:</b>",
    hole=0.3
)
#plotting the charts made on the dashboard
left_column, right_column = st.columns(2)
left_column.plotly_chart(hbp_bar, use_container_width=True)
right_column.plotly_chart(smoking_pie, use_container_width=True)

st.markdown("##")

# calculating the no of deaths registered on different serum-sodium levels
data3 = data_selection.groupby(by=["serum_sodium"]).sum()[["deaths"]]

#Line graph describing  No. of deaths V/s their serum-sodim levels
fig_line = px.line(
    data3,
    x=data3.index,
    y="deaths",
    orientation="v",
    labels={'serum_sodium':'serum-sodium level'},
    title="<b>Serum Sodium level:</b>"
)
# Making the background transparent
fig_line.update_layout(
    plot_bgcolor="rgba(0,0,0,0)"
)
# plotting the line chart on the dashboard
st.plotly_chart(fig_line, use_container_width=True)



# This code is for removing the MADE FROM STREAMLIT text from the bottom and hidding the top drop down menu which is provided by streamlit library
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
