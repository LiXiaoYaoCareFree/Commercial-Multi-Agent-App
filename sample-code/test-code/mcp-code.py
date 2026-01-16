import os
import subprocess
import uuid

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="代码解释器", port=9888)
BASE_DIR = "E:\\agent code\\Commercial-Multi-Agent-App\\sample-code\\test-code"
UV_CMD = "uv"


@mcp.tool()
async def run_code(language: str, code: str, timeout: int = 30) -> str:
    """根据语言运行代码并返回执行结果，Python代码会使用E:\agent code\Commercial-Multi-Agent-App\sample-code\test-code中uv创建的Python 3.12版本运行。

    Args:
        language: 'python' 或者 'node'
        code: 要执行的代码文本
        timeout: 最长运行描述（默认为30s）

    Returns:
        执行输出(stdout)或错误信息(stderr/异常)
    """
    # 1.检查传递的编程语言是否符合规则
    language = (language or "").strip().lower()
    if language not in ("python", "node"):
        return f"不支持的语言: {language}"

    # 2.计算获取临时代码文件名
    suffix = ".py" if language == "python" else ".js"
    name = f"temp_{uuid.uuid4().hex}{suffix}"
    tmp_path = os.path.join(BASE_DIR, name)

    # 3.确保目录存在
    os.makedirs(BASE_DIR, exist_ok=True)

    try:
        # 4.写入临时文件
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(code)

        # 5.判断不同的语言类型执行不同的操作
        cwd = BASE_DIR
        if language == "python":
            # 6.使用uv来运行对应的文件
            cmd = [UV_CMD, "--directory", BASE_DIR, "run", name]
        else:
            # 7.使用node命令运行脚本
            cmd = ["node", tmp_path]

        # 8.调用子线程运行对应命令
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=False,  # 以字节形式获取输出，避免使用系统默认编码解码
            timeout=timeout,
            cwd=cwd,
        )

        # 9.获取输出与错误结果
        stdout = (proc.stdout or b"").decode("utf-8", errors="ignore").strip()
        stderr = (proc.stderr or b"").decode("utf-8", errors="ignore").strip()

        # 10.判断状态码
        if proc.returncode == 0:
            return stdout
        else:
            return f"命令返回非零状态 {proc.returncode}, stderr: \n{stderr or stdout}"
    except subprocess.TimeoutExpired:
        return f"执行超时(>{timeout}s)"
    except FileNotFoundError as e:
        return f"命令未找到活路径错误: {str(e)}"
    except Exception as e:
        return f"执行异常: {str(e)}"
    finally:
        # 尝试删除临时文件（并且忽略错误）
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
