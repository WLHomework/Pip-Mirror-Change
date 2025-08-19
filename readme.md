# Pip 镜像切换器

一个简单易用的 GUI 工具，帮助快速切换 Python pip 镜像源，特别优化了国内常用镜像，支持多作用域设置。

## 功能特点

- 一键切换至国内主流 pip 镜像（清华、阿里云、华为云等）
- 支持三种作用域切换：用户级（推荐）、当前环境 / 虚拟环境、系统级（可能需要管理员权限）
- 镜像测速功能，自动推荐最快镜像
- 一键还原官方默认源
- 查看当前 pip 配置信息
- 支持中英文界面切换
- 现代深色主题，美观易用

## 支持的镜像源

| 镜像名称    | 地址                                                   |
| ----------- | ------------------------------------------------------ |
| 清华 TUNA   | https://pypi.tuna.tsinghua.edu.cn/simple               |
| 阿里云      | https://mirrors.aliyun.com/pypi/simple                 |
| 华为云      | https://mirrors.huaweicloud.com/repository/pypi/simple |
| 腾讯云      | https://mirrors.cloud.tencent.com/pypi/simple          |
| 中科大 USTC | https://pypi.mirrors.ustc.edu.cn/simple                |
| 豆瓣        | https://pypi.doubanio.com/simple                       |

## 使用方法

1. 选择需要使用的镜像源
2. 选择作用域（用户级推荐，无需管理员权限）
3. 点击 "切换为所选镜像" 按钮
4. 操作结果会显示在下方日志区域

其他功能：

- 点击 "还原默认官方源" 恢复至 pip 官方源
- 点击 "查看当前配置" 显示当前 pip 镜像设置
- 点击 "测速并推荐" 测试各镜像速度并推荐最快选项