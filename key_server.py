from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import secrets
import string
import datetime
import os
import hashlib
from functools import wraps
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 启用跨域请求
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))  # 为session设置密钥

# 从环境变量获取数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'educoder_keys')
}

# 管理员配置
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'ADMIN_PASSWORD')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'ADMIN_TOKEN')

# 初始化数据库
def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建卡密表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activation_keys (
            id INT AUTO_INCREMENT PRIMARY KEY,
            key_value VARCHAR(32) UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            max_devices INT DEFAULT 1,
            used_count INT DEFAULT 0
        )
        ''')
        
        # 创建设备绑定表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_bindings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            key_id INT NOT NULL,
            device_id VARCHAR(64) NOT NULL,
            last_verified DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (key_id) REFERENCES activation_keys(id) ON DELETE CASCADE,
            UNIQUE (key_id, device_id)
        )
        ''')
        
        # 创建用户信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(64) NOT NULL,
            key_id INT,
            username VARCHAR(100),
            real_name VARCHAR(100),
            user_identity VARCHAR(50),
            identity VARCHAR(50),
            phone VARCHAR(20),
            school_province VARCHAR(50),
            department_name VARCHAR(100),
            edu_background VARCHAR(50),
            edu_entry_year INT,
            student_id VARCHAR(50),
            user_school_id INT,
            school_name VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (key_id) REFERENCES activation_keys(id) ON DELETE SET NULL,
            UNIQUE (device_id)
        )
        ''')
        
        conn.commit()
        print("数据库初始化成功")
    except Error as e:
        print(f"数据库初始化错误: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 生成随机卡密
def generate_key(length=16):
    """
    生成固定格式的随机卡密，格式为 XXXX-XXXX-XXXX-XXXX（每4位用连字符分隔）
    默认总长度为16个字符（不包括连字符）
    """
    alphabet = string.ascii_uppercase + string.digits  # 使用大写字母和数字
    # 确保length是4的倍数
    if length % 4 != 0:
        length = ((length // 4) + 1) * 4
    
    # 生成连续的随机字符
    random_chars = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # 每4个字符插入一个连字符
    groups = [random_chars[i:i+4] for i in range(0, length, 4)]
    formatted_key = '-'.join(groups)
    
    return formatted_key

# 管理员认证装饰器 - 使用token
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头、请求参数或请求体中获取token
        token = None
        if 'admin_token' in request.headers:
            token = request.headers['admin_token']
        elif request.method == 'GET' and 'admin_token' in request.args:
            token = request.args.get('admin_token')
        elif request.method == 'POST' and request.is_json and 'admin_token' in request.json:
            token = request.json.get('admin_token')
        
        if not token:
            return jsonify({'success': False, 'message': '未授权访问：缺少admin_token参数'}), 401
        
        if token != ADMIN_TOKEN:
            return jsonify({'success': False, 'message': '未授权访问：admin_token无效'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# 验证卡密API
@app.route('/api/verify-key', methods=['POST'])
def verify_key():
    data = request.json
    if not data or 'key' not in data or 'deviceId' not in data:
        return jsonify({'valid': False, 'message': '请求参数不完整'}), 400
    
    key = data['key']
    device_id = data['deviceId']
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查找卡密
        cursor.execute('''
        SELECT id, key_value, is_active, expires_at, max_devices, used_count 
        FROM activation_keys 
        WHERE key_value = %s
        ''', (key,))
        
        key_data = cursor.fetchone()
        
        # 如果卡密不存在
        if not key_data:
            return jsonify({'valid': False, 'message': '卡密无效'}), 200
        
        # 如果卡密已禁用
        if not key_data['is_active']:
            return jsonify({'valid': False, 'message': '卡密已被禁用'}), 200
        
        # 如果卡密已过期
        if key_data['expires_at'] and key_data['expires_at'] < datetime.datetime.now():
            return jsonify({'valid': False, 'message': '卡密已过期'}), 200
        
        # 检查设备绑定
        cursor.execute('''
        SELECT id FROM device_bindings 
        WHERE key_id = %s AND device_id = %s
        ''', (key_data['id'], device_id))
        
        binding = cursor.fetchone()
        
        # 如果设备已绑定，更新验证时间
        if binding:
            cursor.execute('''
            UPDATE device_bindings 
            SET last_verified = CURRENT_TIMESTAMP 
            WHERE id = %s
            ''', (binding['id'],))
            conn.commit()
            return jsonify({'valid': True, 'message': '验证成功'}), 200
        
        # 检查是否达到最大设备数
        cursor.execute('''
        SELECT COUNT(*) as count FROM device_bindings 
        WHERE key_id = %s
        ''', (key_data['id'],))
        
        device_count = cursor.fetchone()['count']
        
        if device_count >= key_data['max_devices']:
            return jsonify({'valid': False, 'message': '已达到最大设备数'}), 200
        
        # 新增设备绑定
        cursor.execute('''
        INSERT INTO device_bindings (key_id, device_id) 
        VALUES (%s, %s)
        ''', (key_data['id'], device_id))
        
        # 更新使用次数
        cursor.execute('''
        UPDATE activation_keys 
        SET used_count = used_count + 1 
        WHERE id = %s
        ''', (key_data['id'],))
        
        conn.commit()
        return jsonify({'valid': True, 'message': '验证成功'}), 200
        
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'valid': False, 'message': '服务器错误'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 管理员API：创建卡密
@app.route('/api/admin/create-key', methods=['POST'])
@admin_required
def create_key():
    data = request.json
    
    # 生成卡密
    if 'key' in data and data['key']:
        key = data['key']
    else:
        # 使用自定义长度生成卡密
        key_length = data.get('key_length', 16)
        key = generate_key(key_length)
        
    expires_at = data.get('expires_at')  # 格式: YYYY-MM-DDTHH:MM
    max_devices = data.get('max_devices', 1)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        if expires_at:
            cursor.execute('''
            INSERT INTO activation_keys (key_value, expires_at, max_devices) 
            VALUES (%s, %s, %s)
            ''', (key, expires_at, max_devices))
        else:
            cursor.execute('''
            INSERT INTO activation_keys (key_value, max_devices) 
            VALUES (%s, %s)
            ''', (key, max_devices))
        
        conn.commit()
        return jsonify({'success': True, 'key': key}), 201
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'创建卡密失败: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 管理员API：获取所有卡密
@app.route('/api/admin/keys', methods=['GET'])
@admin_required
def get_keys():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
        SELECT id, key_value, is_active, created_at, expires_at, max_devices, used_count 
        FROM activation_keys
        ''')
        
        keys = cursor.fetchall()
        
        # 转换日期时间为字符串
        for key in keys:
            key['created_at'] = key['created_at'].isoformat() if key['created_at'] else None
            key['expires_at'] = key['expires_at'].isoformat() if key['expires_at'] else None
        
        return jsonify({'success': True, 'keys': keys}), 200
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'获取卡密失败: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 管理员API：停用卡密
@app.route('/api/admin/deactivate-key', methods=['POST'])
@admin_required
def deactivate_key():
    data = request.json
    if 'key' not in data:
        return jsonify({'success': False, 'message': '请求参数不完整'}), 400
    
    key = data.get('key')
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE activation_keys 
        SET is_active = FALSE 
        WHERE key_value = %s
        ''', (key,))
        
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '卡密不存在'}), 404
        
        return jsonify({'success': True, 'message': '卡密已停用'}), 200
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'停用卡密失败: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 管理员API：删除卡密
@app.route('/api/admin/delete-key', methods=['POST'])
@admin_required
def delete_key():
    data = request.json
    if 'key' not in data:
        return jsonify({'success': False, 'message': '请求参数不完整'}), 400
    
    key = data.get('key')
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 删除卡密时会自动删除关联的设备绑定记录（因为设置了ON DELETE CASCADE）
        cursor.execute('''
        DELETE FROM activation_keys 
        WHERE key_value = %s
        ''', (key,))
        
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '卡密不存在'}), 404
        
        return jsonify({'success': True, 'message': '卡密已删除'}), 200
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'删除卡密失败: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 管理员登录页面
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_token'] = ADMIN_TOKEN  # 保存管理员令牌到session
            return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

# 管理员面板
@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # 渲染管理面板
    return render_template('admin.html', admin_token=ADMIN_TOKEN)

# 登出
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_token', None)  # 清除管理员令牌
    return redirect(url_for('admin_login'))

# 提供模板文件
@app.route('/')
def index():
    return redirect(url_for('admin_login'))

# 管理员API：获取设备绑定信息
@app.route('/api/admin/devices', methods=['GET'])
@admin_required
def get_devices():
    key_value = request.args.get('key')
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        if key_value:
            # 查询特定卡密的设备绑定
            cursor.execute('''
            SELECT d.id, d.device_id, d.last_verified, a.key_value, a.is_active, a.expires_at,
                   (SELECT COUNT(*) FROM device_bindings WHERE key_id = a.id) as device_count,
                   a.max_devices
            FROM device_bindings d
            JOIN activation_keys a ON d.key_id = a.id
            WHERE a.key_value = %s
            ORDER BY d.last_verified DESC
            ''', (key_value,))
        else:
            # 查询所有设备绑定
            cursor.execute('''
            SELECT d.id, d.device_id, d.last_verified, a.key_value, a.is_active, a.expires_at,
                   (SELECT COUNT(*) FROM device_bindings WHERE key_id = a.id) as device_count,
                   a.max_devices
            FROM device_bindings d
            JOIN activation_keys a ON d.key_id = a.id
            ORDER BY d.last_verified DESC
            ''')
        
        devices = cursor.fetchall()
        
        # 转换日期时间为字符串
        for device in devices:
            device['last_verified'] = device['last_verified'].isoformat() if device['last_verified'] else None
            device['expires_at'] = device['expires_at'].isoformat() if device['expires_at'] else None
        
        return jsonify({'success': True, 'devices': devices}), 200
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'获取设备信息失败: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 管理员API：解除设备绑定
@app.route('/api/admin/unbind-device', methods=['POST'])
@admin_required
def unbind_device():
    data = request.json
    if 'device_id' not in data:
        return jsonify({'success': False, 'message': '请求参数不完整'}), 400
    
    device_id = data.get('device_id')
    key_value = data.get('key')
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        if key_value:
            # 解除特定卡密的特定设备绑定
            cursor.execute('''
            DELETE d FROM device_bindings d
            JOIN activation_keys a ON d.key_id = a.id
            WHERE d.device_id = %s AND a.key_value = %s
            ''', (device_id, key_value))
        else:
            # 解除所有卡密中的特定设备绑定
            cursor.execute('''
            DELETE FROM device_bindings 
            WHERE device_id = %s
            ''', (device_id,))
        
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '未找到匹配的设备绑定'}), 404
        
        return jsonify({'success': True, 'message': '设备绑定已解除'}), 200
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'解除设备绑定失败: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 添加设备管理页面路由
@app.route('/admin/devices')
def admin_devices():
    if 'admin_token' not in session:
        return redirect(url_for('admin_login'))
    return render_template('devices.html', admin_token=session.get('admin_token', ''))

# 接收用户信息API
@app.route('/api/user-info', methods=['POST'])
def receive_user_info():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': '请求体为空'}), 400
            
        print(f"收到用户信息请求: {data}")
            
        if 'deviceId' not in data or 'userInfo' not in data:
            return jsonify({'success': False, 'message': '请求参数不完整'}), 400
        
        device_id = data['deviceId']
        user_info = data['userInfo']
        key = data.get('key')
        timestamp = data.get('timestamp')  # 获取客户端提供的时间戳
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查找卡密ID
        key_id = None
        if key:
            cursor.execute('SELECT id FROM activation_keys WHERE key_value = %s', (key,))
            key_result = cursor.fetchone()
            if key_result:
                key_id = key_result['id']
        
        # 检查用户信息是否已存在
        cursor.execute('SELECT id FROM user_info WHERE device_id = %s', (device_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # 更新现有用户信息
            update_query = '''
            UPDATE user_info SET 
                key_id = %s,
                username = %s,
                real_name = %s,
                user_identity = %s,
                identity = %s,
                phone = %s,
                school_province = %s,
                department_name = %s,
                edu_background = %s,
                edu_entry_year = %s,
                student_id = %s,
                user_school_id = %s,
                school_name = %s,
                updated_at = %s
            WHERE device_id = %s
            '''
            
            # 处理edu_entry_year，确保为整数或NULL
            edu_entry_year = user_info.get('edu_entry_year')
            if edu_entry_year == '' or edu_entry_year is None:
                edu_entry_year = None
            else:
                try:
                    edu_entry_year = int(edu_entry_year)
                except (ValueError, TypeError):
                    edu_entry_year = None
                    
            # 处理user_school_id，确保为整数或NULL
            user_school_id = user_info.get('user_school_id')
            if user_school_id == '' or user_school_id is None:
                user_school_id = None
            else:
                try:
                    user_school_id = int(user_school_id)
                except (ValueError, TypeError):
                    user_school_id = None
            
            # 使用客户端提供的时间戳或当前时间
            updated_at = datetime.datetime.now()
            if timestamp:
                try:
                    updated_at = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass  # 如果时间戳格式不正确，使用当前时间
            
            cursor.execute(update_query, (
                key_id,
                user_info.get('username'),
                user_info.get('real_name'),
                user_info.get('user_identity'),
                user_info.get('identity'),
                user_info.get('phone'),
                user_info.get('school_province'),
                user_info.get('department_name'),
                user_info.get('edu_background'),
                edu_entry_year,
                user_info.get('student_id'),
                user_school_id,
                user_info.get('school_name'),
                updated_at,
                device_id
            ))
            
            conn.commit()
            return jsonify({'success': True, 'message': '用户信息已更新'}), 200
        else:
            # 插入新用户信息
            insert_query = '''
            INSERT INTO user_info (
                device_id, key_id, username, real_name, user_identity, 
                identity, phone, school_province, department_name, 
                edu_background, edu_entry_year, student_id, 
                user_school_id, school_name, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            # 处理edu_entry_year，确保为整数或NULL
            edu_entry_year = user_info.get('edu_entry_year')
            if edu_entry_year == '' or edu_entry_year is None:
                edu_entry_year = None
            else:
                try:
                    edu_entry_year = int(edu_entry_year)
                except (ValueError, TypeError):
                    edu_entry_year = None
                    
            # 处理user_school_id，确保为整数或NULL
            user_school_id = user_info.get('user_school_id')
            if user_school_id == '' or user_school_id is None:
                user_school_id = None
            else:
                try:
                    user_school_id = int(user_school_id)
                except (ValueError, TypeError):
                    user_school_id = None
            
            # 使用客户端提供的时间戳或当前时间
            current_time = datetime.datetime.now()
            if timestamp:
                try:
                    current_time = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass  # 如果时间戳格式不正确，使用当前时间
            
            cursor.execute(insert_query, (
                device_id,
                key_id,
                user_info.get('username'),
                user_info.get('real_name'),
                user_info.get('user_identity'),
                user_info.get('identity'),
                user_info.get('phone'),
                user_info.get('school_province'),
                user_info.get('department_name'),
                user_info.get('edu_background'),
                edu_entry_year,
                user_info.get('student_id'),
                user_school_id,
                user_info.get('school_name'),
                current_time,
                current_time
            ))
            
            conn.commit()
            return jsonify({'success': True, 'message': '用户信息已保存'}), 201
            
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'保存用户信息失败: {str(e)}'}), 500
    except Exception as e:
        print(f"处理用户信息时出现未知错误: {e}")
        return jsonify({'success': False, 'message': f'处理用户信息失败: {str(e)}'}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# 管理员API：获取用户信息
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
        SELECT u.*, a.key_value 
        FROM user_info u
        LEFT JOIN activation_keys a ON u.key_id = a.id
        ORDER BY u.updated_at DESC
        ''')
        
        users = cursor.fetchall()
        
        # 转换日期时间为字符串
        for user in users:
            user['created_at'] = user['created_at'].isoformat() if user['created_at'] else None
            user['updated_at'] = user['updated_at'].isoformat() if user['updated_at'] else None
        
        return jsonify({'success': True, 'users': users}), 200
    except Error as e:
        print(f"数据库错误: {e}")
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 添加用户管理页面路由
@app.route('/admin/users')
def admin_users():
    if 'admin_token' not in session:
        return redirect(url_for('admin_login'))
    return render_template('users.html', admin_token=session.get('admin_token', ''))

if __name__ == '__main__':
    init_db()  # 初始化数据库
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    ) 