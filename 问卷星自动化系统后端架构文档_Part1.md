 # 问卷星自动化系统后端架构文档（一）：系统架构与核心模块

## 1. 系统架构概述

问卷星自动化系统采用模块化、分层架构设计，遵循关注点分离原则，将不同功能组件解耦，提高系统维护性和扩展性。系统主要分为以下几个层次：

### 1.1 系统架构图

```
┌───────────────────────────────────────────────────────────────┐
│                         API 层                                │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│ │ 问卷API路由  │  │  任务API路由 │  │      配置API路由       │ │
│ └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                           ▲
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                         服务层                                │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│ │   问卷服务   │  │   任务服务   │  │      配置服务          │ │
│ └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                           ▲
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                         核心层                                │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │
│ │  问卷解析器  │  │ 提交处理器  │  │ LLM生成器  │  │ 验证器 │ │
│ └─────────────┘  └─────────────┘  └─────────────┘  └────────┘ │
└───────────────────────────────────────────────────────────────┘
                           ▲
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                         工具层                                │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│ │  IP追踪器   │  │ JSON编码器  │  │      其他工具          │ │
│ └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                           ▲
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                        配置和数据                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│ │  配置模块   │  │  数据存储   │  │      日志系统          │ │
│ └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 架构特点

1. **模块化设计**：系统由多个功能独立的模块组成，每个模块专注于特定功能
2. **分层架构**：清晰的分层结构，降低各层间耦合度
3. **RESTful API**：基于Flask实现标准化的RESTful API接口
4. **线程池**：使用线程池处理并发任务，提高系统吞吐量
5. **配置驱动**：系统行为由配置驱动，支持动态调整
6. **日志完备**：全面的日志记录，支持问题排查和系统监控

## 2. 代码组织结构

项目目录结构清晰，按功能模块和层次组织：

```
backend/
│
├── app.py                # 应用入口
├── config.py             # 全局配置
│
├── core/                 # 核心功能模块
│   ├── __init__.py
│   ├── parser.py         # 问卷解析器
│   ├── wjx.py            # 问卷星提交器
│   ├── llm_generator.py  # LLM答案生成器
│   └── verification.py   # 验证工具
│
├── services/             # 服务层
│   ├── __init__.py
│   ├── survey_service.py # 问卷服务
│   └── task_service.py   # 任务服务
│
├── routes/               # API路由层
│   ├── __init__.py
│   ├── survey_routes.py  # 问卷API路由
│   ├── task_routes.py    # 任务API路由
│   └── config_routes.py  # 配置API路由
│
├── utils/                # 工具类
│   ├── __init__.py
│   ├── ip_tracker.py     # IP跟踪器
│   └── json_encoder.py   # JSON编码器
│
├── data/                 # 数据存储
│   ├── surveys/          # 问卷数据
│   └── tasks/            # 任务数据
│
└── logs/                 # 日志文件
    ├── api/              # API日志
    └── tasks/            # 任务执行日志
```

## 3. 核心组件详解

### 3.1 应用入口 (app.py)

`app.py` 是系统的入口点，负责初始化Flask应用、配置日志、注册路由和启动服务器。

**主要功能**：
- 创建并配置Flask应用
- 设置跨域资源共享(CORS)
- 注册API路由蓝图
- 初始化应用所需目录
- 配置日志系统
- 启动Web服务器

**关键代码**：

```python
# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 导入路由
from routes.survey_routes import survey_bp
from routes.task_routes import task_bp
from routes.config_routes import config_bp

# 注册路由蓝图
app.register_blueprint(survey_bp, url_prefix='/api/surveys')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(config_bp, url_prefix='/api/config')

@app.route('/')
def index():
    """API根路径，返回服务状态信息"""
    return jsonify({
        "name": "问卷星自动化系统API",
        "version": "1.0.0",
        "status": "运行中"
    })
```

### 3.2 配置模块 (config.py)

`config.py` 是系统的全局配置中心，负责管理系统的各项配置，包括文件路径、API密钥和代理设置等。

**主要功能**：
- 定义应用的全局配置
- 管理文件存储路径
- 配置LLM API密钥
- 管理代理配置
- 提供配置获取接口

**关键代码**：

```python
class Config:
    """应用程序配置类，包含所有全局配置项"""
    
    # 基础目录 - 使用绝对路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 数据存储目录
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # 日志目录
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # 问卷数据存储目录
    SURVEYS_DIR = os.path.join(DATA_DIR, 'surveys')
    
    # 任务数据存储目录
    TASKS_DIR = os.path.join(DATA_DIR, 'tasks')
    
    # LLM配置
    LLM_API_KEYS = {
        'openai': os.environ.get('OPENAI_API_KEY', ''),
        'zhipu': os.environ.get('ZHIPU_API_KEY', ''),
        'baidu': os.environ.get('BAIDU_API_KEY', '')
    }
    
    # 代理配置
    USE_PROXY = os.environ.get('USE_PROXY', 'False').lower() in ('true', 'yes', '1', 't')
    DEFAULT_PROXY_URL = os.environ.get('DEFAULT_PROXY_URL', '')
    
    def __init__(self):
        """初始化配置，创建必要的目录"""
        # 确保目录存在
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs(self.SURVEYS_DIR, exist_ok=True)
        os.makedirs(self.TASKS_DIR, exist_ok=True)
