# content.py
import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import google.generativeai as genai
import re 


def parse_data(input_text):
    """
    Versi Robust: Menerima pemisah koma, spasi, tab, atau enter.
    Mencegah error jika user memasukkan huruf.
    """
    if not input_text: 
        return None
    
    try:
        clean_text = re.sub(r'[;,\t\n]', ' ', input_text)
        
        data_list = []
        for x in clean_text.split():
            try:
                data_list.append(float(x))
            except ValueError:
                continue 
        
        data = np.array(data_list)
        
        if len(data) == 0:
            st.error("⚠️ Tidak ada angka valid yang ditemukan.")
            return None
            
        return data

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")
        return None


# Pastikan import numpy di atas
# import numpy as np

def get_data_input(label, default_text, key_suffix):
    """
    Versi FIXED: Prioritas Upload File > Input Manual.
    Memperbaiki bug di mana file upload tidak terbaca karena tertimpa input manual.
    """
    st.markdown(f"**Data {label}**")
    
    key_text_area = f"text_{key_suffix}"
    
    # Inisialisasi Session State
    if key_text_area not in st.session_state:
        st.session_state[key_text_area] = default_text

    # --- 1. FITUR SKENARIO DEMO ---
    with st.expander("🎲 Pilih Skenario Demo Data"):
        scenario = st.radio(
            "Ingin hasil uji seperti apa?",
            ["Tolak H0 (Signifikan)", "Gagal Tolak H0 (Tidak Signifikan)"],
            key=f"scen_{key_suffix}"
        )
        
        if st.button(f"Terapkan Skenario ({label})", key=f"btn_{key_suffix}"):
            is_group_2 = any(x in key_suffix for x in ['2', 'post', 'w2', 'f2', 'p2'])
            mu = 50
            sigma = 5
            
            if scenario == "Tolak H0 (Signifikan)":
                if not is_group_2:
                    mu = 80; sigma = 2   
                else:
                    mu = 45; sigma = 10  
            
            new_data = np.random.normal(mu, sigma, 30).round(1)
            st.session_state[key_text_area] = ", ".join(map(str, new_data))
            st.rerun()

    # --- 2. RENDER TABS (TAMPILAN) ---
    tab_manual, tab_upload = st.tabs(["✍️ Input Manual", "📂 Upload File (CSV/Excel)"])
    
    # Variabel penampung input (belum diproses)
    manual_input_str = None
    uploaded_file_obj = None

    # Render Tab Manual
    with tab_manual:
        manual_input_str = st.text_area(
            "Masukkan angka (pemisah spasi/koma):", 
            value=st.session_state[key_text_area],
            key=key_text_area,
            height=100
        )

    # Render Tab Upload
    with tab_upload:
        uploaded_file_obj = st.file_uploader(
            f"Upload CSV/Excel ({label})", 
            type=['csv', 'xlsx', 'xls'], 
            key=f"up_{key_suffix}"
        )

    # --- 3. LOGIKA PEMROSESAN DATA (PRIORITAS) ---
    
    # PRIORITAS 1: Cek apakah ada file yang diupload?
    if uploaded_file_obj is not None:
        try:
            if uploaded_file_obj.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file_obj)
            else:
                df = pd.read_excel(uploaded_file_obj)
            
            # Ambil kolom angka saja
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            
            if not numeric_cols:
                st.error("File tidak memiliki kolom angka.")
                return None
            else:
                col_name = numeric_cols[0]
                data_result = df[col_name].dropna().to_numpy()
                st.success(f"✅ Menggunakan data dari file: {uploaded_file_obj.name} (Kolom: {col_name}, n={len(data_result)})")
                return data_result

        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
            return None

    # PRIORITAS 2: Jika tidak ada file, gunakan Input Manual
    if manual_input_str:
        return parse_data(manual_input_str)
    
    return None

