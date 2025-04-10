# 测试目录

本目录包含问卷星自动化系统的测试代码和数据。

## 目录结构

- `unit/`: 单元测试，测试独立的功能模块
- `integration/`: 集成测试，测试多个模块的协作
- `data/`: 测试数据，包含测试所需的样本数据

## 运行测试

### 运行所有测试

```bash
pytest backend/tests
```

### 运行特定测试文件

```bash
pytest backend/tests/unit/test_parser.py
```

### 运行特定测试方法

```bash
pytest backend/tests/unit/test_parser.py::test_parse_and_serialize
```

## 添加新测试

1. 在适当的目录下创建测试文件，命名为`test_模块名.py`
2. 导入需要测试的模块和pytest
3. 编写测试函数，函数名以`test_`开头
4. 运行pytest验证测试是否通过

## 测试数据

测试数据存放在`data/`目录下，包括：
- 序列化的问卷JSON数据
- 样例问卷HTML
- 其他测试所需的数据文件

保持测试数据与测试代码分离，有助于测试的组织和维护。 