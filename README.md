# Fuck EduCoder

![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.1-blue)

Fuck EduCoder 是一个浏览器油猴脚本和配套服务器系统，用于改善 EduCoder 平台上的学习体验。脚本通过禁用监控功能、支持题目提取和 AI 辅助答案生成等功能，帮助学生更有效地完成课程作业。

> ⚠️ **免责声明**：本项目仅供学习和研究使用。使用本项目请遵守相关法律法规和教育机构的规定。滥用本工具可能导致违反学校政策或学术不端行为。

## 🌟 功能特点

### 油猴脚本功能
- 🛡️ **禁用监控功能**
  - 禁用屏幕监控上报
  - 解除防切屏限制
  - 关闭强制全屏模式
  - 允许使用浏览器开发工具（F12）
- 📝 **题目提取与处理**
  - 提取考试/练习题目
  - 自动识别题目类型与选项
  - 支持复制与保存提取的题目
- 🤖 **AI 辅助解答**
  - 支持 DeepSeek/豆包 AI 接口
  - 自动生成题目答案
  - 可配置 API 密钥和模型设置
- 🔒 **卡密验证系统**
  - 设备绑定和验证机制
  - 支持多设备使用

### 服务端功能
- 📊 **卡密管理系统**
  - 卡密生成与分发
  - 卡密状态管理
  - 设备绑定限制
- 👥 **用户管理**
  - 用户信息收集
  - 设备绑定管理
- 🔐 **管理员面板**
  - 完整的卡密管理
  - 用户数据查看
  - 设备绑定查询与解除

### 📈 用户体验改进计划

为了不断优化脚本功能和提升用户体验，本项目采用匿名化方式收集基本使用数据。这些信息将用于：

- 分析各教育机构的常见题型，优化题目提取算法
- 了解不同地区用户的使用习惯，提供更贴近需求的功能
- 识别常见问题模式，主动修复潜在bug


所有数据均经过严格匿名化处理，仅用于产品功能改进，绝不会用于商业目的或分享给第三方。您的使用即表示对此改进计划的支持，我们感谢您的信任与配合。

## 📋 项目结构

```
Fuck EduCoder/
├── Fuck EduCoder.js    # 油猴脚本主文件
├── key_server.py       # Flask 服务器程序
├── requirements.txt    # Python 依赖列表
└── templates/          # 管理面板 HTML 模板
    ├── admin.html      # 管理员主页面
    ├── devices.html    # 设备管理页面
    ├── login.html      # 登录页面
    └── users.html      # 用户信息页面
```

## ⚙️ 安装指南

### 服务器部署

1. **安装依赖**

```bash
pip install -r requirements.txt
```

2. **创建数据库**

在MySQL中创建一个名为`educoder_keys`的数据库：

```sql
CREATE DATABASE educoder_keys;
```

数据库表结构和配置信息已内置在`key_server.py`中，无需额外配置。

3. **启动服务器**

```bash
python key_server.py
```

对于生产环境，可以使用Gunicorn：

```bash
gunicorn --workers=3 --bind=0.0.0.0:5000 key_server:app
```

建议在生产环境中修改`key_server.py`中的相关配置。

### 油猴脚本安装

1. 安装 [Tampermonkey](https://www.tampermonkey.net/) 浏览器扩展
2. 点击 Tampermonkey 图标 → 创建新脚本
3. 复制 `Fuck EduCoder.js` 的内容，粘贴并保存
4. 在脚本中修改以下配置：
   ```javascript
   AUTH_SERVER_URL: 'https://你的服务器地址/api/verify-key', 
   API_BASE_URL: 'https://你的服务器地址', 
   ```

## 🔧 使用说明

### 脚本使用

1. 访问 EduCoder 平台时，脚本会自动运行
2. 首次使用需要输入有效的卡密进行验证
3. 验证成功后，脚本将自动禁用监控功能
4. 在考试/练习页面点击"提取题目"按钮获取题目
5. 点击"AI设置"配置 AI 接口和自动生成答案的选项

脚本会收集必要的匿名使用数据，仅用于改进功能和用户体验。您可以安心使用，我们重视您的隐私保护。

### 管理员功能

1. 访问 `http://你的服务器地址/admin` 登录管理面板
2. 在管理面板创建和管理卡密
3. 查看用户信息和设备绑定情况
4. 解除设备绑定或停用卡密

## 🔌 API 参考

### 客户端 API

#### 验证卡密

```
POST /api/verify-key
Content-Type: application/json

{
  "key": "XXXX-XXXX-XXXX-XXXX",
  "deviceId": "device_unique_id"
}
```

响应:
```json
{
  "valid": true,
  "message": "验证成功"
}
```

#### 提交用户信息

```
POST /api/user-info
Content-Type: application/json

{
  "key": "XXXX-XXXX-XXXX-XXXX",
  "deviceId": "device_unique_id",
  "userInfo": {
    "username": "用户名",
    "real_name": "真实姓名",
    ...
  }
}
```

### 管理员 API

#### 创建卡密

```
POST /api/admin/create-key
Content-Type: application/json

{
  "admin_token": "your_admin_token",
  "key": "XXXX-XXXX-XXXX-XXXX", // 可选，不提供则自动生成
  "expires_at": "2023-12-31T23:59:59", // 可选
  "max_devices": 2 // 可选，默认为1
}
```

#### 获取卡密列表

```
GET /api/admin/keys?admin_token=your_admin_token
```

更多 API 详情请参考源代码中的注释。

## 📝 自定义与配置

### 客户端配置

在油猴脚本中，您可以修改以下常量：

```javascript
const CONSTANTS = {
    // 服务器配置
    AUTH_SERVER_URL: 'https://你的服务器地址/api/verify-key',
    API_BASE_URL: 'https://你的服务器地址',
    
    // AI 模型配置
    DEEPSEEK_API_URL: 'https://api.deepseek.com/chat/completions',
    DEEPSEEK_MODEL: 'deepseek-chat',
    DOUBAO_API_URL: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    DOUBAO_MODEL: 'doubao-seed-1-6-250615'
};
```

### 服务端配置

如需修改服务器配置，请直接编辑`key_server.py`文件中的相关参数：

```python
# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'educoder_keys'
}

# 管理员配置
ADMIN_USERNAME = 'ADMIN_USERNAME'
ADMIN_PASSWORD = 'ADMIN_PASSWORD'
ADMIN_TOKEN = 'ADMIN_TOKEN'
```

## 🤝 贡献指南

欢迎对本项目进行改进！请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 将您的更改推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 详情请参见 [LICENSE](LICENSE) 文件

## 🧩 常见问题

**Q: 我的卡密无法验证怎么办？**  
A: 请检查卡密是否正确、是否过期、是否已达到最大设备数。如有问题请联系管理员。

**Q: 脚本无法正常运行怎么办？**  
A: 请确保使用最新版本的脚本，并检查浏览器控制台是否有错误信息。某些网站可能更新了防护机制导致脚本失效。

**Q: 如何修改服务器地址？**  
A: 在油猴脚本编辑器中修改 `CONSTANTS.AUTH_SERVER_URL` 和 `CONSTANTS.API_BASE_URL` 的值。

**Q: 我可以使用自己的 AI 接口吗？**  
A: 是的，点击脚本界面中的"AI设置"按钮，输入您的 API 密钥即可。

**Q: 为什么脚本需要收集用户信息？**  
A: 收集匿名化的使用数据有助于我们了解不同教育机构的题型特点和用户使用习惯，从而持续优化算法和功能。所有数据均用于改进产品体验，我们严格保护用户隐私。 