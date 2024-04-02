
from flask import Flask, render_template, request, redirect, url_for
import sys
import database 
import pymysql
import datetime #오늘날짜 

#파일처리
import os
try:
	from werkzeug.utils import secure_filename
except:
	from werkzeug import secure_filename

dt_now = datetime.datetime.now()
dt_now = dt_now.date() #날짜만

application = Flask(__name__)

def connectsql():
    conn = pymysql.connect(host='localhost', user='root', password='root',
                      db='cafeteria_db', charset='utf8')
    return conn

@application.route("/") #메인페이지 
def main():
    today_list = database.load_today_list()
    remaining_qty = database.load_remaining_qty()
    
    print(today_list)
    return render_template("main.html", today_list = today_list, remaining_qty = remaining_qty); #이 페이지가 나오게 된다. 
    

@application.route("/admin") #관리자 페이지
def admin():
    return render_template("admin.html"); 

@application.route("/list")  #식단 보기 
def list():
    menu_list = database.load_list()
    length = len(menu_list)
    
    return render_template("list.html", menu_list = menu_list, length = length); 

@application.route("/apply") # 식단 등록 - 입력 부분  
def apply():
    return render_template("apply.html");  


@application.route("/applyphoto") # 식단 등록 - 처리부분
def applyphoto():
    date = request.args.get("date")
    main_menu = request.args.get("main_menu") #웹에서 입력한 값을 파이썬 변수에 저장된다. 
    menu1 = request.args.get("menu1")
    menu2 = request.args.get("menu2")
    menu3 = request.args.get("menu3")
    menu4 = request.args.get("menu4")
    menu5 = request.args.get("menu5")
    menu_price = request.args.get("menu_price")
    menu_qty = request.args.get("menu_qty")
    
    database.save(date, main_menu, menu1, menu2, menu3, menu4, menu5, menu_price, menu_qty)
    
    return render_template("apply_photo.html"); #위의 값들 저장 후에 이 페이지를 렌더링 해준다. 


@application.route("/apply_employee") # 사원 등록 - 입력부분 
def apply_employee():
    return render_template("apply_employee.html");  



@application.route("/apply_employee_proc") # 사원 등록 - 처리부분
def apply_employee_proc():
    employee_num = request.args.get("employee_num")
    employee_name = request.args.get("employee_name") #웹에서 입력한 값을 파이썬 변수에 저장된다. 
    department = request.args.get("department")
    
    database.save_employee(employee_num, employee_name, department)
    return render_template("admin.html"); #위의 값들 저장 후에 이 페이지를 렌더링 해준다.


@application.route("/apply_board") # 게시글 등록 - 입력부분 
def apply_board():
    return render_template("apply_board.html");  



@application.route("/apply_board_proc") # 게시글 등록 - 처리부분
def apply_board_proc():
    employee_num = request.args.get("employee_num")
    title = request.args.get("title") #웹에서 입력한 값을 파이썬 변수에 저장된다. 
    content = request.args.get("content")
    password = request.args.get("password")
    
    database.save_board(employee_num, title, content, password)
    return render_template("apply_board_proc.html"); #위의 값들 저장 후에 이 페이지를 렌더링 해준다. 

@application.route("/order") # 주문하기
def order():
    employee_num = request.args.get("employee_num")
    menu_chk0 = request.args.get("menu_chk0")
    menu_chk1 = request.args.get("menu_chk1")
    
    #체크박스 체크여부를 받아와서 저장
    database.order_menu(employee_num, menu_chk0, menu_chk1) #order 테이블에 추가 

    return render_template("order_success.html");

@application.route("/sales")  
def sales():
    return render_template("sales.html");

@application.route("/sales_proc")  
def sales_proc():
    month = request.args.get("month")
    sales_list = database.load_sales_list(month) #1일부터 ~ 막일까지 판매수량 
    return render_template("sales_proc.html", sales_list = sales_list, month = month);

@application.route("/employee_list")  #회원 목록 보기 
def employee_list():
    employee_list = database.load_employee_list()
    length = len(employee_list)
    expense_list = [] #사원별 총지출액
    
    for i in employee_list:
        expense_list.append(database.load_expense_list(i[0]))
    
    return render_template("employee_list.html", employee_list = employee_list, length = length, expense_list = expense_list); 
    #return render_template("employee_list.html", employee_list = employee_list, length = length); 

