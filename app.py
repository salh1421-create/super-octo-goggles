import io
import json
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة والهوية البصرية
st.set_page_config(
    page_title="منظومة تقارير دعم التميز المدرسي",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تخصيص التنسيق ودعم اللغة العربية (RTL)
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700;800&display=swap');
        
        * {
            font-family: 'Tajawal', sans-serif !important;
            direction: rtl;
            text-align: right;
        }
        
        .main-header {
            background: linear-gradient(135deg, #0f4c47 0%, #0f766e 100%);
            color: white;
            padding: 22px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(15, 118, 110, 0.2);
        }
        .main-header h2 {
            color: white !important;
            margin: 0;
            font-weight: 800;
        }
        .section-box {
            background-color: #f0fdfa;
            border-right: 5px solid #0f766e;
            padding: 10px 15px;
            font-weight: 700;
            color: #0f4c47;
            border-radius: 0 8px 8px 0;
            margin: 20px 0 15px 0;
        }
        .stButton>button {
            width: 100%;
            background-color: #0f766e;
            color: white;
            font-weight: 700;
            border-radius: 8px;
            padding: 10px;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #115e59;
            color: white;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect("school_reports.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            school_name TEXT,
            visit_num TEXT,
            semester TEXT,
            week TEXT,
            visit_date TEXT,
            provider_name TEXT,
            support_type TEXT,
            avg_score REAL,
            full_data TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()

# القائمة الجانبية للتنقل
st.sidebar.image(
    "https://img.icons8.com/color/96/school-building.png", width=75
)
st.sidebar.title("لوحة التحكم")
page = st.sidebar.radio(
    "الانتقال إلى:", ["📝 استكمال تقرير جديد", "📂 سجل التقارير المحفوظة"]
)

if page == "📝 استكمال تقرير جديد":
    st.markdown(
        """
        <div class="main-header">
            <div style="font-size: 0.95rem; opacity: 0.9; margin-bottom: 5px;">المملكة العربية السعودية • وزارة التعليم • الإدارة العامة للتعليم</div>
            <h2>تقرير التغذية الراجعة لمقدمي خدمات دعم التميز المدرسي</h2>
            <div style="font-size: 0.9rem; margin-top: 5px; opacity: 0.95;">خلال الفصل الدراسي الثاني لعام 1447 هـ</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("feedback_report_form"):
        # أولاً: البيانات العامة
        st.markdown(
            '<div class="section-box">أولاً: البيانات العامّة للزّيارة</div>',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            visit_num = st.selectbox(
                "رقم الزيارة", ["الأولى", "الثانية", "الثالثة", "الرابعة"], index=1
            )
            day = st.selectbox(
                "اليوم",
                ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"],
                index=0,
            )
            school_name = st.text_input(
                "اسم المدرسة", value="ربيعة بن الحارث", placeholder="اسم المدرسة"
            )
        with c2:
            semester = st.selectbox(
                "الفصل الدراسي", ["الأول", "الثاني", "الثالث"], index=1
            )
            visit_date = st.text_input("التاريخ", value="١٤٤٧/١١/٠٢ هـ")
            stage = st.selectbox(
                "المرحلة",
                ["ابتدائي", "متوسط", "ثانوي", "طفولة مبكرة"],
                index=1,
            )
        with c3:
            week = st.text_input("الأسبوع", value="الحادي عشر")
            visit_goal = st.text_input("الهدف من الزيارة", value="الدعم والمساندة")
            sector_col1, sector_col2 = st.columns(2)
            with sector_col1:
                gender = st.selectbox("الفئة", ["بنين", "بنات"])
            with sector_col2:
                sector = st.text_input("القطاع", value="العوالي")

        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            provider_name = st.text_input(
                "اسم مقدم/ـة خدمات دعم التميز",
                placeholder="أدخل الاسم الثلاثي...",
            )
        with c_p2:
            presence = st.radio(
                "تواجد مقدم الدعم:",
                ["نعم", "لا"],
                horizontal=True,
                index=0,
            )
        with c_p3:
            support_type = st.radio(
                "نوع الدعم المقدم:",
                ["حضوري", "عن بعد"],
                horizontal=True,
                index=0,
            )

        weekly_report_done = st.radio(
            "تعبئة رابط التقرير الأسبوعي للأسبوع السابق:",
            ["نعم", "لا"],
            horizontal=True,
            index=0,
        )

        st.write("**مجالات الدعم المقدمة للمدرسة خلال الزيارة:**")
        sup_cols = st.columns(4)
        with sup_cols[0]:
            sup_teach = st.checkbox("التدريس", value=True)
        with sup_cols[1]:
            sup_learn = st.checkbox("نواتج التعلم", value=True)
        with sup_cols[2]:
            sup_guide = st.checkbox("التوجيه الطلابي", value=True)
        with sup_cols[3]:
            sup_acts = st.checkbox("الأنشطة المدرسية", value=True)

        # ثانياً: ملخص التقويم
        st.markdown(
            '<div class="section-box">ثانيًا: ملخص نتائج أداء المدرسة وفق تقرير التقويم المدرسي الأخير</div>',
            unsafe_allow_html=True,
        )
        e1, e2, e3 = st.columns(3)
        with e1:
            eval_type = st.radio(
                "نوع التقييم المدرسي:",
                ["ذاتي", "خارجي", "لم يصدر لها تقرير"],
                horizontal=True,
                index=1,
            )
        with e2:
            perf_level = st.text_input(
                "مستوى الأداء العام للمدرسة", value="التقدم"
            )
            perf_rate = st.text_input("نسبة الأداء العام (رقماً)", value="٧٣٪")
        with e3:
            learning_level = st.text_input(
                "مستوى نواتج التعلم", value="انطلاق"
            )
            learning_rate = st.text_input(
                "نسبة نواتج التعلم (رقماً)", value="٦٩.٧٥٪"
            )

        # ثالثاً: رحلة المدرسة في الممارسات
        st.markdown(
            '<div class="section-box">ثالثًا: رحلة المدرسة في تحسين مجالات الممارسات الإشرافية الأساسية</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "📌 معيار التقدير: ( ٣: نُفّذ بدرجة عالية | ٢: نُفّذ بدرجة متوسطة | ١: نُفّذ بدرجة منخفضة )"
        )

        r_score_1 = st.selectbox(
            "١. أعدت المدرسة تقرير الواقع بما يتوافق مع احتياجاتها وأولوياتها التعليمية:",
            [
                (3, "٣ : نفذ بدرجة عالية"),
                (2, "٢ : نفذ بدرجة متوسطة"),
                (1, "١ : نفذ بدرجة منخفضة"),
            ],
            format_func=lambda x: x[1],
            index=0,
        )
        r_note_1 = st.text_input("ملاحظات تقرير الواقع", placeholder="شواهد...")

        r_score_2 = st.selectbox(
            "٢. بنت المدرسة خطة للتحسين في مجالات الممارسات الإشرافية وفق استمارة (١):",
            [
                (3, "٣ : نفذ بدرجة عالية"),
                (2, "٢ : نفذ بدرجة متوسطة"),
                (1, "١ : نفذ بدرجة منخفضة"),
            ],
            format_func=lambda x: x[1],
            index=0,
        )
        r_note_2 = st.text_input("ملاحظات خطة التحسين", placeholder="شواهد...")

        r_score_3 = st.selectbox(
            "٣. تنفذ المدرسة خطة التحسين وفق جدول زمني واضح واستمارة (٢):",
            [
                (3, "٣ : نفذ بدرجة عالية"),
                (2, "٢ : نفذ بدرجة متوسطة"),
                (1, "١ : نفذ بدرجة منخفضة"),
            ],
            format_func=lambda x: x[1],
            index=1,
        )
        r_note_3 = st.text_input("ملاحظات التنفيذ الزمني", placeholder="شواهد...")

        # رابعاً: خدمات دعم التميز المدرسي
        st.markdown(
            '<div class="section-box">رابعًا: تقديم خدمات دعم التميز المدرسي في مجالات الممارسات الإشرافية</div>',
            unsafe_allow_html=True,
        )
        s_c1, s_c2 = st.columns([1, 2])
        with s_c1:
            sc_teach = st.selectbox(
                "دعم التدريس:",
                [(3, "٣ : درجة عالية"), (2, "٢ : درجة متوسطة"), (1, "١ : درجة منخفضة")],
                format_func=lambda x: x[1],
                index=0,
            )
        with s_c2:
            note_teach = st.text_input("ملاحظات دعم التدريس")

        with s_c1:
            sc_learn = st.selectbox(
                "دعم نواتج التعلم:",
                [(3, "٣ : درجة عالية"), (2, "٢ : درجة متوسطة"), (1, "١ : درجة منخفضة")],
                format_func=lambda x: x[1],
                index=0,
            )
        with s_c2:
            note_learn = st.text_input("ملاحظات نواتج التعلم")

        with s_c1:
            sc_acts = st.selectbox(
                "دعم الأنشطة المدرسية:",
                [(3, "٣ : درجة عالية"), (2, "٢ : درجة متوسطة"), (1, "١ : درجة منخفضة")],
                format_func=lambda x: x[1],
                index=1,
            )
        with s_c2:
            note_acts = st.text_input("ملاحظات الأنشطة المدرسية")

        with s_c1:
            sc_guide = st.selectbox(
                "دعم التوجيه الطلابي:",
                [(3, "٣ : درجة عالية"), (2, "٢ : درجة متوسطة"), (1, "١ : درجة منخفضة")],
                format_func=lambda x: x[1],
                index=0,
            )
        with s_c2:
            note_guide = st.text_input("ملاحظات التوجيه الطلابي")

        # حساب المتوسط
        avg_score = round(
            (sc_teach[0] + sc_learn[0] + sc_acts[0] + sc_guide[0]) / 4.0, 2
        )

        avg_note = st.text_area(
            "وصف وملاحظات متوسط مستوى الخدمة المقدمة:",
            placeholder="مستوى الدعم وأثره الميداني...",
        )
        prev_recom_note = st.text_area(
            "مستوى تنفيذ التوصيات السابقة:",
            placeholder="مدى تحقق التوصيات السابقة...",
        )

        # خامساً: الجدارات والتغذية الراجعة
        st.markdown(
            '<div class="section-box">خامسًا: الجدارات الوظيفية والتغذية الراجعة الختامية</div>',
            unsafe_allow_html=True,
        )
        c_j1, c_j2 = st.columns(2)
        with c_j1:
            comp_resp = st.text_input(
                "ملاحظات جدارة المسؤولية", placeholder="شواهد الالتزام..."
            )
            comp_team = st.text_input(
                "ملاحظات جدارة العمل الجماعي",
                placeholder="شواهد التفاعل والتعاون...",
            )
        with c_j2:
            comp_flex = st.text_input(
                "ملاحظات جدارة المرونة للتغيير",
                placeholder="شواهد التكيف والتجاوب...",
            )
            comp_init = st.text_input(
                "ملاحظات جدارة المبادرة",
                placeholder="شواهد المقترحات التطويرية...",
            )

        challenges = st.text_area(
            "التحديات التي تواجه مقدم/ـة خدمات دعم التميز المدرسي:"
        )
        strengths = st.text_area(
            "نقاط القوة في أداء مقدم/ـة خدمات دعم التميز المدرسي:"
        )
        executive_feedback = st.text_area(
            "خلاصة التّغذية الرّاجعة المقدّمة من قبل عضو الفريق التّنفيذيّ:"
        )
        dev_needs = st.text_area(
            "احتياجات التطوير المهني لمقدم/ـة خدمات دعم التميز المدرسي:"
        )

        # سادساً: الاعتماد
        st.markdown(
            '<div class="section-box">سادسًا: بيانات الاعتماد والتوقيع</div>',
            unsafe_allow_html=True,
        )
        sig1, sig2 = st.columns(2)
        with sig1:
            p_sign_name = st.text_input(
                "اسم مقدم/ـة الدعم المعتمد", value=provider_name
            )
        with sig2:
            supervisor_name = st.text_input(
                "مشرف/ـة الفريق التنفيذي", placeholder="اسم المشرف/ـة"
            )

        submit_btn = st.form_submit_button("💾 حفظ التقرير في النظام")

        if submit_btn:
            report_data = {
                "school_name": school_name,
                "visit_num": visit_num,
                "semester": semester,
                "week": week,
                "day": day,
                "visit_date": visit_date,
                "visit_goal": visit_goal,
                "stage": stage,
                "gender": gender,
                "sector": sector,
                "provider_name": provider_name,
                "presence": presence,
                "support_type": support_type,
                "weekly_report_done": weekly_report_done,
                "support_fields": {
                    "teaching": sup_teach,
                    "learning": sup_learn,
                    "guidance": sup_guide,
                    "activities": sup_acts,
                },
                "evaluation": {
                    "type": eval_type,
                    "perf_level": perf_level,
                    "perf_rate": perf_rate,
                    "learning_level": learning_level,
                    "learning_rate": learning_rate,
                },
                "journey_scores": [
                    r_score_1[0],
                    r_score_2[0],
                    r_score_3[0],
                ],
                "journey_notes": [r_note_1, r_note_2, r_note_3],
                "service_scores": [
                    sc_teach[0],
                    sc_learn[0],
                    sc_acts[0],
                    sc_guide[0],
                ],
                "avg_score": avg_score,
                "avg_note": avg_note,
                "prev_recom_note": prev_recom_note,
                "competencies": {
                    "resp": comp_resp,
                    "team": comp_team,
                    "flex": comp_flex,
                    "init": comp_init,
                },
                "challenges": challenges,
                "strengths": strengths,
                "executive_feedback": executive_feedback,
                "dev_needs": dev_needs,
                "provider_sign_name": p_sign_name,
                "supervisor_name": supervisor_name,
            }

            conn = sqlite3.connect("school_reports.db")
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO reports (
                    timestamp, school_name, visit_num, semester, week, 
                    visit_date, provider_name, support_type, avg_score, full_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    school_name,
                    visit_num,
                    semester,
                    week,
                    visit_date,
                    provider_name,
                    support_type,
                    avg_score,
                    json.dumps(report_data, ensure_ascii=False),
                ),
            )
            conn.commit()
            conn.close()

            st.success(
                f"✅ تم حفظ تقرير مدرسة ({school_name}) بنجاح! متوسط الأداء: {avg_score} من 3"
            )

# صفحة استعراض السجلات
elif page == "📂 سجل التقارير المحفوظة":
    st.markdown(
        """
        <div class="main-header">
            <h2>سجل تقارير دعم التميز المدرسي المحفوظة</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    conn = sqlite3.connect("school_reports.db")
    df = pd.read_sql_query(
        "SELECT id as 'رقم التقرير', timestamp as 'وقت التسجيل', school_name as 'اسم المدرسة', visit_num as 'الزيارة', provider_name as 'مقدم الدعم', support_type as 'نوع الدعم', avg_score as 'متوسط الخدمة' FROM reports ORDER BY id DESC",
        conn,
    )
    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        selected_id = st.selectbox(
            "اختر رقم التقرير لمعاينته:", df["رقم التقرير"]
        )

        if st.button("عرض تفاصيل التقرير المحدد"):
            conn = sqlite3.connect("school_reports.db")
            c = conn.cursor()
            c.execute(
                "SELECT full_data FROM reports WHERE id = ?", (selected_id,)
            )
            row = c.fetchone()
            conn.close()

            if row:
                data = json.loads(row[0])
                st.info(
                    f"📌 تفاصيل تقرير مدرسة: **{data['school_name']}** — الزيارة {data['visit_num']}"
                )
                st.json(data)
    else:
        st.info("لا توجد تقارير محفوظة حتى الآن.")