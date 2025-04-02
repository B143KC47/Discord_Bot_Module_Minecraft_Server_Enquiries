# Discord Minecraft服务器查询机器人

一个用于查询Minecraft服务器状态的Discord机器人模块。

中文 | [English](README.md)

![Discord Bot](https://img.shields.io/badge/Discord-机器人-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Minecraft](https://img.shields.io/badge/Minecraft-62B47A?style=for-the-badge&logo=minecraft&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 功能
- ✅ 检查Minecraft服务器状态(在线/离线)
- 👥 获取玩家数量和列表
- 📊 查询服务器版本和MOTD信息
- 🔄 支持配置多个Minecraft服务器
- 💬 美观的Discord嵌入消息

## 要求
- Python 3.8+
- Discord机器人令牌
- Minecraft服务器地址

## 安装
1. 克隆本仓库
2. 安装依赖: `pip install -r requirements.txt`
3. 复制`.env.example`为`.env`并配置您的设置
4. 在`server_info.json`中配置您的Minecraft服务器信息
5. 运行机器人: `python main.py`

## 配置

### Discord机器人设置
编辑`.env`文件:
- `DISCORD_TOKEN`: 您的Discord机器人令牌
- `TEST_GUILD_ID`: (可选) 用于测试/开发的服务器ID

### Minecraft服务器设置
编辑`server_info.json`文件，添加您的服务器信息:
```json
[
  {"ip":"play.example.com", "Name": "我的Minecraft服务器"},
  {"ip":"mc.example.org", "Name": "另一个MC服务器"}
]
```

## 命令
- `/ip`: 显示所有配置的Minecraft服务器状态

## 项目结构
```
├── main.py              # 机器人初始化
├── cogs/
│   └── status_cog.py    # 服务器状态命令实现
├── utils/
│   └── config_loader.py # 配置工具
├── server_info.json     # 服务器配置
└── .env                 # 环境变量
```

## 支持
如有问题或功能请求，请在GitHub上提交issue。

## 许可证
MIT