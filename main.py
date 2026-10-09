import streamlit as st
from ultralytics import YOLO
import cv2
import pandas as pd
from collections import defaultdict
import numpy as np
from io import BytesIO
import hashlib
import json
import time

model = YOLO("yolov8n.pt")

prices = {
    "bottle": 5000,
    "apple": 2000,
    "banana": 1500,
    "orange": 1800,
    "carrot": 1000,
    "broccoli": 3000,
    "book": 20000,
    "cup": 5000,
    "spoon": 2000,
    "knife": 3000,
}

USERS_FILE = "users.json"

texts = {
    "fa": {
        "title": "سیستم پرداخت هوشمند",
        "welcome": "خوش آمدید",
        "login_title": "باشگاه مشتریان",
        "login_tab": "ورود",
        "register_tab": "ثبت نام",
        "member_code": "کد عضویت",
        "password": "رمز عبور",
        "login_btn": "ورود",
        "name": "نام و نام خانوادگی",
        "phone": "شماره تلفن",
        "email": "ایمیل",
        "confirm_password": "تکرار رمز عبور",
        "register_btn": "ثبت نام",
        "payment_title": "درگاه پرداخت",
        "customer": "مشتری",
        "amount_to_pay": "مبلغ قابل پرداخت",
        "card_info": "اطلاعات کارت",
        "card_number": "شماره کارت",
        "expiry_date": "تاریخ انقضا",
        "pay_btn": "پرداخت",
        "back_btn": "بازگشت به صفحه اصلی",
        "webcam_tab": "وبکم",
        "upload_tab": "آپلود عکس",
        "history_tab": "تاریخچه فاکتورها",
        "start_webcam": "شروع وبکم",
        "stop_webcam": "توقف وبکم",
        "reset_invoice": "ریست فاکتور",
        "add_manual": "افزودن دستی آیتم",
        "select_item": "انتخاب آیتم",
        "add_selected": "افزودن آیتم انتخاب شده",
        "invoice": "فاکتور",
        "total": "جمع کل",
        "download_invoice": "دانلود فاکتور",
        "pay": "پرداخت",
        "empty_invoice": "فاکتور خالی است",
        "upload_photo": "آپلود عکس",
        "processed_image": "تصویر پردازش شده",
        "detected_items": "آیتم‌های شناسایی شده",
        "no_items": "هیچ آیتمی شناسایی نشد",
        "invoice_history": "تاریخچه فاکتورها",
        "no_invoices": "هیچ فاکتور پرداخت شده‌ای وجود ندارد",
        "profile": "پروفایل کاربر",
        "logout": "خروج",
        "language": "زبان",
        "new_item_added": "آیتم جدید به فاکتور اضافه شد",
        "webcam_active": "وبکم فعال شد",
        "webcam_stopped": "وبکم متوقف شد",
        "webcam_error": "دسترسی به وبکم ممکن نیست",
        "webcam_inactive": "وبکم غیرفعال است",
        "payment_success": "پرداخت با موفقیت انجام شد",
        "amount_deducted": "تومان از حساب شما کسر شد",
        "complete_card_info": "لطفا اطلاعات کارت را کامل وارد کنید"
    },
    "en": {
        "title": "Smart Checkout System",
        "welcome": "Welcome",
        "login_title": "Customer Club",
        "login_tab": "Login",
        "register_tab": "Register",
        "member_code": "Member Code",
        "password": "Password",
        "login_btn": "Login",
        "name": "Full Name",
        "phone": "Phone Number",
        "email": "Email",
        "confirm_password": "Confirm Password",
        "register_btn": "Register",
        "payment_title": "Payment Gateway",
        "customer": "Customer",
        "amount_to_pay": "Amount to Pay",
        "card_info": "Card Information",
        "card_number": "Card Number",
        "expiry_date": "Expiry Date",
        "pay_btn": "Pay",
        "back_btn": "Back to Main Page",
        "webcam_tab": "Webcam",
        "upload_tab": "Upload Image",
        "history_tab": "Invoice History",
        "start_webcam": "Start Webcam",
        "stop_webcam": "Stop Webcam",
        "reset_invoice": "Reset Invoice",
        "add_manual": "Add Manual Item",
        "select_item": "Select Item",
        "add_selected": "Add Selected Item",
        "invoice": "Invoice",
        "total": "Total",
        "download_invoice": "Download Invoice",
        "pay": "Payment",
        "empty_invoice": "Invoice is empty",
        "upload_photo": "Upload Photo",
        "processed_image": "Processed Image",
        "detected_items": "Detected Items",
        "no_items": "No items detected",
        "invoice_history": "Invoice History",
        "no_invoices": "No paid invoices",
        "profile": "User Profile",
        "logout": "Logout",
        "language": "Language",
        "new_item_added": "New item added to invoice",
        "webcam_active": "Webcam activated",
        "webcam_stopped": "Webcam stopped",
        "webcam_error": "Cannot access webcam",
        "webcam_inactive": "Webcam is inactive",
        "payment_success": "Payment completed successfully",
        "amount_deducted": "was deducted from your account",
        "complete_card_info": "Please complete card information"
    }
}

