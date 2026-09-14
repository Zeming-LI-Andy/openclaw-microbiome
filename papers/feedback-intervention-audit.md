# 长周期任务中的用户反馈能力核查（2026-09-14）

结论：**本项目设计了“长步骤后台运行—智能体让出回合—用户可在同一会话中途介入—命令结束后自动续接”的交互循环。** 这不只是命令结束通知：OpenClaw 补丁同时改变了模型可见的 `exec`/`sessions_yield` 提示及回合续接行为，`workspace/` 则把它落实为微生物组学的逐步骤分析规则。源码支持这一设计，但“反馈实际驱动流程重规划”的成功率与时序仍待运行记录验证；不能据此声称 HITL 或运行中消息接收是首创。

## 将主张拆成四层

1. **消息接收**：运行中用户能发来新指令。
2. **模型采纳**：新指令在何时进入同一会话的模型上下文。
3. **流程调整**：模型在下一个步骤前修改计划/参数/工具选择。
4. **运行中命令处理**：对已启动的 CLI 是继续、停止、还是重跑；已有工具一般不能在不中断情况下更换参数。

若只有 1–2，不足以写“动态调整分析流程”。若能证明 1–4，仍需报告干预延迟和哪些步骤在干预时已不可逆。

## 本项目源码表明什么

1. **让出回合，保留进程。** `workspace/AGENTS.md` 与 `workspace/CODING.md` 规定长步骤调用 `exec(yieldMs: 30000, timeout: 0)`；仅当返回 `status: "running"` 和有效 `sessionId` 时调用 `sessions_yield`。命令继续运行，模型当前回合结束，而会话和 `job_id` 保留。`0004-tool-guidance-yield-before-poll.patch` 同时修改 `exec` 工具说明、运行中返回文案、系统提示词与 `sessions_yield` 工具说明，明确引导模型让出回合等异步完成事件，避免持续轮询。`0005` 将运行中的 `exec` 结果识别为有效的异步续接依据。
2. **用户消息路径。** 在让出的等待窗口里，用户仍可向同一会话发送消息；该消息可触发新的模型回合，使智能体根据反馈检查运行中步骤、更新计划和调整未启动的步骤。`workspace/AGENTS.md` 要求保持计划状态更新，`workspace/CODING.md` 允许用户要求时用 `process` 查看日志/状态或控制进程。这一入站消息路径使用 OpenClaw 原有会话能力；补丁没有单独新增用户消息接口。是否在特定部署/队列设置下及时触发、与完成事件如何排序，须用真实会话日志确认。
3. **命令完成路径。** `0003-exec-notify-immediate-and-steer-wake.patch` 在 `exec` 退出后向空闲会话发即时 heartbeat，或把退出事件 steer 进可接收的活动回合；`0005` 避免在模型仍流式生成时丢失完成事件；`0002` 清理阻碍后续回合写入的上下文；`0001` 修改完成事件提示词，要求在同一会话检查结果并继续，而不是只给静默 heartbeat。这些是**命令完成事件**的投递与续接，不是用户消息本身。
4. **交汇处的动态调整。** 两条路径会在同一 `job_id` 的逐步骤计划中交汇：用户可以在 A 执行时修改 B；A 完成后，智能体应按更新后的计划决定是否运行 B。若用户修改 A 的关键参数，已启动的 CLI 不会自动变更；智能体须选择让它完成并判定旧结果是否仍可用，或显式停止/重跑。源码未提供事务化的重规划保证，尤其要验证用户消息与完成事件接近同时到达时不会丢反馈或重复执行。

这里的“中途介入”是**分析任务尚未结束、后台 CLI 仍在执行时，用户可以发消息并开启同一会话的新回合**；不是抢占正在运行的 CLI 指令或把 `sessions_yield` 变成持续运行的对话回合。

## 相邻工作的准确比较

| 系统 | 已有证据 | 尚不能断言 |
|---|---|---|
| [OpenClaw 当前官方文档：queue](https://docs.openclaw.ai/concepts/queue-steering)、[steer](https://docs.openclaw.ai/tools/steer) | 默认 `steer` 可在模型/工具边界注入运行中的用户消息；空闲会话可接收新消息开启回合。文档明确说不会抢占已开始的工具调用。 | 不能说 OpenClaw 没有运行中用户反馈能力。当前文档可能与本项目固定的 `2026.7.2` 版本细节不同。可比较的是本项目专门为**长时后台 `exec` + `sessions_yield` + 完成事件续接**构造的闭环及微生物组分析中的实际表现。 |
| [MetaClaw 公开仓库](https://github.com/BGI-AI-models/MetaClaw) | 同样基于 OpenClaw；明确 `plan → confirm → submit → poll → finalize`，上游是 FlowHub 的固定作业；计划与参数由用户确认。 | 不能说其根本无法接收中途消息；可说公开论文/仓库尚未展示**已提交上游作业期间用户反馈驱动的重规划实验**。固定上游流与本项目逐步骤本地执行在调整粒度上可能不同，需对照实测。 |
| [Biomni 原始论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC12157518/) | 会先规划、执行代码、观察后调整；提供交互界面。 | 查到的论文没有明确评估“长 CLI 运行中用户插话并重排后续步骤”，但不能由论文未报告推出软件绝无此功能。 |
| [M3A 生物智能体预印本](https://www.biorxiv.org/content/10.64898/2026.06.04.729919v1.full) | 明确比较 human-in-the-loop、human-on-the-loop 和自主模式。 | HITL 本身不是本文首创；这里的工作负载与本文微生物组长任务不同。 |

## 适合论文的暂定措辞

> MicroBioAgent couples asynchronous execution of long-running microbiome analyses with an interruptible agent workflow. While a local analysis step continues in the background, the agent yields its turn and the user may provide new instructions in the same session. The agent can revise pending steps or inspect and control the active process in response; a patched completion-event path then resumes the analysis and verifies its outputs before proceeding.

这段的设计部分可以在 Introduction/Methods 说明；其中的实际动态调整效果要由 Results 的**真实会话轨迹**支持。建议用 “mid-analysis feedback”、“asynchronous human intervention” 或 “feedback-guided replanning during long-running analyses”。不要用 `real-time`、`at any moment` 或 `first` 来暗示对正在运行的 CLI 做抢占式修改。

## 最小验证实验

在固定模型、固定输入与版本下，用可控的长运行模拟步骤（另用至少一项真实微生物组 CLI 复核），测试：

1. **改后续任务**：A 运行时用户改变 B 的参数；记录消息到达、agent 读取、计划更新、A 结束、B 启动时间，核对 B 使用新参数且 A 未重复。
2. **改当前任务**：A 运行时用户改变 A 的关键参数；记录 agent 选择继续/停止/重跑的理由、原进程退出与中间产物状态，确认无孤儿进程和混用旧结果。
3. **竞态**：用户消息恰在 A 退出通知前后到达；确认反馈与退出事件均进入同一 job，不丢消息、不重复启动 B。
4. **基线**：比较未打补丁的相同 OpenClaw 固定版本、打补丁版本、`steer`/`followup` 配置；这样才能把**原有消息接收**、**补丁引导的让出回合**与**补丁改善的退出续接**分别归因。

主要指标：反馈采纳延迟、正确修改的后续步骤比例、错误/重复运行比例、进程清理、产物有效性、人工干预次数。预先写下通过标准；只检查聊天回复“收到”不足以证明能力。
