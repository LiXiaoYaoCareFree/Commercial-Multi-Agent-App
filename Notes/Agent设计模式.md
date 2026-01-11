## 控制循环： Agent核心设计模式

### 控制循环也是Agent中最核心的部分，也是开发者编写的Agent设计模式，这个设计模式就是Agent的生命力Agent的生命力所在

### 五种设计模式：反思模式、工具使用模式、ReAct模式、规划模式、多智能体协作模式

<img height="500" src="https://cdniy.com/xiaoyao/i/2026/01/11/xiyx.png" width="700" alt=""/>  

### 反思模式(Reflection Pattern)
#### 解决问题：
LLM生成的答案“一遍过”，质量可能不高
#### 循环控制做什么：
让LLM生成初稿后，再启动新一轮调用，让它自我批判和修正，最后整合输出

<img height="500" src="https://cdniy.com/xiaoyao/i/2026/01/11/6jf4v.png" width="700" alt=""/>  

### 工具使用模式(Tool Use)
#### 解决问题：
LLM是“书呆子”，无法与现实世界交互，信息滞后

#### 控制循环做什么：
解析LLM“调用工具”的决策，真正地用代码执行函数或API，再将结果返回给LLM

<img height="500" src="https://cdniy.com/xiaoyao/i/2026/01/11/xmnr.png" width="700" alt=""/>  

### ReAct模式(Reason+Act)
#### 解决问题：
面对复杂问题，如何有条不紊地思考和行动

#### 循环控制做什么：
严格执行“思考->行动->观察”的循环，直到LLM认为任务完成

<img height="500" src="https://cdniy.com/xiaoyao/i/2026/01/11/4syl.png" width="700" alt=""/>  

### 规划模式(Planning)
#### 解决问题：
再执行超大型任务时，避免“走一步看一步”导致的迷路。

#### 循环控制做什么：
先让LLM生成一个详细的步骤清单(Plan), 然后控制循环严格按照计划执行

<img height="500" src="https://cdniy.com/xiaoyao/i/2026/01/11/xmsl.png" width="700" alt=""/>  

### 多智能体协作(Multi-Agent)
#### 解决问题：
单个Agent能力有限，无法完成“跨界”的复杂系统工程

#### 循环控制做什么：
升级为“通信和调度总线”，将任务分配给多个专家Agent，并协调它们之间的沟通
