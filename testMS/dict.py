from django.shortcuts import render_to_response
from django.shortcuts import render, redirect

vietnamese = {
    "titleLogin" : "Đăng Nhập Tài Khoản",
    "loginbutton" : "Đăng nhập",
    #Index
    "navigation" : "Thanh công cụ", 
    "CS" : "Dịch Vụ Khách Hàng",
    "CC" : "Tổng Đài Hỗ Trợ",
    "OnlChat" : "Hỗ Trợ Trực Tuyến",
    "Cfeed" : "Khách Hàng Đánh Giá",
    "RP" : "Báo Cáo",
    "CP" : "Xử Lý Hợp Đồng",
    "VNP" : "VNPost",
    "Doc" : "Tài Liệu",
    "Profile" : "Cá Nhân",
    "Signout" : "Đăng Xuất",
    "AutoSMS" : "Tin Nhắn Báo Card Tự Động",
    "AutoMRC" : "Tin Nhắn Báo MRC Tự Động",
    #IndexVNP
    "SendSMS" : "Gửi SMS",
    "title1" : "Buu dien khong phat duoc The tin dung cua Quy khach. Ma buu pham cua KH la:",
    "title2" : "Vui long lien he so (024) 38165018 - 0915233199 de nhan",
    "CN" : "Số Hợp Đồng",
    "ITC" : "Mã Bưu Phẩm",
    "PN" : "Số Điện Thoại",
    "MSGContent" : "Nội Dung",
    "result" : "Kết Quả",
    #reports
    "rplist" : "Danh Sách Báo Cáo",
    "Add" : "Thêm",
    "Name" : "Tên",
    "Des" : "Chi Tiết",
    "Edit" : "Sửa",
    "Del" : "Xóa",
    "Export" : "Xuất",
    #fb report
    "feedback2" : "Giúp chúng tôi nâng cao chất lượng phục vụ bằng những phản hồi của bạn",
    "feedback" : "Phản Hồi",
    "From" : "Từ:",
    "To" : "Đến:",
    "vldate1" : "Vui Lòng Chọn Ngày !",
    "vldate2" : "Ngày bắt đầu không thể lớn hơn ngày kết thúc !",
    "Username" : "Nhân viên",
    "showbtn" : "Hiện",
    "expdatabtn" : "Xuất dữ liệu",
    "Vote" : "Đánh giá",
    "Date" : "Thời gian",

}

english = {
    "titleLogin" : "Account Login",
    "loginbutton" : "Login",
    #Index
    "navigation" : "Tools Navigation",
    "CS" : "Customer Service",
    "CC" : "Call Center",
    "OnlChat" : "Online Chat",
    "Cfeed" : "Customer Feedback",
    "RP" : "Report",
    "CP" : "Contract Processing",
    "VNP" : "VNPost",
    "Doc" : "Documentation",
    "Profile" : "Profile",
    "Signout" : "Sign Out",
    "AutoSMS" : "Auto SMS-Card",
    "AutoMRC" : "Auto SMS-MRC",
    #IndexVNP
    "SendSMS" : "Send SMS",
    "title1" : "Post Office cannot send your Credit Card. The Customer's Postal Code is: ",
    "title2" : "Please contact (024) 38165018 - 0915233199 to receive",
    "CN" : "Contract Number",
    "ITC" : "Item Code",
    "PN" : "Phone Number",
    "MSGContent" : "Message Content",
    "result" : "Result",
    #reports
    "rplist" : "Report List",
    "Add" : "Add",
    "Name" : "Name",
    "Des" : "Description",
    "Edit" : "Edit",
    "Del" : "Delete",
    "Export" : "Export",
    #fb report
    "feedback" : "Feedback",
    "feedback2" : "Please help us improve our service with your feedback",
    "From" : "From:",
    "To" : "To:",
    "vldate1" : "Please choose a date !",
    "vldate2" : "From Date cannot be larger than To Date !",
    "Username" : "Username",
    "showbtn" : "Show",
    "expdatabtn" : "Export Data",
    "Vote" : "Vote",
    "Date" : "Date"
}

def languageContent(lang):
    if lang == "vn":
        return vietnamese
    if lang == "en":
        return english
