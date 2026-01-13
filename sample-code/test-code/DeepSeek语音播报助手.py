import json
import tempfile

import dotenv
import keyboard
import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI

dotenv.load_dotenv()

base_url = "https://yunwu.ai/v1"
api_key = "sk-jw7lxHFNwj7OgDbyA1AZT2CxFSR2ejKRhmpvCzLU6SSF6bUW"


def calculator(expression: str) -> str:
    """一个简单的计算器，可以执行数学表达式"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"无效表达式, 错误信息: {str(e)}"})


class ReActAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [
            {
                "role": "system",
                "content": "你是一个强大的聊天机器人，请根据用户的提问进行答复，如果需要调用工具请直接调用，不知道请直接回复不清楚"
            }
        ]
        self.model = "deepseek-chat"
        self.available_tools = {"calculator": calculator}
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "一个可以计算数学表达式的计算器",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "需要计算的数学表达式，例如：'123+456+789'"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]

    def process_query(self, query: str) -> str:
        """使用deepseek处理用户输出"""
        self.messages.append({"role": "user", "content": query})

        # 调用deepseek发起请求
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
        )

        # 获取响应消息+工具响应
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 将模型第一次回复添加到历史消息中
        self.messages.append(response_message.model_dump())

        # 判断是否执行工具调用
        if tool_calls:

            # 循环执行工具调用
            for tool_call in tool_calls:
                print("Tool Call: ", tool_call.function.name)
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                function_to_call = self.available_tools[tool_name]

                # 调用工具
                result = function_to_call(**tool_args)
                print(f"Tool [{tool_name}] Result: {result}")

                # 将工具结果添加到历史消息中
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result,
                })

            # 再次调用模型，让它基于工具调用的结果生成最终回复内容
            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="none",
            )

            self.messages.append(second_response.choices[0].message.model_dump())
            return "Assistant: " + second_response.choices[0].message.content
        else:
            return "Assistant: " + response_message.content

    def chat_loop(self):
        """运行循环对话"""
        while True:
            try:
                # 获取用户的输入
                query = self.speech_to_text().strip()
                print(f"\nQuery: {query}")
                if query == "退出":
                    break

                # 获取Agent的输出并播放语音
                answer = self.process_query(query)
                print(answer)
                self.text_to_speech(answer)
            except Exception as e:
                print(f"\nError: {str(e)}")
 
    @classmethod
    def speech_to_text(cls) -> str:
        """根据语音信息获取文本的输入内容"""
        samplerate = 16000
        channels = 1
        recording = []
        is_recording = False

        print("按空格开始录音，再按一次空格停止录音...")

        def callback(indata, frames, time, status):
            if is_recording:
                recording.append(indata.copy())

        # 尝试自动选择合适的输入设备
        device_index = None
        try:
            # 优先查找带有 "麦克风" 或 "Microphone" 的设备
            devices = sd.query_devices()
            hostapis = sd.query_hostapis()
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    # 获取该设备所属 Host API 的名称
                    hostapi_name = hostapis[device['hostapi']]['name']
                    
                    # 优先选择 MME 驱动的麦克风，兼容性更好
                    if 'MME' in hostapi_name:
                         if '麦克风' in device['name'] or 'Microphone' in device['name']:
                            device_index = i
                            # 确保通道数匹配
                            if device['max_input_channels'] < channels:
                                channels = device['max_input_channels']
                            break
            
            # 如果没找到特定设备，让 sounddevice 使用默认输入设备
            if device_index is None:
                device_index = sd.default.device[0]
                
            print(f"使用音频输入设备: {devices[device_index]['name']} (ID: {device_index})")
            
        except Exception as e:
            print(f"选择音频设备出错，将尝试使用默认设备: {e}")
            # 如果出错，确保 device_index 至少有个值（虽然可能还是默认值）
            if device_index is None:
                 device_index = sd.default.device[0]

        stream = sd.InputStream(
            samplerate=samplerate, 
            channels=channels, 
            callback=callback,
            device=device_index  # 显式指定设备 ID
        )
        stream.start()

        # 等待第一次空格：开始录音
        keyboard.wait("space")
        is_recording = True
        print("录音中... 再按一次空格停止")

        # 等待第二次空格：停止录音
        keyboard.wait("space")
        is_recording = False
        stream.stop()
        stream.close()
        print("录音结束")

        # 把片段拼接成一个 numpy 数组
        if not recording:
            print("没有录到声音")
            return ""

        audio_data = np.concatenate(recording, axis=0)

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio_data, samplerate)
            audio_path = tmpfile.name

        # 调用 OpenAI API 语音转文本
        with open(audio_path, "rb") as audio_file:
            client = OpenAI(base_url=base_url, api_key=api_key)
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        return transcript.text

    @classmethod
    def text_to_speech(cls, text: str) -> None:
        # 调用 OpenAI TTS 生成语音
        client = OpenAI(base_url=base_url, api_key=api_key)
        response = client.audio.speech.create(
            model="tts-1",  # 文本转语音模型
            voice="alloy",  # 可选：alloy, verse, etc.
            input=text
        )

        # 保存临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            tmpfile.write(response.read())
            audio_path = tmpfile.name

        # 播放语音
        data, samplerate = sf.read(audio_path)
        sd.play(data, samplerate)
        sd.wait()  # 等待播放完成


if __name__ == "__main__":
    ReActAgent().chat_loop()