```

### 3.3 核心层 (core/)

核心层包含系统的核心功能实现，是系统的业务处理中心。

#### 3.3.1 问卷解析器 (parser.py)

`parser.py` 负责从问卷星URL解析问卷结构和内容。

**主要功能**：
- 从URL获取问卷HTML内容
- 解析HTML提取问卷结构
- 识别不同类型的问题
- 提取题目和选项
- 将解析结果保存为标准格式

**关键数据结构**：

```python
@dataclass
class Question:
    """问卷题目数据结构"""
    index: int          # 实际题号
    type: int           # 题型
    title: str          # 题目
    title_index: int    # 题目题号
    options: Union[List[str], List[List[str]], None] = None  # 选项
    ratio: Union[List[int], List[List[int]], None] = None    # 概率分布
    is_hidden: bool = False  # 是否隐藏
    relation: Optional[Tuple[int, int]] = None  # 关联逻辑
    jumps: Optional[List[Tuple[int, int]]] = None  # 跳题逻辑
```

**关键函数**：

```python
def parse_survey(url):
    """解析问卷调查"""
    # 获取HTML内容
    response = session.get(url, headers=headers, timeout=15)
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取标题
    title_element = soup.find('title')
    title = title_element.text.strip() if title_element else "未知标题"
    
    # 提取问题列表
    questions = []
    question_elements = soup.select('div.field')
    
    # 遍历问题元素
    for index, q_elem in enumerate(question_elements):
        question_data = extract_question(q_elem, index)
        if question_data:
            questions.append(question_data)
    
    # 构建问卷数据
    survey_data = {
        "id": extract_survey_id(url),
        "title": title,
        "questions": questions
    }
    
    return survey_data
```

#### 3.3.2 问卷提交器 (wjx.py)

`wjx.py` 封装了问卷星问卷提交的核心逻辑。

**主要功能**：
- 从页面获取提交所需参数
- 构建和加密提交数据
- 发送HTTP请求提交问卷
- 处理提交响应和错误

**关键函数**：

```python
def submit(self, submit_data=None, proxy=None):
    """提交问卷"""
    # 获取jqnonce
    jqnonce = self.get_jqnonce()
    
    # 计算提交参数
    ktimes = self.get_ktimes(questions_count)
    starttime = self.get_starttime()
    
    # 构建请求参数
    params = {
        'shortid': self.survey_id,
        'starttime': starttime,
        'ktimes': f'{ktimes}',
        'jqnonce': jqnonce,
        'jqsign': self.dataenc(jqnonce, ktimes),
    }
    
    # 构建提交数据
    data = {
        'submitdata': submit_data,
    }
    
    # 发送POST请求
    response = requests.post(
        'https://www.wjx.cn/joinnew/processjq.ashx', 
        params=params, 
        cookies=self.cookies, 
        headers=self.headers, 
        data=data,
        proxies=proxy
    )
    
    # 处理响应
    result_text = response.text
    success = '10' in result_text or '提交成功' in result_text
    
    return {"success": success, "message": result_text, "response": result_text}