def check_normality(data, label):
    """Melakukan uji Shapiro-Wilk untuk asumsi normalitas."""
    if len(data) < 3:
        st.warning(f"⚠️ Data {label} terlalu sedikit untuk uji normalitas.")
        return True 
        
    stat, p = stats.shapiro(data)
    alpha = 0.05
    
    if p > alpha:
        st.success(f"✅ Asumsi Normalitas Terpenuhi ({label})\n(Shapiro-Wilk p={p:.4f} > 0.05)")
        return True
    else:
        st.warning(f"⚠️ Asumsi Normalitas TIDAK Terpenuhi ({label})\n(Shapiro-Wilk p={p:.4f} < 0.05). Hasil mungkin bias jika n < 30.")
        return False


def calculate_cohens_d(d1, d2):
    """Menghitung Effect Size (Cohen's d)."""
    n1, n2 = len(d1), len(d2)
    s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
    s_pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    
    if s_pooled == 0: return 0
    return (np.mean(d1) - np.mean(d2)) / s_pooled


def interpret_effect_size(d):
    d = abs(d)
    if d < 0.2: return "Sangat Kecil (Negligible)"
    elif d < 0.5: return "Kecil (Small)"
    elif d < 0.8: return "Sedang (Medium)"
    else: return "Besar (Large)"


def plot_distribution(dist_name, stat_val, crit_val, alpha, test_type, df1=None, df2=None):
    fig, ax = plt.subplots(figsize=(10, 4))
    
    if dist_name == 'normal':
        limit = max(4, abs(stat_val) + 1, abs(crit_val) + 1)
        x = np.linspace(-limit, limit, 1000)
        y = stats.norm.pdf(x, 0, 1)
        label_dist = 'Distribusi Normal Standar (Z)'
    elif dist_name == 't':
        limit = max(4, abs(stat_val) + 1, abs(crit_val) + 1)
        x = np.linspace(-limit, limit, 1000)
        y = stats.t.pdf(x, df1)
        label_dist = f'Distribusi t (df={df1:.2f})'
    elif dist_name == 'f':
        limit = max(5, stat_val + 2, crit_val + 2)
        x = np.linspace(0, limit, 1000)
        y = stats.f.pdf(x, df1, df2)
        label_dist = f'Distribusi F (df1={df1}, df2={df2})'
    
    ax.plot(x, y, label=label_dist, color='#2563EB', linewidth=2)
    ax.fill_between(x, y, alpha=0.1, color='#2563EB')


    type_lower = test_type.lower()
    
    if dist_name in ['normal', 't']:
        crit = abs(crit_val)
        if "two" in type_lower or "dua" in type_lower:
            ax.fill_between(x, y, where=(x <= -crit), color='#EF4444', alpha=0.5, label='Daerah Penolakan')
            ax.fill_between(x, y, where=(x >= crit), color='#EF4444', alpha=0.5)
            ax.axvline(-crit, color='red', linestyle=':')
            ax.axvline(crit, color='red', linestyle=':')
        elif "right" in type_lower or "kanan" in type_lower:
            ax.fill_between(x, y, where=(x >= crit_val), color='#EF4444', alpha=0.5, label='Daerah Penolakan')
            ax.axvline(crit_val, color='red', linestyle=':')
        elif "left" in type_lower or "kiri" in type_lower:
            ax.fill_between(x, y, where=(x <= crit_val), color='#EF4444', alpha=0.5, label='Daerah Penolakan')
            ax.axvline(crit_val, color='red', linestyle=':')
            
    elif dist_name == 'f':
        ax.fill_between(x, y, where=(x >= crit_val), color='#EF4444', alpha=0.5, label='Daerah Penolakan')
        ax.axvline(crit_val, color='red', linestyle=':')

    ax.axvline(stat_val, color='#10B981', linestyle='--', linewidth=2.5, label=f'Statistik Hitung ({stat_val:.2f})')
    
    ax.set_title("Visualisasi Daerah Keputusan")
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)

