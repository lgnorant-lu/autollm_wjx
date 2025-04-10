# 测试指南

本文档提供问卷星自动化系统的测试策略和具体实施方法。

## 1. 测试策略概述

### 1.1 测试目标

- 确保各个模块正常运行且相互协作
- 验证系统功能符合需求规格
- 检测性能瓶颈和边界条件
- 保障系统整体质量和用户体验

### 1.2 测试类型

系统采用以下测试类型：

- **单元测试**：测试单个函数/组件的功能
- **集成测试**：测试多个组件间的交互
- **端到端测试**：模拟用户行为的完整流程测试
- **性能测试**：测试系统在不同负载下的表现
- **安全测试**：验证系统安全防护措施

### 1.3 测试环境

- **开发环境**：开发人员本地环境
- **测试环境**：独立的测试服务器
- **预生产环境**：与生产环境配置相同，用于最终验证

## 2. 单元测试

### 2.1 后端单元测试

使用pytest框架进行Python代码的单元测试。

#### 测试文件组织

```
backend/
├── tests/
│   ├── unit/
│   │   ├── test_parser.py
│   │   ├── test_wjx.py
│   │   └── ...
│   ├── integration/
│   │   └── ...
│   └── conftest.py
```

#### 编写测试示例

```python
# 测试问卷解析功能
def test_parse_survey():
    html_content = load_test_data("sample_survey.html")
    parser = SurveyParser()
    survey = parser.parse(html_content)
    
    assert survey is not None
    assert survey["title"] == "测试问卷"
    assert len(survey["questions"]) == 5
    assert survey["questions"][0]["type"] == "single_choice"
```

#### 运行测试

```bash
# 运行所有测试
cd backend
pytest

# 运行特定测试文件
pytest tests/unit/test_parser.py

# 运行特定测试函数
pytest tests/unit/test_parser.py::test_parse_survey
```

### 2.2 前端单元测试

使用Jest和Vue Test Utils进行前端单元测试。

#### 测试文件组织

```
frontend/
├── src/
│   └── ...
├── tests/
│   ├── unit/
│   │   ├── components/
│   │   │   └── ...
│   │   └── views/
│   │       └── ...
│   └── setup.js
```

#### 编写测试示例

```javascript
// 测试任务列表组件
import { shallowMount } from '@vue/test-utils'
import TaskList from '@/components/TaskList.vue'

describe('TaskList.vue', () => {
  it('renders tasks when passed', () => {
    const tasks = [
      { id: 1, name: '测试任务1', status: 'running' },
      { id: 2, name: '测试任务2', status: 'completed' }
    ]
    const wrapper = shallowMount(TaskList, {
      props: { tasks }
    })
    expect(wrapper.findAll('.task-item')).toHaveLength(2)
    expect(wrapper.text()).toContain('测试任务1')
  })
})
```

#### 运行测试

```bash
# 运行所有测试
cd frontend
npm test

# 运行特定测试文件
npm test -- tests/unit/components/TaskList.spec.js

# 启用测试覆盖率报告
npm test -- --coverage
```

## 3. 集成测试

### 3.1 API集成测试

测试API端点和数据流。

#### 测试示例

```python
# 测试问卷解析API
def test_survey_parse_api(client):
    response = client.post('/api/v1/surveys', json={
        'url': 'https://www.wjx.cn/vm/sample.aspx'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'id' in data['data']
    assert 'title' in data['data']
```

#### 运行方法

```bash
cd backend
pytest tests/integration/
```

### 3.2 前后端集成测试

测试前端组件与后端API的交互。

#### 使用Mock服务器

```javascript
// 配置API Mock
import { setupServer } from 'msw/node'
import { rest } from 'msw'

const server = setupServer(
  rest.get('/api/v1/surveys', (req, res, ctx) => {
    return res(ctx.json({
      status: 'success',
      data: [
        { id: 'survey-1', title: '测试问卷' }
      ]
    }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## 4. 端到端测试

使用Cypress或Selenium进行端到端测试。

### 4.1 安装Cypress

```bash
cd frontend
npm install cypress --save-dev
```

### 4.2 编写测试用例

```javascript
// cypress/integration/survey_submit.spec.js
describe('Survey Submission', () => {
  it('successfully submits a survey', () => {
    // 登录系统
    cy.visit('/')
    cy.get('#username').type('testuser')
    cy.get('#password').type('password')
    cy.get('button[type="submit"]').click()
    
    // 访问问卷页面
    cy.get('a[href="/surveys"]').click()
    
    // 创建新任务
    cy.get('.create-task-btn').click()
    cy.get('#survey-url').type('https://www.wjx.cn/vm/sample.aspx')
    cy.get('#parse-btn').click()
    
    // 确认问卷已解析
    cy.get('.survey-title', { timeout: 10000 }).should('be.visible')
    
    // 设置任务参数
    cy.get('#submission-count').type('5')
    cy.get('#submit-task-btn').click()
    
    // 验证任务创建成功
    cy.get('.task-success-message').should('be.visible')
    cy.url().should('include', '/tasks/')
  })
})
```

### 4.3 运行测试

```bash
# 打开Cypress测试界面
npx cypress open

# 命令行运行所有测试
npx cypress run
```

## 5. 性能测试

### 5.1 负载测试

使用Locust进行API负载测试。

#### 安装Locust

```bash
pip install locust
```

#### 创建测试脚本

```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def view_surveys(self):
        self.client.get("/api/v1/surveys")
    
    @task(2)
    def parse_survey(self):
        self.client.post("/api/v1/surveys", json={
            "url": "https://www.wjx.cn/vm/sample.aspx"
        })
```

#### 运行测试

```bash
locust -f locustfile.py
```

### 5.2 并发测试

测试系统在多用户同时操作时的表现。

## 6. 安全测试

### 6.1 基本安全检查

- **输入验证测试**：尝试各种非法输入
- **认证测试**：验证未授权访问限制
- **会话管理测试**：检查会话超时和失效策略

### 6.2 自动化安全扫描

使用OWASP ZAP进行自动化安全扫描。

```bash
# 安装ZAP
docker pull owasp/zap2docker-stable

# 运行基本扫描
docker run -v $(pwd):/zap/wrk owasp/zap2docker-stable zap-baseline.py \
  -t http://your-application-url -g gen.conf -r testreport.html
```

## 7. 回归测试

在每次代码变更后，运行自动化测试套件，确保现有功能不受影响。

### 7.1 回归测试流程

1. 对关键路径进行自动化测试
2. 运行单元测试和集成测试
3. 进行端到端测试验证
4. 监控性能指标变化

## 8. 持续集成

### 8.1 CI配置

使用GitHub Actions或Jenkins实现自动化测试。

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest
```

## 9. 测试报告

### 9.1 报告生成

```bash
# 生成HTML测试报告
pytest --html=report.html
```

### 9.2 报告内容

- 测试结果摘要
- 失败测试详情
- 测试覆盖率报告
- 执行时间统计

## 10. 测试数据管理

### 10.1 测试数据准备

- 提供一组标准测试问卷
- 创建模拟API响应数据
- 准备边界条件和异常情况的测试数据

### 10.2 测试数据存储

测试数据存储在`backend/tests/data`和`frontend/tests/data`目录下。 