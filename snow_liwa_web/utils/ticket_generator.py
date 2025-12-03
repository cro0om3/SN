"""Generate beautiful tickets for Snow Liwa bookings."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

def generate_ticket_html(booking_data: dict) -> str:
    """Generate a beautiful HTML ticket that can be converted to PDF or printed."""
    
    # Extract booking info
    booking_id = booking_data.get("booking_id", "N/A")
    name = booking_data.get("name", "Guest")
    tickets = booking_data.get("tickets", 1)
    total_amount = booking_data.get("total_amount", 0)
    created_at = booking_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Parse date
    try:
        date_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        formatted_date = date_obj.strftime("%d %b %Y")
        formatted_time = date_obj.strftime("%I:%M %p")
    except:
        formatted_date = created_at
        formatted_time = ""
    
    html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SNOW LIWA Ticket - {booking_id}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Montserrat:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Cairo', 'Montserrat', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .ticket-container {{
            max-width: 800px;
            width: 100%;
            background: white;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 30px 80px rgba(0,0,0,0.3);
        }}
        
        .ticket-header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .ticket-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }}
        
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        .snow-logo {{
            font-size: 48px;
            font-weight: 900;
            color: white;
            letter-spacing: 8px;
            margin-bottom: 8px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
            font-family: 'Montserrat', sans-serif;
        }}
        
        .snow-subtitle {{
            font-size: 18px;
            color: rgba(255,255,255,0.95);
            font-weight: 600;
            position: relative;
            z-index: 1;
        }}
        
        .ticket-body {{
            padding: 40px 30px;
        }}
        
        .booking-id {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 16px;
            margin-bottom: 30px;
        }}
        
        .booking-id-label {{
            font-size: 12px;
            color: rgba(255,255,255,0.9);
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .booking-id-value {{
            font-size: 32px;
            font-weight: 900;
            color: white;
            letter-spacing: 4px;
            font-family: 'Montserrat', monospace;
        }}
        
        .ticket-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .detail-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #4facfe;
        }}
        
        .detail-label {{
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .detail-value {{
            font-size: 20px;
            font-weight: 700;
            color: #212529;
        }}
        
        .ticket-info {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 30px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            text-align: center;
        }}
        
        .info-item {{
            background: rgba(255,255,255,0.5);
            padding: 15px;
            border-radius: 10px;
        }}
        
        .info-icon {{
            font-size: 28px;
            margin-bottom: 5px;
        }}
        
        .info-label {{
            font-size: 11px;
            color: #6c3c00;
            margin-bottom: 3px;
            text-transform: uppercase;
        }}
        
        .info-value {{
            font-size: 18px;
            font-weight: 700;
            color: #6c3c00;
        }}
        
        .instructions {{
            background: #e8f5ff;
            padding: 25px;
            border-radius: 16px;
            border: 2px dashed #4facfe;
            margin-bottom: 30px;
        }}
        
        .instructions-title {{
            font-size: 16px;
            font-weight: 700;
            color: #0066cc;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .instructions-list {{
            list-style: none;
            padding: 0;
        }}
        
        .instructions-list li {{
            padding: 10px 0;
            color: #333;
            display: flex;
            align-items: start;
            gap: 10px;
        }}
        
        .instructions-list li::before {{
            content: '✓';
            display: inline-block;
            width: 24px;
            height: 24px;
            background: #4facfe;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-weight: bold;
            flex-shrink: 0;
        }}
        
        .whatsapp-cta {{
            background: linear-gradient(135deg, #25d366 0%, #128c7e 100%);
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .whatsapp-cta-text {{
            color: white;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        
        .whatsapp-button {{
            display: inline-block;
            background: white;
            color: #128c7e;
            padding: 12px 30px;
            border-radius: 999px;
            text-decoration: none;
            font-weight: 700;
            font-size: 16px;
            transition: transform 0.2s;
        }}
        
        .whatsapp-button:hover {{
            transform: scale(1.05);
        }}
        
        .ticket-footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 12px;
        }}
        
        .qr-placeholder {{
            width: 150px;
            height: 150px;
            background: white;
            border: 2px dashed #dee2e6;
            border-radius: 12px;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #adb5bd;
            font-size: 14px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .ticket-container {{
                box-shadow: none;
                max-width: 100%;
            }}
            .whatsapp-cta, .whatsapp-button {{
                display: none;
            }}
        }}
        
        @media (max-width: 768px) {{
            .ticket-details {{
                grid-template-columns: 1fr;
            }}
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            .booking-id-value {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="ticket-container">
        <!-- Header -->
        <div class="ticket-header">
            <div class="snow-logo">SNOW LIWA</div>
            <div class="snow-subtitle">❄️ تجربة شتوية في قلب الظفرة ❄️</div>
        </div>
        
        <!-- Body -->
        <div class="ticket-body">
            <!-- Booking ID -->
            <div class="booking-id">
                <div class="booking-id-label">رقم الحجز · Booking ID</div>
                <div class="booking-id-value">{booking_id}</div>
            </div>
            
            <!-- Guest Details -->
            <div class="ticket-details">
                <div class="detail-box">
                    <div class="detail-label">اسم الضيف · Guest Name</div>
                    <div class="detail-value">{name}</div>
                </div>
                <div class="detail-box">
                    <div class="detail-label">تاريخ الحجز · Booking Date</div>
                    <div class="detail-value">{formatted_date}</div>
                </div>
            </div>
            
            <!-- Ticket Info -->
            <div class="ticket-info">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-icon">🎟️</div>
                        <div class="info-label">عدد التذاكر</div>
                        <div class="info-value">{tickets}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">💰</div>
                        <div class="info-label">المبلغ الإجمالي</div>
                        <div class="info-value">{total_amount:.0f} AED</div>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">✅</div>
                        <div class="info-label">الحالة</div>
                        <div class="info-value">مدفوع</div>
                    </div>
                </div>
            </div>
            
            <!-- Instructions -->
            <div class="instructions">
                <div class="instructions-title">
                    <span>📋</span>
                    <span>تعليمات مهمة · Important Instructions</span>
                </div>
                <ul class="instructions-list">
                    <li>احتفظ بهذه التذكرة معك عند الزيارة (مطبوعة أو على جوالك)</li>
                    <li>تواصل معنا على الواتساب لاستلام موقع Snow Liwa السري 🗺️</li>
                    <li>التذكرة صالحة للاستخدام في اليوم المحدد فقط</li>
                    <li>يرجى الوصول قبل 15 دقيقة من موعد الزيارة</li>
                </ul>
            </div>
            
            <!-- WhatsApp CTA -->
            <div class="whatsapp-cta">
                <div class="whatsapp-cta-text">
                    📱 تواصل معنا على الواتساب لاستلام موقع Snow Liwa
                </div>
                <a href="https://wa.me/971501234567?text=مرحباً، رقم حجزي: {booking_id}" class="whatsapp-button">
                    💬 أرسل رسالة واتساب
                </a>
            </div>
            
            <!-- QR Code Placeholder -->
            <div class="qr-placeholder">
                QR Code
            </div>
        </div>
        
        <!-- Footer -->
        <div class="ticket-footer">
            <p>شكراً لاختياركم SNOW LIWA ❄️</p>
            <p>Thank you for choosing SNOW LIWA</p>
            <p style="margin-top: 10px; font-size: 10px;">
                © 2025 SNOW LIWA - Emirati Youth Project
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return html
