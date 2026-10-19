
# no-patch 的 token 为什么更高

统计口径与 `token_usage.csv` 相同：只计最终会话窗口里的模型调用，续写窗口不重复加总。三次 no-patch 的调用数与该表一致（155、268、145）。`total` = uncached input + cached input + cache write + output。reasoning 含在 output 里，不另加。

## 结论

no-patch 三次合计 67,974,764 token，均值 22,658,255。full 三次合计 43,576,653，均值 14,525,551。多出来的约 810 万均值，主要来自 **`2-ablation-no-patch` 这一次**（35,353,340，占 no-patch 全部 token 的 52%）。另外两次是 16,628,863 和 15,992,561，只比 full 略高。

账单里 95.8% 是 cached input。系统提示在 no-patch 里更短，单次调用并没有因为提示词变长而变贵。贵在 **轮次变多，而且每一轮都把已经变长的历史重新读一遍**。

轮次变多的直接原因：长命令还在跑时，模型用 `process poll` 反复查询，而不是 `sessions_yield` 一次、等命令结束后再被唤醒。full 的 `CODING.md` 禁止这种轮询；no-patch 的 `AGENTS.md` / `TOOLS.md` 没有这组规则。

## 三次和 full 的对比

| 会话                | 模型调用 | `process` | `sessions_yield` | `exec` |  uncached |     cached |  output |      total |
| ------------------- | -------: | ----------: | -----------------: | -------: | --------: | ---------: | ------: | ---------: |
| 1-ablation-no-patch |      155 |          66 |                  0 |       80 |   505,808 | 16,077,696 |  45,359 | 16,628,863 |
| 2-ablation-no-patch |      268 |          86 |                  0 |      140 | 1,332,507 | 33,867,264 | 153,569 | 35,353,340 |
| 3-ablation-no-patch |      145 |          20 |                  0 |       84 |   695,597 | 15,208,704 |  88,260 | 15,992,561 |
| 1-ablation-full     |      150 |           1 |                 17 |       91 |   505,931 | 12,370,176 |  48,530 | 12,924,637 |
| 2-ablation-full     |      124 |          21 |                  5 |       74 |   686,782 | 14,028,544 |  97,594 | 14,812,920 |
| 3-ablation-full     |      126 |           0 |                 13 |       82 |   458,430 | 15,273,216 | 107,450 | 15,839,096 |

模型：`1-ablation-no-patch` 是 `deepseek/deepseek-v4-pro`（reasoning = 0）。另外两次 no-patch 是 `huoshan/deepseek-v4-pro-ga-260813`（reasoning 分别 96,706 和 46,823，已含在 output 中）。full 的第一次是 huoshan 与 deepseek 混用，后两次是 huoshan。

作为参照，三次 no-skills 的 `process` 次数是 13、0、0，`sessions_yield` 是 25、19、22。它们的 total 是 16,975,649、10,922,275、11,840,182。

## 原因 1：用 process poll 代替 yield

`exec` 返回 `status: "running"` 时，工具结果里写着要调用 `sessions_yield`。full 的长任务规则是：确认仍在运行后 yield 一次；`process poll` 只在用户要求查看状态时使用，不用来循环等到结束。no-patch 删掉了这组规则。

三次 no-patch 实际做成了轮询。`process` 的 `timeout` 大多是 30000。一次 poll 返回之后，模型再发起下一次，于是同一条后台命令对应一串模型调用。只含 `process` 的那些调用，其提示词 token 为：

| 会话                | 只含 process 的调用 | 这些调用的提示词 token | 占该次 total |
| ------------------- | ------------------: | ---------------------: | -----------: |
| 1-ablation-no-patch |                  64 |              7,398,519 |          44% |
| 2-ablation-no-patch |                  86 |             11,280,679 |          32% |
| 3-ablation-no-patch |                  20 |              2,378,553 |          15% |

三次合计 21,057,751，占 no-patch 全部 token 的 31%。`1-ablation-no-patch` 里最长的一段连续 poll 是 15 次。`2-ablation-no-patch` 有 44 段 poll，其中 26 次发生在上下文已经超过 15 万 token 之后，所以后半段每次 poll 都更贵。

`2-ablation-no-patch` 全程没有调用 `sessions_yield`，在 MetaPhlAn 后半段还注册了 automation 来盯进度，并继续 poll。这和「yield 一次然后停下」是两条路径。

## 原因 2：会话 2 的轮次和上下文一起变长

`2-ablation-no-patch` 的 35,353,340 可以拆开：

