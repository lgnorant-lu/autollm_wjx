"""
---------------------------------------------------------------
File name:                  conftest.py
Author:                     Ignorant-lu
Date created:               2025/03/05
Description:                Pytest配置文件
----------------------------------------------------------------

Changed history:            
                            2025/03/05: 初始创建;
                            2025/03/28: 添加样例问卷URL fixture;
----
"""

import os
import sys
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 这里可以添加共享的pytest fixtures
@pytest.fixture
def sample_survey_url():
    """返回用于测试的样例问卷URL"""
    return 'https://www.wjx.cn/vm/wWwct2F.aspx' 