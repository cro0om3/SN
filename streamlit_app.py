"""
Snow Liwa - Streamlit App
تطبيق سنو ليوا لحجز التذاكر - يعرض صفحة HTML الأصلية
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

# Hide Streamlit elements
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "booking_id" not in st.session_state:
    st.session_state.booking_id = None
if "show_booking_form" not in st.session_state:
    st.session_state.show_booking_form = False

# Load the original HTML file
html_file_path = Path(__file__).parent.parent / "FHD" / "1.html"

if st.session_state.page == "landing" and not st.session_state.show_booking_form:
    # Display original HTML
    if html_file_path.exists():
        html_content = html_file_path.read_text(encoding="utf-8")
        
        # Inject booking form handler
        html_content = html_content.replace(
            'onsubmit="return false;"',
            'onsubmit="return handleBooking(event);"'
        )
        
        # Add JavaScript to handle form submission
        booking_js = """
        <script>
        function handleBooking(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            
            // Store form data in sessionStorage
            sessionStorage.setItem('bookingName', formData.get('name'));
            sessionStorage.setItem('bookingPhone', formData.get('phone'));
            sessionStorage.setItem('bookingTickets', formData.get('tickets'));
            sessionStorage.setItem('bookingNotes', formData.get('notes') || '');
            
            // Redirect to Streamlit booking page
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'show_form'}, '*');
            return false;
        }
        </script>
        """
        html_content = html_content.replace('</body>', booking_js + '</body>')
        
        # Display the HTML
        components.html(html_content, height=2000, scrolling=True)
        
        # Check if user wants to book
        if st.button("", key="hidden_book_btn", help="Book"):
            st.session_state.show_booking_form = True
            st.rerun()
    else:
        st.error(f"HTML file not found: {html_file_path}")
        st.info("Showing alternative booking page...")
        st.session_state.show_booking_form = True

elif st.session_state.show_booking_form or st.session_state.page == "booking":
    # Back button
    if st.button("← العودة للصفحة الرئيسية | Back to Home"):
        st.session_state.page = "landing"
        st.session_state.show_booking_form = False
        st.rerun()
    
    st.markdown("""
    <style>
    .booking-page {
        max-width: 600px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 22px;
        box-shadow: 0 14px 40px rgba(7, 36, 63, 0.10);
    }
    .page-title {
        text-align: center;
        color: #163046;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .price-box {
        background: linear-gradient(135deg, #ffcf70, #f7b343);
        color: #2b1b05;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #ffcf70, #f7b343);
        color: #2b1b05;
        font-size: 1.2rem;
        padding: 0.8rem;
        border-radius: 999px;
        border: none;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(211, 151, 49, 0.45);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="booking-page">', unsafe_allow_html=True)
    st.markdown('<h2 class="page-title">احجز تذكرتك | Book Ticket</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="price-box">💳 {TICKET_PRICE_AED} AED per ticket</div>', unsafe_allow_html=True)
    
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