@application.route("/upload_done", methods = ['GET', 'POST']) 
def upload_done():
    if request.method == 'POST':
        uploaded_files = request.files['file'] #file 이라는 값을 받는다. 
		#저장할 경로 + 파일명
        uploaded_files.save('static/uploads/' + secure_filename(uploaded_files.filename)) # uploads 안에 저장
        #uploaded_files.save('static/uploads/' + secure_filename(uploaded_files.filename)+'{}'.format(dt_now)) # uploads 안에 저장

    # uploaded_files.save("static/img/{}.jpeg".format(database.now_index())) # index로 이미지 이름을 저장한다. 
    return redirect(url_for("admin")) #admin 라는 함수로 보내준다. 

# 아래는 원본 
@application.route("/house_info/<int:index>/") 
def house_info(index):
    '''menu_list = database.load_list()
    length = len(menu_list)
    
    photo = f"img/{index}.jpeg"
    #print(location, cleaness, built_in)
    return render_template("house_info.html", menu_list = menu_list, length = length, photo = photo); #앞에 있는 변수는 house_info.html에서의 변수 이름이고, 뒤에 있는 변수는 이 코드 바로 앞에 있는 변수들임 
'''
    photo = f"img/{index}.jpeg"
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "SELECT * FROM cafeteria WHERE menu_num = %s"
    value = index
    cursor.execute(query, value)
    content = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('house_info.html', data = content, photo = photo)



# 블로그 

@application.route("/post") #게시판 페이지
def post():
    board_list = database.load_board_list()
    length = len(board_list)
    return render_template("post.html", board_list = board_list, length = length);


@application.route('/post/content/<id>') # 게시글 자세히 보기 
def content(id):
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "SELECT no, date, employee_num, title, content FROM review_board WHERE no = %s"
    value = id
    cursor.execute(query, value)
    content = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('content.html', data = content)



@application.route('/post/edit/<id>', methods=['GET', 'POST'])
# GET -> 유지되고있는 username 세션과 현재 접속되어진 id와 일치시 edit페이지 연결
# POST -> 접속되어진 id와 일치하는 title, content를 찾아 UPDATE
def edit(id):
    if request.method == 'POST':
        edittitle = request.form['title']
        editcontent = request.form['content']

        conn = connectsql()
        cursor = conn.cursor()
        query = "UPDATE review_board SET title = %s, content = %s WHERE no = %s"
        value = (edittitle, editcontent, id)
        cursor.execute(query, value)
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('editSuccess.html')
    else:   
        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT no, title, content FROM review_board WHERE no = %s"
        value = id
        cursor.execute(query, value)
        postdata = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('edit.html', data=postdata)
           

        

@application.route('/post/delete/<id>')
# 유지되고 있는 username 세션과 id 일치시 삭제확인 팝업 연결
def delete(id):
    return render_template('delete.html', id = id)
    

@application.route('/post/delete/success/<id>')
# 삭제 확인시 id와 일치하는 컬럼 삭제, 취소시 /post 페이지 연결
def deletesuccess(id):
    conn = connectsql()
    cursor = conn.cursor()
    query = "DELETE FROM review_board WHERE no = %s"
    value = id
    cursor.execute(query, value)
    conn.commit()
    cursor.close()
    conn.close()
    
    return render_template('deleteSuccess.html')
    #return render_template ('post.html')

@application.route('/write', methods=['GET', 'POST'])
# GET -> write 페이지 연결
# POST -> username, password를 세션으로 불러온 후, form에 작성되어진 title, content를 테이블에 입력
def write():
    if request.method == 'POST':  
        usertitle = request.form['title']
        usercontent = request.form['content']
        useremployee_num = request.form['employee_num']

        conn = connectsql()
        cursor = conn.cursor() 
        query = "INSERT INTO review_board (date, employee_num, title, content) values (%s, %s, %s, %s)"
        value = (dt_now, useremployee_num, usertitle, usercontent)
        cursor.execute(query, value)
        conn.commit()
        cursor.close()
        conn.close()
        return render_template ('writeSuccess.html')
    
    else:
        return render_template ('write.html')

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