def t(key):
    """تابع برای دریافت متن بر اساس زبان انتخاب شده"""
    lang = st.session_state.get('language', 'fa')
    return texts[lang].get(key, key)

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_to_csv(item_count, customer_name, filename="invoice"):
    data = []
    total_price = 0
    for item, count in item_count.items():
        price = prices[item] * count
        total_price += price
        data.append({"Item": item, "Count": count, "Price per Item (T)": prices[item], "Total Price (T)": price})
    data.append({"Item": "Total", "Count": "", "Price per Item (T)": "", "Total Price (T)": total_price})
    
    df = pd.DataFrame(data)
    customer_info = pd.DataFrame([{"Customer": customer_name}])
    final_df = pd.concat([customer_info, df], axis=1)
    
    csv = final_df.to_csv(index=False).encode('utf-8')
    return csv, f"{filename}_{customer_name}.csv"

def process_image(frame):
    results = model(frame)
    item_count = defaultdict(int)
    detected_items = set()
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = model.names[class_id]
            
            if confidence > 0.5 and label in prices:
                item_count[label] += 1
                detected_items.add(label)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                text = f"{label}: {int(confidence * 100)}% - Price: {prices[label]} T"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                text_x, text_y = x1, y1 - 10
                cv2.rectangle(frame, (text_x, text_y - text_size[1] - 5), 
                              (text_x + text_size[0] + 5, text_y + 5), (0, 255, 0), -1)
                cv2.putText(frame, text, (text_x, text_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    total_price = sum(prices[item] * count for item, count in item_count.items())
    if total_price > 0:
        cv2.putText(frame, f"Total Price: {total_price} T", (10, frame.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    return frame, item_count, total_price, detected_items

def login_page():
    st.title(t("login_title"))
    st.markdown("---")
    
    if 'language' not in st.session_state:
        st.session_state.language = 'fa'
    
    lang_col1, lang_col2 = st.columns([3, 1])
    with lang_col2:
        language = st.selectbox(t("language"), ["فارسی", "English"], 
                               index=0 if st.session_state.language == 'fa' else 1)
        st.session_state.language = 'fa' if language == "فارسی" else 'en'
    
    tab1, tab2 = st.tabs([t("login_tab"), t("register_tab")])
    
    with tab1:
        st.subheader(t("login_tab"))
        
        with st.form("login_form"):
            member_code = st.text_input(t("member_code"))
            password = st.text_input(t("password"), type="password")
            login_btn = st.form_submit_button(t("login_btn"))
            
            if login_btn:
                users = load_users()
                if member_code in users and users[member_code]['password'] == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.user_info = users[member_code]
                    st.session_state.member_code = member_code
                    st.success(f"{t('welcome')} {users[member_code]['name']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("کد عضویت یا رمز عبور اشتباه است" if st.session_state.language == 'fa' else "Wrong member code or password")
    
    with tab2:
        st.subheader(t("register_tab"))
        
        with st.form("register_form"):
            name = st.text_input(t("name"))
            phone = st.text_input(t("phone"))
            email = st.text_input(t("email"))
            password = st.text_input(t("password"), type="password")
            confirm_password = st.text_input(t("confirm_password"), type="password")
            register_btn = st.form_submit_button(t("register_btn"))
            
            if register_btn:
                if password != confirm_password:
                    st.error("رمز عبور و تکرار آن مطابقت ندارند" if st.session_state.language == 'fa' else "Passwords don't match")
                elif not name or not phone:
                    st.error("لطفا اطلاعات ضروری را وارد کنید" if st.session_state.language == 'fa' else "Please enter required information")
                else:
                    users = load_users()
                    member_code = f"CLUB{len(users) + 1:04d}"
                    
                    users[member_code] = {
                        'name': name,
                        'phone': phone,
                        'email': email,
                        'password': hash_password(password),
                        'join_date': time.strftime("%Y-%m-%d")
                    }
                    
                    save_users(users)
                    success_msg = f"""
                    ثبت نام با موفقیت انجام شد!
                    
                    **کد عضویت شما:** {member_code}
                    **نام:** {name}
                    
                    لطفا کد عضویت خود را یادداشت کنید.
                    """ if st.session_state.language == 'fa' else f"""
                    Registration successful!
                    
                    **Your Member Code:** {member_code}
                    **Name:** {name}
                    
                    Please save your member code.
                    """
                    st.success(success_msg)

def payment_page(total_amount, customer_name):
    st.title(t("payment_title"))
    st.markdown("---")
    
    st.info(f"{t('customer')}: **{customer_name}**")
    st.warning(f"{t('amount_to_pay')}: **{total_amount:,} {t('amount_deducted').split()[-1] if st.session_state.language == 'en' else 'تومان'}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t("card_info"))
        card_number = st.text_input(t("card_number"), placeholder="6037-XXXX-XXXX-XXXX")
        expiry_date = st.text_input(t("expiry_date"), placeholder="MM/YY")
        cvv2 = st.text_input("CVV2", type="password")
    
    with col2:
        st.subheader(t("pay_btn"))
        if st.button(t("pay_btn"), type="primary", use_container_width=True):
            if card_number and cvv2:
                st.balloons()
                st.success(f"✅ {t('payment_success')}!")
                st.info(f"{total_amount:,} {t('amount_deducted')}")
                
                if 'invoice_history' not in st.session_state:
                    st.session_state.invoice_history = []
                
                st.session_state.invoice_history.append({
                    'customer': customer_name,
                    'amount': total_amount,
                    'date': time.strftime("%Y-%m-%d %H:%M"),
                    'items': dict(st.session_state.item_count_webcam)
                })
                
                st.session_state.item_count_webcam = defaultdict(int)
                st.session_state.detected_items_history = set()
                st.session_state.payment_page = False
                st.rerun()
            else:
                st.error(t("complete_card_info"))
    
    if st.button(t("back_btn")):
        st.session_state.payment_page = False
        st.rerun()

def main_app():
    st.title(f"🛒 {t('title')}")
    st.title(f"{t('welcome')} {st.session_state.user_info['name']}")

    with st.sidebar:
        st.subheader(t("profile"))
        st.write(f"**{t('name').split(' و ')[0] if st.session_state.language == 'fa' else 'Name'}:** {st.session_state.user_info['name']}")
        st.write(f"**{t('member_code')}:** {st.session_state.member_code}")
        st.write(f"**{t('phone').split(' ')[0] if st.session_state.language == 'fa' else 'Phone'}:** {st.session_state.user_info.get('phone', '---')}")
        
        language = st.selectbox(t("language"), ["فارسی", "English"], 
                               index=0 if st.session_state.language == 'fa' else 1)
        st.session_state.language = 'fa' if language == "فارسی" else 'en'
        
        if st.button(t("logout")):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs([t("webcam_tab"), t("upload_tab"), t("history_tab")])
    
    with tab1:
        st.header(t("webcam_tab"))
        
        if 'item_count_webcam' not in st.session_state:
            st.session_state.item_count_webcam = defaultdict(int)
        if 'detected_items_history' not in st.session_state:
            st.session_state.detected_items_history = set()
        if 'cap' not in st.session_state:
            st.session_state.cap = None
        if 'webcam_active' not in st.session_state:
            st.session_state.webcam_active = False

        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(t("start_webcam"), type="primary", use_container_width=True):
                st.session_state.cap = cv2.VideoCapture(0)
                if st.session_state.cap.isOpened():
                    st.session_state.webcam_active = True
                    st.session_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    st.session_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    st.session_state.cap.set(cv2.CAP_PROP_FPS, 30)
                    st.success(t("webcam_active"))
                else:
                    st.error(t("webcam_error"))
        
        with col2:
            if st.button(t("stop_webcam"), use_container_width=True):
                if st.session_state.cap:
                    st.session_state.cap.release()
                    st.session_state.cap = None
                st.session_state.webcam_active = False
                st.info(t("webcam_stopped"))

        video_placeholder = st.empty()
        status_placeholder = st.empty()

        if st.session_state.webcam_active and st.session_state.cap and st.session_state.cap.isOpened():
            while st.session_state.webcam_active:
                ret, frame = st.session_state.cap.read()
                if not ret:
                    st.error("خطا در دریافت تصویر" if st.session_state.language == 'fa' else "Frame capture error")
                    break
                
                processed_frame, current_items, total_price, detected_items = process_image(frame)
                video_placeholder.image(processed_frame, channels="BGR", use_container_width=True)
                
                new_items = detected_items - st.session_state.detected_items_history
                
                if new_items:
                    for item in new_items:
                        st.session_state.item_count_webcam[item] += 1
                    
                    st.session_state.detected_items_history = detected_items.copy()
                    status_placeholder.success(f"{t('new_item_added')}: {', '.join(new_items)}")
                
                cv2.waitKey(1)
        
        elif not st.session_state.webcam_active:
            video_placeholder.info(t("webcam_inactive"))

        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button(t("reset_invoice"), use_container_width=True):
                st.session_state.item_count_webcam = defaultdict(int)
                st.session_state.detected_items_history = set()
                st.success("فاکتور ریست شد!" if st.session_state.language == 'fa' else "Invoice reset!")
        
        with col4:
            if st.button(t("add_manual"), use_container_width=True):
                manual_item = st.selectbox(t("select_item"), list(prices.keys()))
                if st.button(t("add_selected")):
                    st.session_state.item_count_webcam[manual_item] += 1
                    st.success(f"{manual_item} {'به فاکتور اضافه شد!' if st.session_state.language == 'fa' else 'added to invoice!'}")

        st.subheader(f"{t('invoice')} - {st.session_state.user_info['name']}")
        
        if st.session_state.item_count_webcam:
            total_invoice_price = 0
            
            for item, count in st.session_state.item_count_webcam.items():
                price = prices[item] * count
                total_invoice_price += price
                
                col_item, col_count, col_price = st.columns([3, 2, 3])
                with col_item:
                    st.write(f"{item}")
                with col_count:
                    st.write(f"{count} × {prices[item]} T")
                with col_price:
                    st.write(f"{price} T")
            
            st.markdown("---")
            st.markdown(f"**{t('total')}: {total_invoice_price:,} {'تومان' if st.session_state.language == 'fa' else 'T'}**")
            
            col5, col6 = st.columns(2)
            
            with col5:
                csv, filename = save_to_csv(st.session_state.item_count_webcam, st.session_state.user_info['name'], "invoice")
                st.download_button(
                    label=t("download_invoice"),
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col6:
                if st.button(t("pay"), type="primary", use_container_width=True):
                    st.session_state.payment_page = True
                    st.session_state.payment_amount = total_invoice_price
                    st.rerun()
            
        else:
            st.info(t("empty_invoice"))

    with tab2:
        st.header(t("upload_tab"))
        
        if 'item_count_image' not in st.session_state:
            st.session_state.item_count_image = defaultdict(int)
        
        uploaded_file = st.file_uploader(t("upload_photo"), type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            processed_frame, item_count, total_price, _ = process_image(frame)
            st.image(processed_frame, channels="BGR", caption=t("processed_image"), width=400)
            
            st.subheader(t("detected_items"))
            
            if item_count:
                for item, count in item_count.items():
                    price = prices[item] * count
                    st.write(f"{item}: {count} × {prices[item]} T = {price} T")
                
                st.write(f"**{t('total')}: {total_price:,} {'تومان' if st.session_state.language == 'fa' else 'T'}**")
                
                st.session_state.item_count_image = item_count
                
                if st.button(f"{t('pay')} {t('download_invoice')}"):
                    csv, filename = save_to_csv(st.session_state.item_count_image, st.session_state.user_info['name'], "invoice_image")
                    st.download_button(
                        label=t("download_invoice"),
                        data=csv,
                        file_name=filename,
                        mime="text/csv"
                    )
                    st.session_state.item_count_image = defaultdict(int)
            else:
                st.warning(t("no_items"))

    with tab3:
        st.header(t("invoice_history"))
        
        if 'invoice_history' in st.session_state and st.session_state.invoice_history:
            for i, invoice in enumerate(st.session_state.invoice_history[::-1], 1):
                with st.expander(f"{t('invoice')} {i} - {invoice['date']}"):
                    st.write(f"**{t('customer')}:** {invoice['customer']}")
                    st.write(f"**{t('amount_to_pay').split(':')[0] if st.session_state.language == 'fa' else 'Amount'}:** {invoice['amount']:,} {'تومان' if st.session_state.language == 'fa' else 'T'}")
                    st.write(f"**{'تاریخ' if st.session_state.language == 'fa' else 'Date'}:** {invoice['date']}")
                    st.write(f"**{'آیتم‌ها' if st.session_state.language == 'fa' else 'Items'}:**")
                    for item, count in invoice['items'].items():
                        st.write(f"- {item}: {count} {'عدد' if st.session_state.language == 'fa' else 'pcs'}")
        else:
            st.info(t("no_invoices"))

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'payment_page' not in st.session_state:
        st.session_state.payment_page = False
    if 'language' not in st.session_state:
        st.session_state.language = 'fa'
    
    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.payment_page:
        payment_page(st.session_state.payment_amount, st.session_state.user_info['name'])
    else:
        main_app()

if __name__ == "__main__":
    main()



    