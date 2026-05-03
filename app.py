import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0a0e1a; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b27 100%);
        border-right: 1px solid #21262d;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #161b27 0%, #1c2333 100%);
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #58a6ff;
        margin: 8px 0 4px 0;
    }
    
    .kpi-label {
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-delta {
        font-size: 0.75rem;
        color: #3fb950;
        margin-top: 4px;
    }

    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e6edf3;
        padding: 8px 0;
        border-bottom: 2px solid #21262d;
        margin-bottom: 16px;
    }

    .insight-box {
        background: linear-gradient(135deg, #0d1117, #161b27);
        border: 1px solid #30363d;
        border-left: 4px solid #58a6ff;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 8px 0;
        color: #c9d1d9;
        font-size: 0.9rem;
    }

    .upload-box {
        background: linear-gradient(135deg, #161b27, #1c2333);
        border: 2px dashed #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #8b949e;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #161b27 0%, #1c2333 100%);
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 16px 20px;
    }

    h1, h2, h3 { color: #e6edf3 !important; }
    p { color: #8b949e; }

    .stSelectbox, .stMultiSelect { color: #e6edf3; }
    
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👥 HR Analytics")
    st.markdown("---")

    # CSV Upload
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader("Upload HR CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} records")
    else:
        df = pd.read_csv("hr_data.csv")
        st.info("📊 Using IBM HR Dataset")

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    dept_filter = st.multiselect(
        "Department",
        options=sorted(df["Department"].unique()),
        default=sorted(df["Department"].unique())
    )

    gender_filter = st.multiselect(
        "Gender",
        options=df["Gender"].unique(),
        default=df["Gender"].unique()
    )

    attrition_filter = st.multiselect(
        "Attrition Status",
        options=df["Attrition"].unique(),
        default=df["Attrition"].unique()
    )

    age_range = st.slider(
        "Age Range",
        min_value=int(df["Age"].min()),
        max_value=int(df["Age"].max()),
        value=(int(df["Age"].min()), int(df["Age"].max()))
    )

    st.markdown("---")
    st.markdown("<small style='color:#8b949e'>IBM HR Analytics Dataset<br>1,470 Employee Records</small>", unsafe_allow_html=True)

# ─── FILTER DATA ───────────────────────────────────────────
filtered_df = df[
    (df["Department"].isin(dept_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["Attrition"].isin(attrition_filter)) &
    (df["Age"].between(age_range[0], age_range[1]))
]

# ─── HEADER ────────────────────────────────────────────────
st.markdown("# 👥 HR Analytics Dashboard")
st.markdown("<p style='color:#8b949e'>IBM HR Employee Attrition & Performance Intelligence Platform</p>", unsafe_allow_html=True)
st.markdown("---")

# ─── KPI CARDS ─────────────────────────────────────────────
total = len(filtered_df)
attr_count = len(filtered_df[filtered_df["Attrition"] == "Yes"])
attr_rate = round((attr_count / total) * 100, 1) if total > 0 else 0
avg_salary = round(filtered_df["MonthlyIncome"].mean(), 0)
avg_age = round(filtered_df["Age"].mean(), 1)
avg_tenure = round(filtered_df["YearsAtCompany"].mean(), 1)
avg_satisfaction = round(filtered_df["JobSatisfaction"].mean(), 2)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("👥 Total Employees", f"{total:,}")
with col2:
    st.metric("🚪 Attrition Rate", f"{attr_rate}%", delta=f"-{round(attr_rate-16,1)}% vs avg", delta_color="inverse")
with col3:
    st.metric("💰 Avg Monthly Income", f"${avg_salary:,.0f}")
with col4:
    st.metric("🎂 Average Age", f"{avg_age} yrs")
with col5:
    st.metric("⭐ Avg Satisfaction", f"{avg_satisfaction}/4")

st.markdown("---")

# ─── ROW 1: ATTRITION ──────────────────────────────────────
st.markdown("### 📉 Attrition Analysis")
col1, col2, col3 = st.columns([2, 2, 1.5])

with col1:
    dept_attr = filtered_df.groupby(["Department", "Attrition"]).size().reset_index(name="Count")
    fig = px.bar(dept_attr, x="Department", y="Count", color="Attrition",
                 barmode="group", title="Attrition by Department",
                 color_discrete_map={"Yes": "#f85149", "No": "#238636"})
    fig.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#161b27",
        font_color="#c9d1d9", title_font_color="#e6edf3",
        legend=dict(bgcolor="#0d1117"),
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d")
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    filtered_df["AgeGroup"] = pd.cut(filtered_df["Age"],
                                      bins=[18, 25, 35, 45, 60],
                                      labels=["18-25", "26-35", "36-45", "46-60"])
    age_attr = filtered_df.groupby(["AgeGroup", "Attrition"]).size().reset_index(name="Count")
    fig2 = px.bar(age_attr, x="AgeGroup", y="Count", color="Attrition",
                  barmode="group", title="Attrition by Age Group",
                  color_discrete_map={"Yes": "#f85149", "No": "#238636"})
    fig2.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#161b27",
        font_color="#c9d1d9", title_font_color="#e6edf3",
        legend=dict(bgcolor="#0d1117"),
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d")
    )
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    attr_pie = filtered_df["Attrition"].value_counts().reset_index()
    attr_pie.columns = ["Attrition", "Count"]
    fig3 = px.pie(attr_pie, values="Count", names="Attrition",
                  title="Overall Attrition",
                  color_discrete_map={"Yes": "#f85149", "No": "#238636"},
                  hole=0.5)
    fig3.update_layout(paper_bgcolor="#161b27", font_color="#c9d1d9",
                       title_font_color="#e6edf3")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ─── ROW 2: SALARY & PERFORMANCE ───────────────────────────
st.markdown("### 💰 Salary & Performance")
col1, col2 = st.columns(2)

with col1:
    fig4 = px.box(filtered_df, x="Department", y="MonthlyIncome",
                  color="Department", title="Salary Distribution by Department",
                  color_discrete_sequence=["#58a6ff", "#3fb950", "#d29922"])
    fig4.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#161b27",
        font_color="#c9d1d9", title_font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d"),
        showlegend=False
    )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    fig5 = px.scatter(filtered_df, x="YearsAtCompany", y="MonthlyIncome",
                      color="Attrition", title="Tenure vs Salary",
                      color_discrete_map={"Yes": "#f85149", "No": "#58a6ff"},
                      opacity=0.7, size_max=8)
    fig5.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#161b27",
        font_color="#c9d1d9", title_font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d")
    )
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ─── ROW 3: DIVERSITY & SATISFACTION ───────────────────────
st.markdown("### 👫 Diversity & Satisfaction")
col1, col2, col3 = st.columns(3)

with col1:
    gender_counts = filtered_df["Gender"].value_counts().reset_index()
    gender_counts.columns = ["Gender", "Count"]
    fig6 = px.pie(gender_counts, values="Count", names="Gender",
                  title="Gender Distribution", hole=0.5,
                  color_discrete_map={"Male": "#58a6ff", "Female": "#bc8cff"})
    fig6.update_layout(paper_bgcolor="#161b27", font_color="#c9d1d9",
                       title_font_color="#e6edf3")
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    sat_map = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
    filtered_df["SatisfactionLabel"] = filtered_df["JobSatisfaction"].map(sat_map)
    sat_counts = filtered_df["SatisfactionLabel"].value_counts().reset_index()
    sat_counts.columns = ["Satisfaction", "Count"]
    order = ["Low", "Medium", "High", "Very High"]
    sat_counts["Satisfaction"] = pd.Categorical(sat_counts["Satisfaction"], categories=order, ordered=True)
    sat_counts = sat_counts.sort_values("Satisfaction")
    fig7 = px.bar(sat_counts, x="Satisfaction", y="Count",
                  title="Job Satisfaction Levels",
                  color="Satisfaction",
                  color_discrete_sequence=["#f85149", "#d29922", "#58a6ff", "#3fb950"])
    fig7.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#161b27",
        font_color="#c9d1d9", title_font_color="#e6edf3",
        showlegend=False,
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d")
    )
    st.plotly_chart(fig7, use_container_width=True)

with col3:
    edu_map = {1: "Below College", 2: "College", 3: "Bachelor", 4: "Master", 5: "Doctor"}
    filtered_df["EducationLabel"] = filtered_df["Education"].map(edu_map)
    edu_counts = filtered_df["EducationLabel"].value_counts().reset_index()
    edu_counts.columns = ["Education", "Count"]
    fig8 = px.pie(edu_counts, values="Count", names="Education",
                  title="Education Distribution", hole=0.5,
                  color_discrete_sequence=px.colors.sequential.Blues_r)
    fig8.update_layout(paper_bgcolor="#161b27", font_color="#c9d1d9",
                       title_font_color="#e6edf3")
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")

# ─── KEY INSIGHTS ──────────────────────────────────────────
st.markdown("### 🧠 Key Insights")
col1, col2 = st.columns(2)

high_attr_dept = filtered_df[filtered_df["Attrition"]=="Yes"]["Department"].value_counts().idxmax()
high_attr_age = filtered_df[filtered_df["Attrition"]=="Yes"]["AgeGroup"].value_counts().idxmax()
top_salary_dept = filtered_df.groupby("Department")["MonthlyIncome"].mean().idxmax()
low_sat = round(len(filtered_df[filtered_df["JobSatisfaction"]<=2]) / total * 100, 1)

with col1:
    st.markdown(f"""
    <div class='insight-box'>🚨 <b>Highest attrition</b> is in the <b>{high_attr_dept}</b> department — consider targeted retention strategies.</div>
    <div class='insight-box'>👶 <b>Age group {high_attr_age}</b> shows the most attrition — early career employees need better engagement.</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='insight-box'>💰 <b>{top_salary_dept}</b> offers the highest average salary — benchmark other departments against it.</div>
    <div class='insight-box'>😟 <b>{low_sat}%</b> of employees have low/medium satisfaction — a risk factor for future attrition.</div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── PERFORMANCE RATING ────────────────────────────────────
st.markdown("### 🏆 Performance Analysis")
col1, col2 = st.columns(2)

with col1:
    perf = filtered_df.groupby(["Department", "PerformanceRating"]).size().reset_index(name="Count")
    perf["PerformanceRating"] = perf["PerformanceRating"].map({1: "Low", 2: "Good", 3: "Excellent", 4: "Outstanding"})
    fig9 = px.bar(perf, x="Department", y="Count", color="PerformanceRating",
                  title="Performance Rating by Department",
                  barmode="group",
                  color_discrete_sequence=["#f85149", "#d29922", "#58a6ff", "#3fb950"])
    fig9.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#161b27",
        font_color="#c9d1d9", title_font_color="#e6edf3",
        legend=dict(bgcolor="#0d1117"),
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d")
    )
    st.plotly_chart(fig9, use_container_width=True)

with col2:
    jobrole_salary = filtered_df.groupby("JobRole")["MonthlyIncome"].mean().reset_index()
    jobrole_salary = jobrole_salary.sort_values("MonthlyIncome", ascending=True)
    fig10 = px.bar(jobrole_salary, x="MonthlyIncome", y="JobRole",
                   orientation="h", title="Average Salary by Job Role",
                   color="MonthlyIncome",
                   color_continuous_scale="Blues")
    fig10.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#161b27",
        font_color="#c9d1d9", title_font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig10, use_container_width=True)

st.markdown("---")

# ─── HEATMAP ───────────────────────────────────────────────
st.markdown("### 🔥 Correlation Heatmap")
corr_cols = ["Age", "MonthlyIncome", "JobSatisfaction", "YearsAtCompany",
             "PerformanceRating", "WorkLifeBalance", "TotalWorkingYears"]
corr_matrix = filtered_df[corr_cols].corr().round(2)

fig11 = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_cols,
    y=corr_cols,
    colorscale="RdBu",
    zmid=0,
    text=corr_matrix.values,
    texttemplate="%{text}",
    textfont={"size": 11},
    hoverongaps=False
))
fig11.update_layout(
    title="Feature Correlation Matrix",
    paper_bgcolor="#161b27",
    plot_bgcolor="#0d1117",
    font_color="#c9d1d9",
    title_font_color="#e6edf3",
    height=450
)
st.plotly_chart(fig11, use_container_width=True)

st.markdown("---")

# ─── RAW DATA + DOWNLOAD ───────────────────────────────────
st.markdown("### 📋 Raw Data")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"<p style='color:#8b949e'>Showing <b style='color:#58a6ff'>{len(filtered_df)}</b> of <b style='color:#58a6ff'>{len(df)}</b> records based on filters</p>", unsafe_allow_html=True)
with col2:
    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_hr_data.csv",
        mime="text/csv",
        use_container_width=True
    )
with col3:
    st.download_button(
        label="⬇️ Download Full CSV",
        data=df.to_csv(index=False),
        file_name="full_hr_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with st.expander("📋 View Raw Data Table"):
    st.dataframe(
        filtered_df.style.background_gradient(subset=["MonthlyIncome"], cmap="Blues"),
        use_container_width=True
    )

st.markdown("<br><center><small style='color:#8b949e'>HR Analytics Dashboard | IBM HR Dataset | Built with Python & Streamlit</small></center>", unsafe_allow_html=True)