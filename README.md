# PandaAI工具管理助手 V2.0

这是一个功能完整的图形界面工具，帮助你快速部署和管理完整的PandaAI量化生态系统，包括PandaFactor和PandaQuantFlow项目。

## 🎯 主要功能

- 🖥️ **现代化图形界面** - 分页式设计，操作更直观
- 🔄 **双项目支持** - 同时管理PandaFactor和QuantFlow
- 🗄️ **数据库集成** - 自动配置和启动MongoDB数据库
- 🔧 **智能环境管理** - 自动创建和配置conda环境
- 📥 **自动化部署** - 从GitHub自动克隆和更新项目
- 📦 **依赖管理** - 智能安装和管理所有Python包
- 📊 **状态监控** - 实时显示服务器和环境状态
- 🚀 **一键启动** - 自动启动所有服务（MongoDB、Factor、QuantFlow）
- 🌐 **快捷访问** - 内置数据操作和工作流管理功能

## 📋 系统要求

在使用这个工具之前，请确保你的电脑已经安装了：

### 必需软件
1. **Python 3.11+** - [下载地址](https://www.python.org/downloads/)
2. **Git** - [下载地址](https://git-scm.com/downloads)
3. **Conda** - [Anaconda](https://www.anaconda.com/products/distribution) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### 可选组件
4. **MongoDB** - 用于数据存储，可通过工具配置路径
5. **足够的磁盘空间** - 建议至少5GB可用空间

## 🚀 快速开始

### 方法一：直接运行（推荐）

1. 下载 `panda_deploy_tool_v2.py` 文件
2. 双击运行，或者在命令行中执行：
   ```bash
   python panda_deploy_tool_v2.py
   ```

### 方法二：使用conda环境

1. 创建新的conda环境：
   ```bash
   conda create -n pandaaitool python=3.12 -y
   conda activate pandaaitool
   ```

2. 运行工具：
   ```bash
   python panda_deploy_tool_v2.py
   ```

## 📖 使用说明

### 界面介绍

工具采用现代化的分页设计，包含三个主要页面：

#### 📦 项目部署页面
- **项目配置区域**
  - Factor Git地址配置
  - QuantFlow Git地址配置
  - 安装路径选择
  - Conda环境设置
  - MongoDB路径配置

- **部署状态监控**
  - Git状态指示器
  - Conda环境状态
  - Python环境检查
  - 项目文件状态
  - MongoDB连接状态

- **操作按钮**
  - 🚀 开始部署
  - 🔄 检查更新
  - 🗑️ 清除状态

- **实时日志**
  - 详细的部署过程
  - 进度条显示
  - 错误和警告提示

#### 🚀 项目启动页面
- **环境状态检查**
  - 实时状态指示器（绿色/红色）
  - 项目信息显示

- **启动控制**
  - 🚀 启动项目（MongoDB + Factor + QuantFlow）
  - 🛑 停止项目
  - 🌐 打开浏览器
  - 🔄 刷新状态

- **服务器状态**
  - 显示当前运行状态

- **启动日志**
  - 实时启动过程记录

#### ⚙️ 数据操作页面
- **Factor数据功能**
  - 📈 数据更新
  - 📋 数据列表

- **QuantFlow工作流**
  - 📈 超级图表
  - 🔗 工作流管理

- **服务器状态检查**
  - 自动检测服务可用性

- **操作日志**
  - 记录所有操作历史

### 操作步骤

#### 第一步：项目部署

1. **配置项目信息**
   - 设置Factor Git地址（默认已配置）
   - 设置QuantFlow Git地址（默认已配置）
   - 选择安装路径
   - 设置Conda环境名称
   - 配置MongoDB安装路径

2. **开始部署**
   - 点击"🚀 开始部署"按钮
   - 等待部署完成（通常需要5-15分钟）
   - 观察实时日志了解进度

3. **部署完成**
   - 所有状态指示器变为绿色
   - 部署日志显示"部署完成"

#### 第二步：启动服务

1. **切换到启动页面**
   - 点击"🚀 项目启动"页签

2. **检查环境状态**
   - 确认所有状态指示器为绿色
   - 查看项目信息是否正确

3. **启动所有服务**
   - 点击"🚀 启动项目"按钮
   - 系统会自动启动：
     - MongoDB数据库服务
     - PandaFactor服务器
     - QuantFlow服务器

4. **访问服务**
   - Factor服务器：http://localhost:8111
   - QuantFlow服务器：http://localhost:8000

#### 第三步：使用功能

1. **切换到数据操作页面**
   - 点击"⚙️ 数据操作"页签

2. **使用Factor功能**
   - 点击"📈 数据更新"进行数据管理
   - 点击"📋 数据列表"查看数据

3. **使用QuantFlow功能**
   - 点击"📈 超级图表"使用可视化功能
   - 点击"🔗 工作流"管理量化工作流

## 📁 部署后的文件结构

部署完成后，你的文件结构将如下所示：

```
选择的安装路径/
├── panda_factor/                 # PandaFactor项目主目录
│   ├── panda_common/            # 公共模块
│   ├── panda_data/              # 数据模块
│   ├── panda_data_hub/          # 数据中心模块
│   ├── panda_factor/            # 因子计算模块
│   ├── panda_llm/               # 大模型模块
│   ├── panda_factor_server/     # Factor服务器模块
│   ├── requirements.txt         # Python依赖
│   └── README.md                # 项目说明
├── panda_quantflow/             # QuantFlow项目主目录
│   ├── src/                     # 源代码目录
│   │   ├── panda_server/        # QuantFlow服务器
│   │   ├── panda_plugins/       # 插件系统
│   │   ├── panda_ml/            # 机器学习组件
│   │   └── common/              # 通用工具
│   ├── user_data/               # 用户数据
│   ├── pyproject.toml           # 项目配置
│   └── README.md                # 项目说明
├── 启动PandaAI.bat              # 交互式启动脚本
├── 启动PandaAI服务器.bat        # 直接启动脚本
└── project_status.json          # 项目状态文件
```

## 🔧 高级使用

### 手动激活环境

如果你想手动使用conda环境：

```bash
# 激活环境
conda activate pandaaitool  # 或你设置的环境名

# 启动Factor服务器
cd "你的安装路径\panda_factor"
python panda_factor_server/panda_factor_server/__main__.py

# 启动QuantFlow服务器（新终端窗口）
cd "你的安装路径\panda_quantflow"
python src/panda_server/main.py
```

### 服务端口说明

- **PandaFactor服务器**: http://localhost:8111
  - 数据更新页面: http://localhost:8111/factor/#/datahubdataclean
  - 数据列表页面: http://localhost:8111/factor/#/datahublist

- **QuantFlow服务器**: http://localhost:8000
  - 超级图表: http://localhost:8000/charts/
  - 工作流管理: http://localhost:8000/quantflow/

- **MongoDB数据库**: localhost:27017

### 更新项目

项目更新有两种方式：

1. **使用工具自动更新（推荐）**
   - 在部署页面点击"🔄 检查更新"
   - 如果有更新，重新点击"🚀 开始部署"

2. **手动更新**
   ```bash
   # 更新Factor项目
   cd "你的安装路径\panda_factor"
   git pull
   
   # 更新QuantFlow项目
   cd "你的安装路径\panda_quantflow" 
   git pull
   
   # 重新安装依赖（如有需要）
   conda activate pandaaitool
   pip install -r requirements.txt
   ```

## ❗ 常见问题

### Q: 提示"Git未安装或不在PATH中"
**A:** 请先安装Git，并确保添加到系统PATH中。重启命令行或重新启动工具。

### Q: 提示"Conda未安装或不在PATH中"
**A:** 请先安装Anaconda或Miniconda，安装时选择"Add to PATH"选项。

### Q: QuantFlow启动失败，显示"... was unexpected at this time"
**A:** 这通常是批处理脚本语法问题，解决方案：
- 确保安装路径中没有特殊字符
- 检查Conda环境名称是否正确
- 尝试手动启动QuantFlow服务器

### Q: MongoDB连接失败
**A:** 可能的解决方案：
- 确保MongoDB路径配置正确
- 检查MongoDB服务是否正常启动
- 确认端口27017未被占用

### Q: 服务器无法访问
**A:** 检查以下几点：
- 确认所有服务都已启动
- 检查防火墙设置
- 确认端口8111和8000未被占用
- 查看启动日志中的错误信息

### Q: 下载速度很慢
**A:** 可能是网络问题，可以尝试：
- 使用VPN
- 配置Git代理
- 多次重试部署

### Q: 依赖安装失败
**A:** 可能的解决方案：
- 检查网络连接
- 更新conda：`conda update conda`
- 更新pip：`pip install --upgrade pip`
- 使用国内pip源
- 确保Python版本为3.11+

### Q: 权限不足
**A:** 尝试以管理员身份运行工具，或选择用户有写权限的目录。

### Q: 状态指示器显示红色
**A:** 根据具体的红色指示器：
- Git状态红色：检查Git安装和网络连接
- Conda状态红色：检查Conda环境配置
- MongoDB状态红色：检查MongoDB路径和服务状态

## 📞 获取帮助

如果遇到问题，你可以：

1. **查看工具日志**
   - 部署日志：查看部署过程中的详细信息
   - 启动日志：查看服务启动过程
   - 操作日志：查看数据操作记录

2. **检查状态指示器**
   - 绿色：正常状态
   - 红色：存在问题，需要处理

3. **参考官方文档**
   - [PandaFactor项目](https://github.com/PandaAI-Tech/panda_factor)
   - [QuantFlow项目](https://github.com/PandaAI-Tech/panda_quantflow)

4. **社区支持**
   - 在GitHub项目页面提交Issue
   - 加入PandaAI交流群获取帮助

## 🆕 版本特性

### V2.0 主要更新
- 🎨 全新的分页式界面设计
- 🔄 双项目支持（Factor + QuantFlow）
- 🗄️ MongoDB数据库集成
- 📊 实时状态监控和指示器
- 🚀 一键启动所有服务
- ⚙️ 内置数据操作和工作流管理
- 💾 状态持久化和断点续传
- 🔧 更智能的错误处理和恢复

## 📄 许可证

本工具遵循MIT许可证，可自由使用和修改。

---

**🐼 PandaAI工具管理助手 V2.0 - 让量化研究更简单！**