| 调用内容                      | 次数 | 提示词 token |
| ----------------------------- | ---: | -----------: |
| exec                          |  133 |   16,278,733 |
| process                       |   86 |   11,280,679 |
| write / edit                  |   32 |    4,682,984 |
| 其余（计划、automation、收尾） |   17 | 约 2,700,000 |

同一次 full（`2-ablation-full`）是 124 次调用、1,481 万 token。no-patch 这一次是 268 次。调用数约为 2.1 倍，cached input 约为 2.4 倍（33,867,264 / 14,028,544）。单次上下文的中位数是 139,302 token，末尾升到 233,259。调用数和单次长度是同一件事的两面：poll、改脚本、重跑命令都写进历史，后面每轮都重读。

任务提示词出现之前还有 33 次调用、1,599,743 token。这条会话先有两个被杀掉的窗口，转录里留下四次 “Please set up a job”。这 160 万是实打的消耗，只占这一次的 4.5%。

后半段的额外 exec 主要是脚本失败后的修改和 MetaPhlAn 重跑，不是另一套生物学流程。可见的失败包括 `phase0_shotgun_depth.py`、`phase2_alpha.py`、`phase4_visualize.py` 的 Traceback，一次 SIGTERM，以及 MetaPhlAn 因旧的 bowtie2out 状态被关掉后重新启动。`exec` 次数是 140，full 三次是 91、74、82。

`3-ablation-no-patch` 的 poll 只有 20 次，total 与 `3-ablation-full` 几乎相同（15,992,561 对 15,839,096）。它多出来的是 27 次 write/edit（提示词 token 3,328,102），不是轮询。

## 原因 3：heartbeat 把缓存打掉

这解释 uncached 列，不解释 total。no-patch 的 uncached 合计 2,533,912，只占 total 的 3.7%。

模型刚结束一轮后，下一条用户消息常常是成对出现的 `[OpenClaw heartbeat poll]`。紧接着的那一次模型调用只命中约 8192 个 cached token，其余整段历史按未缓存重计；再下一次又命中刚写上的缓存。

| 会话                | 位置                            |                   uncached |   cached |
| ------------------- | ------------------------------- | -------------------------: | -------: |
| 1-ablation-no-patch | seq 68，heartbeat 之后          |                     84,948 |        0 |
| 1-ablation-no-patch | seq 253，heartbeat 之后         |                    126,924 |      256 |
| 2-ablation-no-patch | seq 473                         |                    179,093 |    8,192 |
| 2-ablation-no-patch | seq 486，heartbeat 之后         |                    185,906 |    8,192 |
| 2-ablation-no-patch | seq 519，heartbeat 之后         |                    207,494 |    8,192 |
| 2-ablation-no-patch | seq 562，结束语之后的 heartbeat |                    225,067 |    8,192 |
| 3-ablation-no-patch | seq 51、196、258                | 64,844 + 123,729 + 136,686 | 各 6,144 |

`2-ablation-no-patch` 这四次合计 797,560 uncached，占该次 uncached 的 60%，占该次 total 的 2.3%。同一机制在 no-skills 里也出现过。它放大的是「已经很长的历史被整段重计一次」，前提仍是历史已经被 poll 和重试撑长。

## 对总量影响很小的部分

- **reasoning。** 会话 2 的 96,706 和会话 3 的 46,823 都在 output 里。会话 2 的 output 一共 153,569，不到 total 的 0.5%。会话 1 没有 reasoning，total 仍然有 1,663 万，因为 poll 本身就占了 44%。
- **单次工具输出过大。** 三次 no-patch 里，单条工具结果超过 2 万字符的只有两条（约 2.8 万和 2.1 万字符）。没有把整份大文件读进上下文。
- **系统提示变长。** no-patch 少了 `CODING.md`。多花的 token 不在这段固定前缀上，而在被重读的对话历史上。

## 和现有规则的对应关系

full 的 `papers/case_studies_design/case_study_1/ablation/full/CODING.md` 要求：`status: "running"` 且有 `sessionId` 时调用 `sessions_yield`；不要 poll-loop，也不要用 automation 看守一条还在跑的命令。`process` 只在用户要求查看或中止时使用。

no-patch 的 `AGENTS.md` 在硬规则处停在「用 exec、不要编造结果」，没有 yield、`yieldMs` 或 poll 的说明。转录里的行为与此相符：三次 `process` 为 66、86、20，`sessions_yield` 均为 0；会话 2 还另外建了 automation 来等 MetaPhlAn。