def display_test_result(stat_val, crit_val, p_val, alpha, test_type, model_label='Z', reject=False, dist_name='normal', df1=None, df2=None):
    st.markdown("---")
    st.subheader("📊 Hasil Perhitungan Statistik")

    c1, c2, c3 = st.columns(3)
    c1.metric(f"{model_label}-Hitung", f"{stat_val:.4f}")
    c2.metric("Critical Value", f"{crit_val:.4f}")
    c3.metric("P-Value", f"{p_val:.5f}", delta_color="inverse")

    plot_distribution(dist_name, stat_val, crit_val, alpha, test_type, df1, df2)

    st.markdown("### 📝 Kesimpulan")
    if reject:
        st.error(f"**Keputusan: Tolak H0** (Signifikan)")
        st.write(f"Karena P-Value ({p_val:.5f}) < Alpha ({alpha}), maka kita memiliki cukup bukti untuk menolak Hipotesis Nol.")
    else:
        st.success(f"**Keputusan: Gagal Tolak H0** (Tidak Signifikan)")
        st.write(f"Karena P-Value ({p_val:.5f}) > Alpha ({alpha}), maka bukti belum cukup untuk menolak Hipotesis Nol.")

def load_ai_consultant():
    st.header("🤖 AI Statistical Consultant")
    
    st.markdown("""
    <div style="background-color:#F0F9FF; padding:20px; border-radius:10px; border-left:5px solid #0284C7; margin-bottom: 20px;">
        <h4 style="color:#0369A1; margin-top:0;">Bingung Memilih Uji Statistik?</h4>
        <p style="color:#334155; margin-bottom:0;">
            Ceritakan masalah penelitian Anda. AI akan menganalisis berdasarkan buku Levine.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        has_valid_key = True
        st.caption("✅ Terhubung menggunakan System API Key")
    else:
        try:
            import os
            if os.environ.get("GEMINI_API_KEY"):
                api_key = os.environ.get("GEMINI_API_KEY")
                has_valid_key = True
            else:
                api_key = st.text_input("🔑 Masukkan Google Gemini API Key:", type="password")
                has_valid_key = bool(api_key)
        except:
             api_key = st.text_input("🔑 Masukkan Google Gemini API Key:", type="password")
             has_valid_key = bool(api_key)

    user_case = st.text_area("📝 Deskripsikan Studi Kasus Anda:", height=150)

    if st.button("🔍 Analisis Kasus", type="primary"):
        if not has_valid_key:
            st.error("⚠️ API Key tidak ditemukan.")
            return
        
        if not user_case:
            st.warning("⚠️ Mohon tuliskan deskripsi kasus Anda.")
            return

        try:
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('models/gemini-2.5-flash') 
            
            system_prompt = f"""
            Kamu adalah Asisten Ahli Statistik (Metode Levine).
            Tugas: Pilih SATU uji statistik yang tepat untuk kasus user dari daftar ini:
            1. Uji Proporsi 1 Sampel
            2. Uji Proporsi 2 Sampel
            3. Uji Rata-rata 1 Sampel (Z-test)
            4. Uji Rata-rata 1 Sampel (t-test)
            5. Uji Rata-rata 2 Sampel Independen (Pooled t-test)
            6. Uji Rata-rata 2 Sampel Independen (Welch t-test)
            7. Uji Rata-rata 2 Sampel Dependen (Paired t-test)
            8. Uji Kesamaan Varians (F-test)
            
            KASUS USER: "{user_case}"
            
            Jawab dengan format Markdown:
            1. **Rekomendasi Uji**: [Nama Uji]
            2. **Alasan**: [Penjelasan singkat]
            3. **Langkah**: Pilih menu [Nama Menu] di sidebar.
            """
            
            with st.spinner("🤖 AI sedang berpikir..."):
                response = model.generate_content(system_prompt)
                st.markdown("---")
                st.subheader("💡 Hasil Analisis")
                st.markdown(response.text)
                st.success("✅ Silakan pilih uji tersebut di menu sidebar.")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.info("Tips: Pastikan API Key benar. Jika error model 404, coba update library 'google-generativeai'.")

def load_home():
    pass 


def load_uji_proporsi_1_sampel(title):
    st.header(title)
    with st.expander("📘 Penjelasan & Rumus (Levine Ch. 9.4)", expanded=False):
        st.write("""
        **Z-Test for the Proportion (One Sample)**
        
        Uji ini digunakan untuk menentukan apakah proporsi populasi ($p$ atau $\pi$) berbeda dari nilai standar atau historis tertentu ($\pi_0$).
        
        **Asumsi (Levine Ch. 9.4):**
        1. Data yang dipilih adalah sampel acak.
        2. Sampel independen satu sama lain.
        3. Jumlah item (n) cukup besar sehingga $n\pi \ge 5$ dan $n(1-\pi) \ge 5$, sehingga distribusi normal dapat digunakan sebagai pendekatan distribusi binomial.
        """)
        st.latex(r"Z_{STAT} = \frac{p - \pi}{\sqrt{\frac{\pi(1-\pi)}{n}}}")
        st.write("""
        Dimana:
        * $p = X/n$ (Proporsi Sampel)
        * $\pi$ = Proporsi Hipotesis (Populasi)
        * $n$ = Ukuran Sampel
        """)

    c1, c2 = st.columns(2)
    with c1:
        x = st.number_input("Jumlah Sukses (X)", min_value=0, value=40)
        n = st.number_input("Jumlah Sampel (n)", min_value=1, value=100)
    with c2:
        pi0 = st.number_input("Proporsi Hipotesis (π)", 0.0, 1.0, 0.5)
        alpha = st.number_input("Alpha (α)", 0.001, 0.20, 0.05)
    
    jenis_uji = st.selectbox("Jenis Uji", ("Two-sided (Dua Arah)", "Right-sided (Uji Kanan)", "Left-sided (Uji Kiri)"))

    if st.button("Hitung Z Proporsi"):
        p_hat = x / n
        denom = np.sqrt((pi0 * (1 - pi0)) / n)
        
        if n*pi0 < 5 or n*(1-pi0) < 5:
            st.warning("⚠️ Peringatan: Asumsi nπ ≥ 5 atau n(1-π) ≥ 5 mungkin tidak terpenuhi.")

        z_score = (p_hat - pi0) / denom
        
        if "Two" in jenis_uji:
            z_crit = stats.norm.ppf(1 - alpha/2)
            p_val = 2 * (1 - stats.norm.cdf(abs(z_score)))
            reject = abs(z_score) > z_crit
        elif "Right" in jenis_uji:
            z_crit = stats.norm.ppf(1 - alpha)
            p_val = 1 - stats.norm.cdf(z_score)
            reject = z_score > z_crit
        else:
            z_crit = stats.norm.ppf(alpha)
            p_val = stats.norm.cdf(z_score)
            reject = z_score < z_crit

        st.info(f"Proporsi Sampel (p) = {p_hat:.4f}")
        display_test_result(z_score, z_crit, p_val, alpha, jenis_uji, 'Z', reject, 'normal')

def load_uji_proporsi_2_sampel(title):
    st.header(title)
    with st.expander("📘 Penjelasan & Rumus (Levine Ch. 10.3)", expanded=False):
        st.write("""
        **Z-Test for the Difference Between Two Proportions**
        
        Uji ini digunakan untuk menguji apakah terdapat perbedaan yang signifikan antara proporsi dua populasi independen.
        
        **Asumsi:**
        1. Sampel diambil secara acak dan independen dari dua populasi.
        2. $n\pi \ge 5$ dan $n(1-\pi) \ge 5$ untuk kedua kelompok.
        """)
        st.latex(r"Z_{STAT} = \frac{p_1 - p_2}{\sqrt{\bar{p}(1-\bar{p})\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}}")
        st.write("Dimana $\\bar{p}$ (pooled proportion) adalah:")
        st.latex(r"\bar{p} = \frac{X_1 + X_2}{n_1 + n_2}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Sampel 1**")
        x1 = st.number_input("Sukses (X1)", 0, value=150)
        n1 = st.number_input("Total (n1)", 1, value=200)
    with c2:
        st.markdown("**Sampel 2**")
        x2 = st.number_input("Sukses (X2)", 0, value=162)
        n2 = st.number_input("Total (n2)", 1, value=300)
        
    alpha = st.number_input("Alpha", 0.01, 0.2, 0.05)
    jenis_uji = st.selectbox("Jenis Uji", ("Two-sided", "Right-sided", "Left-sided"))

    if st.button("Hitung Z Proporsi 2 Sampel"):
        p1, p2 = x1/n1, x2/n2
        p_pool = (x1 + x2) / (n1 + n2)
        denom = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        z_score = (p1 - p2) / denom
        
        if "Two" in jenis_uji:
            z_crit = stats.norm.ppf(1 - alpha/2)
            p_val = 2 * (1 - stats.norm.cdf(abs(z_score)))
            reject = abs(z_score) > z_crit
        elif "Right" in jenis_uji:
            z_crit = stats.norm.ppf(1 - alpha)
            p_val = 1 - stats.norm.cdf(z_score)
            reject = z_score > z_crit
        else:
            z_crit = stats.norm.ppf(alpha)
            p_val = stats.norm.cdf(z_score)
            reject = z_score < z_crit
            
        st.info(f"Selisih Proporsi: {p1-p2:.4f}")
        display_test_result(z_score, z_crit, p_val, alpha, jenis_uji, 'Z', reject, 'normal')


def load_z_test_1(title):
    st.header(title)
    with st.expander("📘 Penjelasan & Rumus (Z-Test)", expanded=False):
        st.write("""
        **One-sample Z-test** digunakan untuk menentukan apakah rata-rata populasi ($\mu$) berbeda secara signifikan dari nilai hipotesis ($\mu_0$).
        
        **Syarat Penggunaan:**
        1. **Simpangan Baku Populasi ($\sigma$) Diketahui.**
        2. Data Berdistribusi Normal atau $n \ge 30$.
        """)
        st.latex(r"Z_{STAT} = \frac{\bar{x} - \mu_0}{\sigma / \sqrt{n}}")
    
    mu0 = st.number_input("Rata-rata Hipotesis (μ0)", value=0.0)
    sigma = st.number_input("Simpangan Baku Populasi (σ)", value=1.0)
    alpha = st.number_input("Alpha", 0.05)
    jenis_uji = st.selectbox("Jenis Uji", ("Two-sided", "Right-sided", "Left-sided"))
    
    data = get_data_input("Sampel", "10, 12, 11, 14, 13", "z1")

    if st.button("Hitung Z-Test"):
        if data is not None:
            n = len(data)
            xbar = np.mean(data)
            z_score = (xbar - mu0) / (sigma / np.sqrt(n))
            
            if "Two" in jenis_uji:
                z_crit = stats.norm.ppf(1 - alpha/2)
                p_val = 2 * (1 - stats.norm.cdf(abs(z_score)))
                reject = abs(z_score) > z_crit
            elif "Right" in jenis_uji:
                z_crit = stats.norm.ppf(1 - alpha)
                p_val = 1 - stats.norm.cdf(z_score)
                reject = z_score > z_crit
            else:
                z_crit = stats.norm.ppf(alpha)
                p_val = stats.norm.cdf(z_score)
                reject = z_score < z_crit

            st.info(f"Mean Sampel: {xbar:.4f}")
            display_test_result(z_score, z_crit, p_val, alpha, jenis_uji, 'Z', reject, 'normal')

def load_t_test_1(title):
    st.header(title)
    with st.expander("📘 Penjelasan & Rumus (Levine Ch. 9.2)", expanded=False):
        st.write("""
        **t-Test for the Mean (Sigma Unknown)**
        
        Digunakan ketika deviasi standar populasi ($\sigma$) tidak diketahui. Statistik uji mengikuti distribusi t Student dengan derajat kebebasan $n-1$.
        """)
        st.latex(r"t_{STAT} = \frac{\bar{X} - \mu}{S / \sqrt{n}}")
        st.write("df (Derajat Kebebasan) = $n - 1$")
    
    mu0 = st.number_input("Rata-rata Hipotesis (μ0)", value=50.0)
    alpha = st.number_input("Alpha", 0.05)
    jenis_uji = st.selectbox("Jenis Uji", ("Two-sided", "Right-sided", "Left-sided"), key='type_t1')
    
    data = get_data_input("Sampel", "52, 55, 49, 58, 54, 51", "t1")

    if st.button("Hitung t-Test"):
        if data is not None and len(data) > 1:
            check_normality(data, "Sampel") 
            
            n = len(data)
            x_bar = np.mean(data)
            s = np.std(data, ddof=1)
            t_stat = (x_bar - mu0) / (s / np.sqrt(n))
            df = n - 1
            
            if "Two" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha/2, df)
                p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df))
                reject = abs(t_stat) > t_crit
            elif "Right" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha, df)
                p_val = 1 - stats.t.cdf(t_stat, df)
                reject = t_stat > t_crit
            else:
                t_crit = stats.t.ppf(alpha, df)
                p_val = stats.t.cdf(t_stat, df)
                reject = t_stat < t_crit

            st.info(f"Mean: {x_bar:.4f} | Std Dev: {s:.4f}")
            display_test_result(t_stat, t_crit, p_val, alpha, jenis_uji, 't', reject, 't', df1=df)

def load_pooled_t_test(title):
    st.header(title)
    
    with st.expander("📘 Penjelasan & Rumus (Levine Ch. 10.1)", expanded=False):
        st.markdown("""
        **Pooled-Variance t-Test** digunakan untuk membandingkan rata-rata dua populasi independen 
        dengan asumsi bahwa varians kedua populasi adalah **SAMA** ($\sigma_1^2 = \sigma_2^2$).
        
        **Asumsi:**
        1. Sampel diambil secara acak dan independen.
        2. Kedua populasi berdistribusi normal.
        3. Varians kedua populasi homogen.
        """)
        st.latex(r"t_{STAT} = \frac{(\bar{X}_1 - \bar{X}_2) - (\mu_1 - \mu_2)}{\sqrt{S_p^2 \left(\frac{1}{n_1} + \frac{1}{n_2}\right)}}")
        st.write("Dimana $S_p^2$ (Pooled Variance) adalah:")
        st.latex(r"S_p^2 = \frac{(n_1 - 1)S_1^2 + (n_2 - 1)S_2^2}{(n_1 - 1) + (n_2 - 1)}")

    col_param, col_data = st.columns([1, 2])
    with col_param:
        st.subheader("⚙️ Parameter")
        alpha = st.number_input("Signifikansi (α)", 0.01, 0.20, 0.05, step=0.01, key='a_pool')
        jenis_uji = st.selectbox("Arah Hipotesis", ["Two-sided", "Right-sided", "Left-sided"], key='t_pool')

    with col_data:
        st.subheader("📂 Input Data")
        tab1, tab2 = st.tabs(["Grup 1", "Grup 2"])
        with tab1: d1 = get_data_input("Sampel 1", "10, 12, 11, 14, 13", "p1")
        with tab2: d2 = get_data_input("Sampel 2", "14, 13, 15, 16, 14", "p2")

    # 3. EKSEKUSI
    if st.button("🚀 Jalankan Analisis Lengkap", type="primary"):
        if d1 is not None and d2 is not None:
            n1, n2 = len(d1), len(d2)
            
            st.markdown("---")
            st.subheader("1. Pengecekan Asumsi")
            c1, c2 = st.columns(2)
            with c1: check_normality(d1, "Grup 1")
            with c2: check_normality(d2, "Grup 2")
            
            x1, x2 = np.mean(d1), np.mean(d2)
            s1, s2 = np.std(d1, ddof=1), np.std(d2, ddof=1)
            
            sp2 = ((n1 - 1)*s1**2 + (n2 - 1)*s2**2) / (n1 + n2 - 2)
            se = np.sqrt(sp2 * (1/n1 + 1/n2))
            t_stat = (x1 - x2) / se
            df = n1 + n2 - 2
            
            if "Two" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha/2, df)
                p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df))
                reject = abs(t_stat) > t_crit
            elif "Right" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha, df)
                p_val = 1 - stats.t.cdf(t_stat, df)
                reject = t_stat > t_crit
            else:
                t_crit = stats.t.ppf(alpha, df)
                p_val = stats.t.cdf(t_stat, df)
                reject = t_stat < t_crit

            cohen_d = calculate_cohens_d(d1, d2)
            
            t_ci = stats.t.ppf(1 - 0.05/2, df)
            moe = t_ci * se
            ci_low = (x1-x2) - moe
            ci_high = (x1-x2) + moe

            st.markdown("### 2. Ringkasan Statistik")
            summ = pd.DataFrame({
                "Grup": ["1", "2"], "N": [n1, n2], "Mean": [x1, x2], "Std.Dev": [s1, s2]
            })
            st.table(summ)
            
            display_test_result(t_stat, t_crit, p_val, alpha, jenis_uji, 't', reject, 't', df1=df)
            
            st.markdown("### 3. Estimasi Tambahan")
            st.info(f"**Confidence Interval (95%):** [{ci_low:.4f}, {ci_high:.4f}]")
            st.success(f"**Effect Size (Cohen's d):** {abs(cohen_d):.4f} ({interpret_effect_size(cohen_d)})")

        else:
            st.error("Data kosong.")

def load_welch_t_test(title):
    st.header(title)
    with st.expander("📘 Penjelasan & Rumus (Levine Ch. 10.1)", expanded=False):
        st.write("""
        **Separate-Variance t Test (Welch)**
        
        Digunakan ketika varians populasi **tidak sama** ($\sigma_1^2 \\neq \sigma_2^2$). 
        Disebut juga Welch's t-test. Derajat kebebasan dihitung menggunakan rumus Satterthwaite.
        """)
        st.latex(r"t_{STAT} = \frac{(\bar{X}_1 - \bar{X}_2)}{\sqrt{\frac{S_1^2}{n_1} + \frac{S_2^2}{n_2}}}")
        st.write("Derajat Kebebasan (v) dihitung dengan rumus pendekatan:")
        st.latex(r"v = \frac{(\frac{S_1^2}{n_1} + \frac{S_2^2}{n_2})^2}{ \frac{(\frac{S_1^2}{n_1})^2}{n_1-1} + \frac{(\frac{S_2^2}{n_2})^2}{n_2-1} }")
        
    c1, c2 = st.columns(2)
    with c1: d1 = get_data_input("Grup 1", "78, 85, 80, 92, 75", "w1")
    with c2: d2 = get_data_input("Grup 2", "70, 72, 68, 71, 69", "w2")
    
    alpha = st.number_input("Alpha", 0.05, key='a_welch')
    jenis_uji = st.selectbox("Jenis Uji", ["Two-sided", "Right-sided", "Left-sided"], key='t_welch')

    if st.button("Hitung Welch t-Test"):
        if d1 is not None and d2 is not None:
            n1, n2 = len(d1), len(d2)
            v1, v2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
            se = np.sqrt(v1/n1 + v2/n2)
            t_stat = (np.mean(d1) - np.mean(d2)) / se
            
            num = (v1/n1 + v2/n2)**2
            den = ((v1/n1)**2 / (n1-1)) + ((v2/n2)**2 / (n2-1))
            df = num / den
            
            if "Two" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha/2, df)
                p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df))
                reject = abs(t_stat) > t_crit
            elif "Right" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha, df)
                p_val = 1 - stats.t.cdf(t_stat, df)
                reject = t_stat > t_crit
            else:
                t_crit = stats.t.ppf(alpha, df)
                p_val = stats.t.cdf(t_stat, df)
                reject = t_stat < t_crit
            
            st.info(f"Selisih Mean: {np.mean(d1)-np.mean(d2):.4f} | df: {df:.2f}")
            display_test_result(t_stat, t_crit, p_val, alpha, jenis_uji, 't', reject, 't', df1=df)

def load_paired_t_test(title):
    st.header(title)
    with st.expander("📘 Penjelasan & Rumus (Levine Ch. 10.2)", expanded=False):
        st.write("""
        **Paired t Test (Uji t Berpasangan)**
        
        Digunakan ketika sampel saling berhubungan (dependent), misalnya pengukuran "Pre-test" dan "Post-test" pada subjek yang sama.
        Kita menguji selisih ($D_i$) antara pasangan nilai.
        """)
        st.latex(r"t_{STAT} = \frac{\bar{D} - \mu_D}{S_D / \sqrt{n}}")
        st.write(r"""
        Dimana:
        * $\bar{D}$ = Rata-rata selisih sampel
        * $S_D$ = Simpangan baku selisih sampel
        """)
    
    c1, c2 = st.columns(2)
    with c1: d1 = get_data_input("Sebelum (Pre)", "50, 60, 70", "pair1")
    with c2: d2 = get_data_input("Sesudah (Post)", "60, 65, 75", "pair2")
    
    alpha = st.number_input("Alpha", 0.05, key='a_pair')
    jenis_uji = st.selectbox("Jenis Uji", ["Two-sided", "Right-sided", "Left-sided"], key='t_pair')

    if st.button("Hitung Paired t"):
        if d1 is not None and d2 is not None and len(d1) == len(d2):
            diff = d1 - d2
            check_normality(diff, "Selisih Data (Diff)")
            
            n = len(diff)
            d_bar = np.mean(diff)
            sd = np.std(diff, ddof=1)
            t_stat = d_bar / (sd / np.sqrt(n))
            df = n - 1
            
            if "Two" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha/2, df)
                p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df))
                reject = abs(t_stat) > t_crit
            elif "Right" in jenis_uji:
                t_crit = stats.t.ppf(1 - alpha, df)
                p_val = 1 - stats.t.cdf(t_stat, df)
                reject = t_stat > t_crit
            else:
                t_crit = stats.t.ppf(alpha, df)
                p_val = stats.t.cdf(t_stat, df)
                reject = t_stat < t_crit
                
            st.info(f"Rata-rata Selisih: {d_bar:.4f}")
            display_test_result(t_stat, t_crit, p_val, alpha, jenis_uji, 't', reject, 't', df1=df)
        else:
            st.error("Jumlah data harus sama.")

def load_f_test(title):
    st.header(title)
    with st.expander("📘 Penjelasan & Rumus (Levine Ch. 10.4)", expanded=False):
        st.write("""
        **F Test for the Ratio of Two Variances**
        
        Digunakan untuk menguji apakah dua populasi memiliki varians yang sama ($\sigma_1^2 = \sigma_2^2$). 
        Dalam menghitung rasio F, varians sampel yang lebih besar ($S_1^2$) selalu ditempatkan di pembilang (numerator).
        """)
        st.latex(r"F_{STAT} = \frac{S_1^2}{S_2^2}")
        st.write("Dimana $S_1^2 \ge S_2^2$.")
    
    c1, c2 = st.columns(2)
    with c1: d1 = get_data_input("Grup 1", "7, 9, 12, 10, 8", "f1")
    with c2: d2 = get_data_input("Grup 2", "8, 8, 9, 7, 8", "f2")
    
    alpha = st.number_input("Alpha", 0.05, key='a_f')
    
    if st.button("Hitung F-Test"):
        if d1 is not None and d2 is not None:
            v1, v2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
            n1, n2 = len(d1), len(d2)
            
            if v1 >= v2:
                f_stat = v1 / v2
                df1, df2 = n1 - 1, n2 - 1
            else:
                f_stat = v2 / v1
                df1, df2 = n2 - 1, n1 - 1
            
            f_crit = stats.f.ppf(1 - alpha/2, df1, df2)
            p_val = 2 * (1 - stats.f.cdf(f_stat, df1, df2))
            reject = f_stat > f_crit
            
            st.info(f"Rasio Varians (F): {f_stat:.4f}")
            display_test_result(f_stat, f_crit, p_val, alpha, "Two-sided", 'F', reject, 'f', df1=df1, df2=df2)