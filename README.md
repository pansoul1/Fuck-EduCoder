# Fuck EduCoder

![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.1-blue)

> ### ⚠️ **重要说明：此脚本仅适用于 EduCoder 平台的考试功能！**

Fuck EduCoder 是一个浏览器油猴脚本，用于改善 EduCoder 平台上的学习体验。脚本通过禁用监控功能、支持题目提取和 AI 辅助答案生成等功能，帮助学生更有效地完成课程作业。

> ⚠️ **免责声明**：本项目仅供学习和研究使用。使用本项目请遵守相关法律法规和教育机构的规定。滥用本工具可能导致违反学校政策或学术不端行为。

## 🙏 作者的话

这是一个代码质量不高、结构不够优美的项目。它是我为了应对学校不太合理的期末考试监控机制而匆忙开发的，开发过程中也借助了AI的帮助。由于我已经结束了头歌平台的考试，后续维护和更新可能不会很频繁，还望大家见谅。

我希望这个工具能在关键时刻帮到有需要的同学，但也真诚地建议大家：**尽量不要依赖工具作弊，好好复习才是正道**。只有在实在没有时间准备的情况下，这个工具或许能帮你渡过难关。

感谢大家对这个简陋项目的包容和支持！

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

## 📋 项目结构

```
Fuck EduCoder/
└── Fuck EduCoder.js    # 油猴脚本主文件
```

## ⚙️ 安装指南

### 油猴脚本安装

1. 安装 [Tampermonkey](https://www.tampermonkey.net/) 浏览器扩展
2. 在浏览器的扩展管理页面中开启"开发者模式"
   - Chrome浏览器：访问 chrome://extensions/ 并打开右上角的开发者模式
   - Edge浏览器：访问 edge://extensions/ 并打开左下角的开发者模式
   - Firefox浏览器：访问 about:addons，点击扩展，然后点击设置齿轮图标
3. 点击 Tampermonkey 图标 → 创建新脚本
4. 复制 `Fuck EduCoder.js` 的内容，粘贴并保存

## 🔧 使用说明

### 脚本使用

1. 访问 EduCoder 平台时，脚本会自动运行
2. 脚本将自动禁用监控功能
3. 在考试/练习页面点击"提取题目"按钮获取题目
4. 点击"AI设置"配置 AI 接口和自动生成答案的选项

### AI 模型配置

脚本支持两种AI模型接口：豆包和DeepSeek。

- **豆包API**：[https://www.volcengine.com/product/doubao/](https://www.volcengine.com/product/doubao/)
  - 推荐使用，有免费额度
  - 如需更快的响应速度，可以在设置中关闭"深度思考"功能

- **DeepSeek API**：[https://platform.deepseek.com/usage](https://platform.deepseek.com/usage)

在脚本面板的"AI设置"中，您可以选择使用哪个模型，并输入对应的API密钥。获取API密钥需要在上述网站注册账号并申请。

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

**Q: 脚本无法正常运行怎么办？**  
A: 请确保使用最新版本的脚本，并检查浏览器控制台是否有错误信息。某些网站可能更新了防护机制导致脚本失效。

**Q: 我可以使用自己的 AI 接口吗？**  
A: 是的，点击脚本界面中的"AI设置"按钮，输入您的 API 密钥即可。 