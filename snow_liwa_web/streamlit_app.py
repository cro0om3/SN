"""
Snow Liwa - Streamlit App
تطبيق سنو ليوا لحجز التذاكر
"""
import streamlit as st
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

# Custom CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1e3a8a;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.5rem;
        margin-bottom: 3rem;
    }
    .price-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        padding: 1rem;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "booking"
if "booking_id" not in st.session_state:
    st.session_state.booking_id = None

# Header
st.markdown('<h1 class="main-title">❄️ Snow Liwa</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">احجز تذكرتك الآن | Book Your Ticket Now</p>', unsafe_allow_html=True)

# Check if payment is configured
if not has_ziina_configured():
    st.warning("⚠️ نظام الدفع غير مفعّل حالياً | Payment system not configured")

# Booking Form Page
if st.session_state.page == "booking":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Price display
        st.markdown(f"""
        <div class="price-badge">
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
