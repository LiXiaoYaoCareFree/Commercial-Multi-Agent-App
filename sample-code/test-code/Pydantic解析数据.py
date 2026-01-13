from pydantic import BaseModel, Field, EmailStr

class UserInfo(BaseModel):
    """传递用户的信息进行数据提取&处理，涵盖name、age、email等"""
    name: str = Field(..., description="用户名字")
    age: int = Field(..., description="用户年龄，必须是正整数")
    email: EmailStr = Field(..., description="用户的电子邮件")

# 假设这是从Tool Calls的arguments中获取的字符串
json_string = '{"name": "张三", "age": 25, "email": "zhangsan@example.com"}'

try:
    user = UserInfo.model_validate_json(json_string)  # Pydantic V2的推荐方法

    # 得到的是一个真正的Python对象，而不是字典！
    print(f"解析成功！用户名: {user.name}")
    print(f"用户年龄: {user.age}")
    print(f"用户邮箱: {user.email}")
    print(user)  # 打印出的对象清晰明了

except Exception as e:
    print(f"数据校验失败: {e}")

# --- 让我们试试错误数据 ---
invalid_json_string = '{"name": "李四", "age": -5, "email": "not-an-email"}'
try:
    UserInfo.model_validate_json(invalid_json_string)
except Exception as e:
    print("\n--- 错误数据测试 ---")
    print(f"数据校验失败:\n{e}")