```

#### 3.3.3 LLM答案生成器 (llm_generator.py)

`llm_generator.py` 集成了大语言模型API，用于生成更智能的问卷答案。

**主要功能**：
- 构建LLM提示词
- 调用不同厂商的LLM API（阿里云、百度、智谱、OpenAI）
- 解析LLM返回的答案
- 转换为问卷提交格式

**关键函数**：

```python
def generate_answers(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
    """为整个问卷生成答案"""
    # 构建提示词
    prompt = self._build_prompt(question_data)
    
    # 调用LLM API
    response = self._call_llm_api(prompt)
    
    # 解析响应
    answers = self._parse_response(response, question_data)
    
    return answers

def _call_llm_api(self, prompt: str) -> str:
    """调用不同的LLM API"""
    if self.model_type == "aliyun":
        return self._call_aliyun(prompt)
    elif self.model_type == "openai":
        return self._call_openai(prompt)
    elif self.model_type == "zhipu":
        return self._call_zhipu(prompt)
    elif self.model_type == "baidu":
        return self._call_baidu(prompt)
    else:
        raise ValueError(f"不支持的模型类型: {self.model_type}")
```

## 4. 服务层 (services/)

服务层负责业务逻辑的处理，协调核心层组件，并向API层提供服务。

### 4.1 问卷服务 (survey_service.py)

`survey_service.py` 提供问卷相关的服务功能。

**主要功能**：
- 解析和存储问卷
- 管理问卷索引
- 获取问卷列表和详情
- 删除问卷

**关键函数**：

```python
def parse_survey(self, url):
    """解析问卷并存储"""
    # 调用核心层解析问卷
    survey_result = parse_survey(url)
    
    # 处理解析结果
    survey_id = survey_result.get('id')
    survey_title = survey_result.get('title')
    questions = survey_result.get('questions')
    
    # 保存问卷数据
    file_path = os.path.join(self.surveys_dir, f"{survey_id}_{timestamp}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(survey_data, f, ensure_ascii=False, indent=2)
    
    # 更新索引
    index_entry = {
        "id": survey_id,
        "title": survey_title,
        "url": url,
        "created_at": timestamp,
        "file_path": file_path
    }
    
    return survey_data
    
def get_survey_by_id(self, survey_id):
    """根据ID获取问卷内容"""
    # 先检查缓存
    if survey_id in self.survey_cache:
        return self.survey_cache[survey_id]
    
    # 查找问卷文件
    for filename in os.listdir(self.surveys_dir):
        if survey_id in filename and filename.endswith('.json'):
            file_path = os.path.join(self.surveys_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                survey_data = json.load(f)
                
            # 添加到缓存
            self.survey_cache[survey_id] = survey_data
            return survey_data
    
    return None
```

### 4.2 任务服务 (task_service.py)

`task_service.py` 是系统的核心服务，负责任务的创建、执行和管理。

**主要功能**：
- 创建和管理任务
- 启动后台线程执行任务
- 生成问卷答案
- 提交问卷
- 更新任务状态和进度
- 控制任务执行

**关键函数**：

```python
def create_task(self, task_data):
    """创建新任务"""
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 验证必需字段
    if 'survey_id' not in task_data or 'count' not in task_data:
        raise ValueError("必须提供survey_id和count字段")
    
    # 构建任务数据
    task = {
        "id": task_id,
        "survey_id": task_data['survey_id'],
        "count": int(task_data.get('count', 1)),
        "use_llm": task_data.get('use_llm', False),
        "use_proxy": task_data.get('use_proxy', False),
        "proxy_url": task_data.get('proxy_url', ''),
        "status": "pending",
        "progress": 0,
        "success_count": 0,
        "fail_count": 0,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 保存任务数据
    with open(os.path.join(self.tasks_dir, f"{task_id}.json"), 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    
    # 更新索引
    self.index.append({
        "id": task_id,
        "survey_id": task['survey_id'],
        "status": task['status'],
        "created_at": task['created_at']
    })
    self._save_index()
    
    # 启动后台线程执行任务
    thread = threading.Thread(
        target=self._submit_task,
        args=(task_id, task),
        daemon=True
    )
    self.running_tasks[task_id] = thread
    thread.start()
    
    return task_id
```

## 5. API层 (routes/)

API层通过RESTful接口向外部提供服务，是用户与系统交互的接口。

### 5.1 问卷API路由 (survey_routes.py)

`survey_routes.py` 提供问卷相关的HTTP API。

**主要接口**：
- `/api/surveys/parse` (POST): 解析问卷
- `/api/surveys` (GET): 获取所有问卷
- `/api/surveys/<survey_id>` (GET): 获取指定问卷
- `/api/surveys/<survey_id>` (DELETE): 删除问卷

**示例接口**：

```python
@survey_bp.route('/parse', methods=['POST'])
def parse_survey():
    """解析问卷API"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "请提供问卷URL", "code": 400}), 400
        
        url = data['url']
        
        # 调用服务层解析问卷
        survey = survey_service.parse_survey(url)
        return jsonify({"data": survey, "code": 200, "message": "问卷解析成功"})
    except Exception as e:
        return jsonify({"error": str(e), "code": 500, "message": "问卷解析失败"}), 500
```

### 5.2 任务API路由 (task_routes.py)

`task_routes.py` 提供任务管理相关的HTTP API。

**主要接口**：
- `/api/tasks` (POST): 创建任务
- `/api/tasks` (GET): 获取任务列表
- `/api/tasks/<task_id>` (GET): 获取任务详情
- `/api/tasks/<task_id>/status` (PUT): 更新任务状态
- `/api/tasks/<task_id>/pause` (POST): 暂停任务
- `/api/tasks/<task_id>/resume` (POST): 恢复任务
- `/api/tasks/<task_id>/stop` (POST): 停止任务
- `/api/tasks/<task_id>/refresh` (POST): 刷新任务状态
- `/api/tasks/<task_id>` (DELETE): 删除任务

**示例接口**：

```python
@task_bp.route('', methods=['POST'])
def create_task():
    """创建新任务"""
    data = request.json
    required_fields = ['survey_id', 'count']
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        task_id = task_service.create_task(data)
        return jsonify({"task_id": task_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```