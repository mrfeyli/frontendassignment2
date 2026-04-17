import streamlit as st
import requests

# Konfigurera sidans utseende
st.set_page_config(page_title="HR Attrition Predictor", layout="wide")

st.title("🏃‍♂️ HR Attrition Prediction API")
st.write("Fyll i medarbetarens uppgifter nedan för att förutsäga risken för att personen slutar (Attrition).")

# --- INSTÄLLNINGAR ---
# Här definierar vi URL:en till din AWS-instans
API_URL = "http://13.62.6.30:8000"

# --- FORMULÄR FÖR INPUT ---
with st.form("prediction_form"):
    st.subheader("Medarbetardata")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Personlig information & Erfarenhet**")
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced"])
        education = st.selectbox("Education (1-5)", [1, 2, 3, 4, 5])
        education_field = st.selectbox("Education Field", ["Life Sciences", "Medical", "Marketing", "Technical Degree", "Human Resources", "Other"])
        num_companies_worked = st.number_input("Num Companies Worked", min_value=0, max_value=10, value=1)
        total_working_years = st.number_input("Total Working Years", min_value=0, max_value=40, value=10)
        distance_from_home = st.number_input("Distance From Home", min_value=1, max_value=30, value=5)

    with col2:
        st.markdown("**Roll & Kompensation**")
        department = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources"])
        job_role = st.selectbox("Job Role", ["Sales Executive", "Research Scientist", "Laboratory Technician", "Manufacturing Director", "Healthcare Representative", "Manager", "Sales Representative", "Research Director", "Human Resources"])
        monthly_income = st.number_input("Monthly Income", min_value=1000, max_value=20000, value=5000)
        daily_rate = st.number_input("Daily Rate", min_value=100, max_value=1500, value=800)
        hourly_rate = st.number_input("Hourly Rate", min_value=30, max_value=100, value=60)
        monthly_rate = st.number_input("Monthly Rate", min_value=2000, max_value=30000, value=15000)
        percent_salary_hike = st.number_input("Percent Salary Hike", min_value=11, max_value=25, value=15)
        over_time = st.selectbox("OverTime", ["Yes", "No"])
        business_travel = st.selectbox("Business Travel", ["Travel_Rarely", "Travel_Frequently", "Non-Travel"])

    with col3:
        st.markdown("**Nöjdhet & Tid på företaget**")
        job_satisfaction = st.selectbox("Job Satisfaction (1-4)", [1, 2, 3, 4])
        environment_satisfaction = st.selectbox("Environment Satisfaction (1-4)", [1, 2, 3, 4])
        relationship_satisfaction = st.selectbox("Relationship Satisfaction (1-4)", [1, 2, 3, 4])
        job_involvement = st.selectbox("Job Involvement (1-4)", [1, 2, 3, 4])
        work_life_balance = st.selectbox("Work Life Balance (1-4)", [1, 2, 3, 4])
        performance_rating = st.selectbox("Performance Rating (3-4)", [3, 4])
        training_times_last_year = st.number_input("Training Times Last Year", min_value=0, max_value=6, value=3)
        years_at_company = st.number_input("Years At Company", min_value=0, max_value=40, value=5)
        years_in_current_role = st.number_input("Years In Current Role", min_value=0, max_value=20, value=3)
        years_since_last_promotion = st.number_input("Years Since Last Promotion", min_value=0, max_value=15, value=1)
        years_with_curr_manager = st.number_input("Years With Curr Manager", min_value=0, max_value=20, value=2)

    st.markdown("---")
    model_choice = st.radio("🧠 Välj modell för prediktion", ["Advanced MLP (PyTorch)", "LightGBM (Tree)"])
    
    submitted = st.form_submit_button("Analysera risk för Attrition")

# --- LOGIK FÖR ATT SKICKA DATA TILL FASTAPI ---
if submitted:
    payload = {
        "Age": age, "BusinessTravel": business_travel, "DailyRate": daily_rate,
        "Department": department, "DistanceFromHome": distance_from_home,
        "Education": education, "EducationField": education_field,
        "EnvironmentSatisfaction": environment_satisfaction, "Gender": gender,
        "HourlyRate": hourly_rate, "JobInvolvement": job_involvement,
        "JobRole": job_role, "JobSatisfaction": job_satisfaction,
        "MaritalStatus": marital_status, "MonthlyIncome": monthly_income,
        "MonthlyRate": monthly_rate, "NumCompaniesWorked": num_companies_worked,
        "OverTime": over_time, "PercentSalaryHike": percent_salary_hike,
        "PerformanceRating": performance_rating, "RelationshipSatisfaction": relationship_satisfaction,
        "TotalWorkingYears": total_working_years, "TrainingTimesLastYear": training_times_last_year,
        "WorkLifeBalance": work_life_balance, "YearsAtCompany": years_at_company,
        "YearsInCurrentRole": years_in_current_role, "YearsSinceLastPromotion": years_since_last_promotion,
        "YearsWithCurrManager": years_with_curr_manager
    }

    # Bestäm endpoint
    endpoint = "/predict/mlp" if "MLP" in model_choice else "/predict/tree"
    
    with st.spinner("Ansluter till AWS och beräknar..."):
        try:
            # Här använder vi nu variabeln API_URL som vi definierade högst upp
            full_url = f"{API_URL}{endpoint}"
            response = requests.post(full_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result["prediction"].upper()
                probability = result["probability"] * 100
                
                if prediction == "YES":
                    st.error(f"⚠️ Risk för Attrition: **{prediction}**")
                else:
                    st.success(f"✅ Risk för Attrition: **{prediction}**")
                    
                st.info(f"Sannolikhet: **{probability:.2f}%**")
            else:
                st.error(f"Fel från API: {response.status_code}")
                st.write(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error(f"🚨 Kunde inte ansluta till servern på {API_URL}")
            st.info("Tips: Kontrollera att din AWS EC2-instans körs och att port 8000 är öppen i Security Groups.")
