from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# 데이터 저장 파일
DATA_FILE = "school_schedule.json"

# 시간표 설정
TIME_SLOTS = [
    "조회 (08:30-08:40)",
    "1교시 (08:40-09:30)",
    "2교시 (09:40-10:30)",
    "3교시 (10:40-11:30)",
    "4교시 (11:40-12:30)",
    "점심 (12:30-13:30)",
    "5교시 (13:30-14:20)",
    "6교시 (14:30-15:20)",
    "7교시 (15:30-16:20)",
    "정소 (16:20-16:40)"
]

# 요일 설정
WEEKDAYS = ["월요일", "화요일", "수요일", "목요일", "금요일"]

# 부서 설정
DEPARTMENTS = [
    "교무기획부", "교육과정부", "교육연구부", "체육예술건강교육부",
    "진로진학상담부", "방과후자공고부", "학생생활안전부", "교육정보부",
    "인문사회교육부", "과학중점교육부", "1학년부", "2학년부", "3학년부"
]

def load_data():
    """저장된 데이터 로드"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    """데이터 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_week_start(date_str=None):
    """주어진 날짜의 주 시작일(월요일) 반환"""
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date = datetime.now()
    
    days_since_monday = date.weekday()
    monday = date - timedelta(days=days_since_monday)
    return monday

@app.route('/')
def index():
    """메인 페이지"""
    # 현재 주의 시작일
    week_start = get_week_start()
    
    # 주간 날짜들 생성
    week_dates = []
    for i in range(5):  # 월~금
        date = week_start + timedelta(days=i)
        week_dates.append({
            'date': date.strftime('%Y-%m-%d'),
            'display': date.strftime('%m월 %d일'),
            'weekday': WEEKDAYS[i]
        })
    
    # 데이터 로드
    schedule_data = load_data()
    
    return render_template('index.html', 
                         time_slots=TIME_SLOTS,
                         week_dates=week_dates,
                         departments=DEPARTMENTS,
                         schedule_data=schedule_data)

@app.route('/week/<date>')
def week_view(date):
    """특정 주의 뷰"""
    week_start = get_week_start(date)
    
    # 주간 날짜들 생성
    week_dates = []
    for i in range(5):  # 월~금
        date_obj = week_start + timedelta(days=i)
        week_dates.append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'display': date_obj.strftime('%m월 %d일'),
            'weekday': WEEKDAYS[i]
        })
    
    # 데이터 로드
    schedule_data = load_data()
    
    return render_template('index.html', 
                         time_slots=TIME_SLOTS,
                         week_dates=week_dates,
                         departments=DEPARTMENTS,
                         schedule_data=schedule_data)

@app.route('/api/add_task', methods=['POST'])
def add_task():
    """업무 추가 API"""
    try:
        data = request.get_json()
        department = data.get('department')
        date = data.get('date')
        time_slot = data.get('time_slot')
        task = data.get('task')
        
        if not all([department, date, time_slot, task]):
            return jsonify({'success': False, 'message': '모든 필드를 입력해주세요.'})
        
        # 데이터 로드
        schedule_data = load_data()
        
        # 데이터에 저장
        if date not in schedule_data:
            schedule_data[date] = {}
        
        if time_slot not in schedule_data[date]:
            schedule_data[date][time_slot] = []
        
        task_info = {
            "department": department,
            "task": task,
            "time_slot": time_slot
        }
        
        schedule_data[date][time_slot].append(task_info)
        save_data(schedule_data)
        
        return jsonify({'success': True, 'message': '업무가 추가되었습니다.'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@app.route('/api/delete_task', methods=['POST'])
def delete_task():
    """업무 삭제 API"""
    try:
        data = request.get_json()
        date = data.get('date')
        time_slot = data.get('time_slot')
        task_index = data.get('task_index')
        
        if not all([date, time_slot, task_index is not None]):
            return jsonify({'success': False, 'message': '필수 정보가 누락되었습니다.'})
        
        # 데이터 로드
        schedule_data = load_data()
        
        if date in schedule_data and time_slot in schedule_data[date]:
            tasks = schedule_data[date][time_slot]
            if 0 <= task_index < len(tasks):
                del tasks[task_index]
                
                # 빈 리스트면 시간대 삭제
                if not tasks:
                    del schedule_data[date][time_slot]
                
                # 빈 날짜면 날짜 삭제
                if not schedule_data[date]:
                    del schedule_data[date]
                
                save_data(schedule_data)
                return jsonify({'success': True, 'message': '업무가 삭제되었습니다.'})
        
        return jsonify({'success': False, 'message': '삭제할 업무를 찾을 수 없습니다.'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@app.route('/api/get_schedule')
def get_schedule():
    """스케줄 데이터 조회 API"""
    schedule_data = load_data()
    return jsonify(schedule_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 