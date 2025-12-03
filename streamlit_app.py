"""
Snow Liwa - Streamlit App
تطبيق سنو ليوا لحجز التذاكر
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import TICKET_PRICE_AED, get_ziina_config
from services.payments_ziina import has_ziina_configured, create_payment_intent
from utils.logic import get_next_booking_id, create_booking_and_get_amount
from utils.io import load_bookings, save_bookings

# Page config
st.set_page_config(
    page_title="Snow Liwa - حجز التذاكر",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Enhanced with landing page styles
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Landing page styles */
    .hero-section {
        background: radial-gradient(circle at top right, #ffffff, #f3f7ff 55%, #ffe9c3 120%);
        padding: 3rem 2rem;
        border-radius: 26px;
        box-shadow: 0 14px 40px rgba(7, 36, 63, 0.10);
        margin-bottom: 2rem;
    }
    .hero-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        color: #61b8ff;
        letter-spacing: 0.3em;
        margin-bottom: 1rem;
    }
    .hero-subtitle-ar {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: #163046;
        margin-bottom: 1rem;
    }
    .hero-desc {
        text-align: center;
        font-size: 1.1rem;
        color: #6b7b8c;
        max-width: 800px;
        margin: 0 auto 2rem;
        line-height: 1.6;
    }
    .badge-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    .badge {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #e0e9f5;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.9rem;
        color: #6b7b8c;
    }
    .feature-card {
        background: white;
        border-radius: 18px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(7, 36, 63, 0.08);
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #163046;
        margin-bottom: 0.5rem;
    }
    .feature-text {
        font-size: 1rem;
        color: #6b7b8c;
        line-height: 1.6;
    }
    .price-highlight {
        background: linear-gradient(135deg, #ffcf70, #f7b343);
        color: #2b1b05;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0;
        box-shadow: 0 10px 26px rgba(211, 151, 49, 0.55);
    }
    .booking-section {
        background: white;
        border-radius: 22px;
        padding: 2rem;
        box-shadow: 0 14px 40px rgba(7, 36, 63, 0.10);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 2px solid #28a745;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #ffcf70, #f7b343);
        color: #2b1b05;
        font-size: 1.2rem;
        padding: 1rem;
        border-radius: 999px;
        border: none;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 10px 26px rgba(211, 151, 49, 0.55);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 36px rgba(211, 151, 49, 0.75);
    }
    .logo-mark {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4dafff, #ffcf70);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 28px;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "booking_id" not in st.session_state:
    st.session_state.booking_id = None

# LANDING PAGE
if st.session_state.page == "landing":
    # Logo
    st.markdown('<div class="logo-mark">SL</div>', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">SNOW LIWA</div>
        <div class="hero-subtitle-ar">تجربة شتوية في قلب الظفرة</div>
        <p class="hero-desc">
            مشروع شبابي إماراتي يقدم أجواء شتوية للعائلات والشباب، من لعب الثلج إلى
            الشوكولاتة الساخنة ولمسات من البساطة والجمال.
        </p>
        <p class="hero-desc" style="font-style: italic;">
            Emirati youth project offering a cozy winter experience in the heart of Al Dhafra,
            mixing the charm of Liwa desert with snow, hot chocolate and warm hospitality.
        </p>
        <div class="badge-container">
            <span class="badge">❄️ Snow Experience</span>
            <span class="badge">🏜️ Desert x Snow</span>
            <span class="badge">👨‍👩‍👧‍👦 Families & Youth</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">❄️ تجربة الثلج</div>
            <div class="feature-text">
                في مبادرةٍ فريدةٍ تمنح الزوّار أجواءً ثلجية ممتعة وتجربةً استثنائية لا تُنسى،
                يمكنكم الاستمتاع بمشاهدة تساقط الثلج، وتجربة مشروب الشوكولاتة الساخنة.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🍫 ضيافة راقية</div>
            <div class="feature-text">
                مع ضيافةٍ راقية تشمل الفراولة ونافورة الشوكولاتة، نقدم تجربة متكاملة
                للعائلات والشباب في أجواء آمنة وممتعة.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Price highlight
    st.markdown(f"""
    <div class="price-highlight">
        🎟️ تذكرة الدخول فقط {TICKET_PRICE_AED} درهم<br>
        Entrance ticket only {TICKET_PRICE_AED} AED
    </div>
    """, unsafe_allow_html=True)
    
    # How it works
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📋 كيف تحجز؟</div>
        <div class="feature-text">
            <p>① املأ نموذج الحجز بالمعلومات المطلوبة.</p>
            <p>② ادفع أونلاين عبر Ziina (175 درهم لكل شخص).</p>
            <p>③ استلم تذكرتك الإلكترونية مباشرة بعد الدفع.</p>
            <p>④ تواصل معنا على الواتساب لاستلام لوكيشن الموقع 🫣</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Who we are
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">من نحن؟ | Who are we</div>
        <div class="feature-text">
            <p>مشروع شبابي إماراتي من قلب منطقة الظفرة، يقدم تجربة شتوية فريدة تجمع بين أجواء ليوا
            الساحرة ولمسات من البساطة والجمال.</p>
            <p style="font-style: italic; margin-top: 1rem;">
            Emirati youth project from the heart of Al Dhafra region. It offers a unique winter
            experience that combines the charming atmosphere of Liwa with touches of simplicity
            and beauty.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # FAQ
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">❓ أسئلة شائعة | FAQ</div>
        <div class="feature-text">
            <p><strong>هل المكان مناسب للعائلات؟</strong><br>
            نعم، SNOW LIWA مخصص للعائلات والشباب مع أجواء آمنة وممتعة.</p>
            
            <p><strong>هل يجب الحجز مسبقًا؟</strong><br>
            نعم، احجز وادفع أونلاين لتضمن مكانك وتحصل على تذكرتك فوراً.</p>
            
            <p><strong>أين موقعكم؟</strong><br>
            الموقع سري 🫣 – سيتم إرسال اللوكيشن بعد تأكيد الدفع على الواتساب.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎫 احجز تذكرتك الآن | Book Your Ticket Now", key="cta_landing"):
        st.session_state.page = "booking"
        st.rerun()
    
    # Warning if payment not configured
    if not has_ziina_configured():
        st.warning("⚠️ نظام الدفع غير مفعّل حالياً | Payment system not configured")

# BOOKING FORM PAGE
elif st.session_state.page == "booking":
    # Back button
    if st.button("← العودة للصفحة الرئيسية | Back to Home"):
        st.session_state.page = "landing"
        st.rerun()
    
    st.markdown('<div class="logo-mark">SL</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #163046; margin-bottom: 2rem;">احجز تذكرتك | Book Your Ticket</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="booking-section">', unsafe_allow_html=True)
        
        # Price display
        st.markdown(f"""
        <div class="price-highlight" style="margin-top: 0;">
            💳 سعر التذكرة | Ticket Price<br>
            <strong>{TICKET_PRICE_AED} AED</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Booking form
        with st.form("booking_form"):
            st.subheader("📝 معلومات الحجز | Booking Information")
            
            name = st.text_input(
                "الاسم الكامل | Full Name *",
                placeholder="أدخل اسمك الكامل"
            )
            
            phone = st.text_input(
                "رقم الهاتف | Phone Number *",
                placeholder="+971xxxxxxxxx"
            )
            
            tickets = st.number_input(
                "عدد التذاكر | Number of Tickets *",
                min_value=1,
                max_value=20,
                value=1
            )
            
            notes = st.text_area(
                "ملاحظات إضافية | Additional Notes",
                placeholder="أي ملاحظات خاصة؟"
            )
            
            st.markdown("---")
            
            col_a, col_b = st.columns(2)
            with col_a:
                total_amount = tickets * TICKET_PRICE_AED
                st.metric("المجموع | Total", f"{total_amount} AED")
            
            submit = st.form_submit_button("🎫 احجز الآن | Book Now")
            
            if submit:
                if not name.strip() or not phone.strip():
                    st.error("⚠️ الرجاء إدخال الاسم ورقم الهاتف | Please enter name and phone")
                else:
                    # Create booking
                    form_data = {
                        "name": name.strip(),
                        "phone": phone.strip(),
                        "tickets": int(tickets),
                        "notes": notes.strip()
                    }
                    
                    booking_id, total_amount = create_booking_and_get_amount(form_data)
                    st.session_state.booking_id = booking_id
                    
                    if has_ziina_configured():
                        # Create payment intent
                        with st.spinner("جاري تحويلك إلى صفحة الدفع..."):
                            pi = create_payment_intent(total_amount, booking_id, name)
                            
                            if pi:
                                # Get redirect URL
                                redirect_url = (
                                    pi.get("redirect_url")
                                    or pi.get("hosted_page_url")
                                    or (pi.get("next_action") or {}).get("redirect_url")
                                )
                                
                                # Update booking with payment intent
                                df = load_bookings()
                                mask = df["booking_id"] == booking_id
                                if mask.any():
                                    payment_intent_id = str(pi.get("id", ""))
                                    df.loc[mask, "payment_intent_id"] = payment_intent_id
                                    df.loc[mask, "payment_status"] = pi.get("status", "pending")
                                    save_bookings(df)
                                
                                if redirect_url:
                                    st.success(f"✅ تم إنشاء الحجز رقم: {booking_id}")
                                    st.markdown(f"""
                                    <div class="success-box">
                                        <h3>🎉 تم إنشاء حجزك بنجاح!</h3>
                                        <p>رقم الحجز: <strong>{booking_id}</strong></p>
                                        <p>المبلغ الإجمالي: <strong>{total_amount} AED</strong></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.markdown(f"### [💳 اضغط هنا للدفع عبر Ziina]({redirect_url})")
                                    st.info("👆 اضغط على الرابط أعلاه لإكمال عملية الدفع")
                                else:
                                    st.error("❌ حدث خطأ في إنشاء رابط الدفع")
                            else:
                                st.error("❌ فشل الاتصال بنظام الدفع")
                    else:
                        # No payment system configured
                        st.session_state.page = "success_no_payment"
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Success page (no payment)
elif st.session_state.page == "success_no_payment":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="success-box">
            <h2>✅ تم إنشاء الحجز بنجاح!</h2>
            <h3>Booking Created Successfully!</h3>
            <p>رقم الحجز | Booking ID: <strong>{st.session_state.booking_id}</strong></p>
            <p>⚠️ الرجاء التواصل مع الإدارة لإكمال الدفع</p>
            <p>Please contact admin to complete payment</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 حجز جديد | New Booking"):
            st.session_state.page = "booking"
            st.session_state.booking_id = None
            st.rerun()

# Admin sidebar
with st.sidebar:
    st.markdown("### 🔐 Admin Panel")
    admin_pin = st.text_input("Admin PIN", type="password")
    
    if admin_pin:
        from core.config import ADMIN_PIN
        if admin_pin == ADMIN_PIN:
            st.success("✅ Admin access granted")
            
            if st.button("📊 View All Bookings"):
                st.session_state.page = "admin"
                st.rerun()

# Admin page
if st.session_state.page == "admin":
    st.markdown("## 📊 لوحة التحكم | Admin Dashboard")
    
    df = load_bookings()
    
    if not df.empty:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("إجمالي الحجوزات", len(df))
        with col2:
            paid_count = len(df[df["status"] == "paid"])
            st.metric("المدفوعة", paid_count)
        with col3:
            pending_count = len(df[df["status"] == "pending"])
            st.metric("قيد الانتظار", pending_count)
        with col4:
            total_revenue = df[df["status"] == "paid"]["total_amount"].sum()
            st.metric("الإيرادات", f"{total_revenue:.0f} AED")
        
        st.markdown("---")
        
        # Filters
        status_filter = st.selectbox(
            "تصفية حسب الحالة",
            ["All", "paid", "pending", "cancelled"]
        )
        
        # Apply filter
        if status_filter != "All":
            filtered_df = df[df["status"] == status_filter]
        else:
            filtered_df = df
        
        # Display table
        st.dataframe(
            filtered_df[[
                "booking_id", "customer_name", "phone", 
                "tickets", "total_amount", "status", 
                "payment_status", "created_at"
            ]],
            use_container_width=True
        )
        
        # Sync button
        if has_ziina_configured():
            if st.button("🔄 Sync Payment Status"):
                from services.payments_ziina import sync_all_bookings
                with st.spinner("Syncing..."):
                    updated_df = sync_all_bookings(df)
                    st.success("✅ Payment status updated!")
                    st.rerun()
    else:
        st.info("لا توجد حجوزات حتى الآن | No bookings yet")
    
    if st.button("🔙 Back to Booking"):
        st.session_state.page = "booking"
        st.rerun()
