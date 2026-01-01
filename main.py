# main.py
import streamlit as st
import styles
import content


# 1. Page Configuration
st.set_page_config(
    page_title="StatLab: Statistical Hypothesis Testing", 
    layout="wide",
    page_icon="📈"
)

# 2. Load Styles
styles.load_css()

with st.sidebar:
    st.title("StatLab 🔬")
    st.caption("Professional Statistical Analysis")
    st.markdown("---")
    
    st.markdown("**Created by:**")
    st.markdown("Mohamad Iqbal - Statistika Unpad") 
    st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/mohamad-iqbal-82ab6037a) | [GitHub](https://github.com/mohamadiqbal69)")
    st.markdown("---")

st.sidebar.title("Navigasi")
main_menu = st.sidebar.radio(
    "Go to:",
    ["🏠 Home",  
     "🤖 AI Consultant",
     "📚 Analisis Statistik"]
)

# 3. Routing Logic
if main_menu == "🏠 Home":
    # Hero Section yang lebih profesional
    st.title("Statistical Hypothesis Testing Suite")
    st.markdown("""
    <div style="background-color:#EFF6FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB;">
        <p style="font-size: 1.1rem; color: #1F2937; margin:0;">
            Aplikasi berbasis Python untuk melakukan uji hipotesis parametrik secara presisi. 
            Metodologi mengacu pada buku teks standar <b>"Statistics for Managers Using Microsoft Excel" (Levine et al.)</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🛠️ Fitur Analisis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.container(border=True)
        st.subheader("Uji Proporsi")
        st.markdown(
            """
            Analisis terhadap proporsi sukses dalam populasi (Data Kategorik).
            
            * **Uji Proporsi 1 Sampel**
            * **Uji Proporsi 2 Sampel**
            """
        )

    # Kartu 2: Uji Rata-rata
    with col2:
        st.container(border=True)
        st.subheader("Uji Rata-rata")
        st.markdown(
            """
            Komparasi nilai tengah (mean) populasi (Data Numerik).
            
            * **1 Sampel (Z-test)**
            * **1 Sampel (t-test)**
            * **2 Sampel Independen**
            * **2 Sampel Dependen (Paired)**
            """
        )

    # Kartu 3: Uji Varians
    with col3:
        st.container(border=True)
        st.subheader("Uji Varians") 
        st.markdown(
            """
            Analisis keragaman atau homogenitas data.
            
            * **Uji Kesamaan Varians (F-test)**
            """
        )
    st.markdown("---")
    st.subheader("Implementation Details")
    st.code("Python 3.10+ | Scipy Stats | Streamlit | NumPy", language='text')


elif main_menu == "🤖 AI Consultant":   
    content.load_ai_consultant()
    
elif main_menu == "📚 Analisis Statistik":
    # Menu yang lebih rapi
    menu = st.sidebar.selectbox(
        "Pilih Metode Uji:",
        [
            "--- Pilih Uji ---",
            "Uji Proporsi 1 Sampel",
            "Uji Proporsi 2 Sampel",
            "Uji Rata-rata 1 Sampel (Z-test)",
            "Uji Rata-rata 1 Sampel (t-test)",
            "Uji Rata-rata 2 Sampel Independen (Pooled t-test)",
            "Uji Rata-rata 2 Sampel Independen (Welch t-test)",
            "Uji Rata-rata 2 Sampel Dependen (Paired t-test)",
            "Uji Kesamaan Varians (F-test)"
        ]
    )
    
    if menu == "--- Pilih Uji ---":
        st.info("Silakan pilih jenis uji statistik dari dropdown di sidebar.")
    elif menu == "Uji Proporsi 1 Sampel":
        content.load_uji_proporsi_1_sampel(menu)
    elif menu == "Uji Proporsi 2 Sampel":
        content.load_uji_proporsi_2_sampel(menu)
    elif menu == "Uji Rata-rata 1 Sampel (Z-test)":
        content.load_z_test_1(menu)
    elif menu == "Uji Rata-rata 1 Sampel (t-test)":
        content.load_t_test_1(menu)
    elif menu == "Uji Rata-rata 2 Sampel Independen (Pooled t-test)":
        content.load_pooled_t_test(menu)
    elif menu == "Uji Rata-rata 2 Sampel Independen (Welch t-test)":
        content.load_welch_t_test(menu)
    elif menu == "Uji Rata-rata 2 Sampel Dependen (Paired t-test)":
        content.load_paired_t_test(menu)
    elif menu == "Uji Kesamaan Varians (F-test)":
        content.load_f_test(menu)