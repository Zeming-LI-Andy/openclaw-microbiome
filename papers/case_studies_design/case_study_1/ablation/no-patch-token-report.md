# no-patch 的 token 为什么更高

口径：只计三次 dashboard 分析会话的最终窗口。同一 `responseId` 只保留一次。`total` = uncached input + cached input + cache write + output。reasoning 含在 output 里，不另加。0 token 的调用不计入次数。同名的 cron 会话 `check_metaphlan_done`（25 个独立窗口，约 748 万 token）是 MetaPhlAn 定时检查，不是这三次分析，不计入。

三次都是 `deepseek/deepseek-v4-pro`，reasoning = 0，cache write = 0。运行的是未打 exec-session-wake 补丁的 OpenClaw，工作区用的是 `ablation/no_patch/` 的提示词。

## 结论

no-patch 三次合计 105,242,592 token，均值 35,080,864。full 三次合计 43,576,653，均值 14,525,551。均值大约高出 2,056 万。三次分别是 23,766,127、49,321,971、32,154,494，都高于对应的 full（12,924,637、14,812,920、15,839,096）。`2-ablation-no-patch` 占 no-patch 全部 token 的 47%。

账单里 99.1% 是 cached input。no-patch 的系统提示比 full 更短，单次调用并没有因为固定前缀变长而变贵。贵在轮次变多，而且每一轮都把已经变长的历史重新读一遍。

轮次变多的直接原因：长命令还在跑时，模型用 `process poll` 反复查询。三次的 `sessions_yield` 都是 0。未打补丁的 `exec` 在命令仍在运行时写的是 `Use process (list/poll/…) for follow-up`，不再提示 `sessions_yield`。工作区的 `AGENTS.md`、`TOOLS.md`、`CODING.md` 也删掉了 `yieldMs` 和「不要 poll-loop」的规则。

## 三次和 full 的对比

| 会话 | 模型调用 | `process` | `sessions_yield` | `exec` | uncached | cached | output | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1-ablation-no-patch | 211 | 102 | 0 | 77 | 405,415 | 23,304,960 | 55,752 | 23,766,127 |
| 2-ablation-no-patch | 403 | 227 | 0 | 142 | 159,742 | 49,086,848 | 75,381 | 49,321,971 |
| 3-ablation-no-patch | 245 | 136 | 0 | 99 | 169,640 | 31,921,408 | 63,446 | 32,154,494 |
| 1-ablation-full | 150 | 1 | 17 | 91 | 505,931 | 12,370,176 | 48,530 | 12,924,637 |
| 2-ablation-full | 124 | 21 | 5 | 74 | 686,782 | 14,028,544 | 97,594 | 14,812,920 |
| 3-ablation-full | 126 | 0 | 13 | 82 | 458,430 | 15,273,216 | 107,450 | 15,839,096 |

`process`、`sessions_yield`、`exec` 是工具调用次数。模型调用是有 token 的助手回合。`1-ablation-no-patch` 另有 5 次 0 token 调用，`2-ablation-no-patch` 另有 1 次，都未计入上表。

## 原因 1：用 process poll 代替 yield

一次 poll 返回之后，模型再发起下一次，于是同一条后台命令对应一串模型调用。`process` 的 `timeout` 大多是 30000。只含 `process` 的那些模型调用，其提示词 token 为：

| 会话 | 只含 process 的调用 | 这些调用的提示词 token | 占该次 total |
|---|---:|---:|---:|
| 1-ablation-no-patch | 100 | 11,892,252 | 50% |
| 2-ablation-no-patch | 227 | 29,375,201 | 60% |
| 3-ablation-no-patch | 136 | 18,816,354 | 59% |

三次合计 60,083,807，占 no-patch 全部 token 的 57%。最长的连续 poll：会话 1 是 14 次，会话 2 是 52 次，会话 3 是 13 次。会话 2 有 105 次 poll 发生在上下文已经超过 15 万 token 之后，会话 3 有 49 次；会话 1 的单次上下文最高 155,987，没有超过这条线。后半段每次 poll 都更贵。

三次都没有调用 `sessions_yield`。会话 1 另外有 3 次 `automations`（提示词 token 434,382），用来盯 MetaPhlAn，并继续 poll。

## 原因 2：会话 2 的返工把轮次再拉高一截

`2-ablation-no-patch` 的 49,321,971 可以拆开：

| 调用内容 | 次数 | 提示词 token |
|---|---:|---:|
| process | 227 | 29,375,201 |
| exec | 137 | 15,719,179 |
| write / edit | 25 | 2,884,586 |
| 其余（计划、读文件、建 job、收尾） | 14 | 约 1,268,000 |

用户在 seq 451 发了一次 `Continue`。在此之前是 214 次调用，之后又是 189 次。停住的位置是 MetaPhlAn 批量脚本：配对 FASTQ 丢掉了 `--bowtie2out`，35 个样本都打印了 `DONE`，profile 却几乎是空的。`Continue` 之后模型改了 `run_sample.sh` 并重跑。接着用 `while true; do ls …/*_profile.txt` 盯进度，连续 poll 了 52 次；两个后台 `exec` 大约 30 分钟时失败，后面又重新查。

所以会话 2 的 `exec` 有 142 次，full 三次是 91、74、82。多出来的是改脚本和重跑，不是另一套生物学流程。单次上下文中位数是 130,359 token，末尾升到 176,097。调用数约为 `2-ablation-full` 的 3.3 倍（403 / 124），cached input 约为 3.5 倍（49,086,848 / 14,028,544）。

`3-ablation-no-patch` 没有这轮返工，也没有中途的 `Continue`。它一次做完，调用 245 次，仍是 `3-ablation-full`（126 次、15,839,096 token）的大约两倍。多出来的主要是 136 次 poll，不是少做了分析：收尾写明 7 个阶段都完成了。它只 `write` 了最后的 `SUMMARY.md`。

`1-ablation-no-patch` 在任务提示之后、第一次 `continue` 之前只有 25 次调用。后面有 6 次用户 `continue`，poll 累计 100 次。它的 total 是三次里最低的，仍比 `1-ablation-full` 高约 1,084 万。

## 缓存失效只解释 uncached

no-patch 的 uncached 合计 734,797，只占 total 的 0.7%。会话 2 和会话 3 没有整段历史被重计的调用；它们的未缓存输入大约是每轮新长出来的那一截。

会话 1 有两次接近整段重计：

| 位置 | uncached | cached |
|---|---:|---:|
| seq 358，成对的 `[OpenClaw heartbeat poll]` 之后，回复 `HEARTBEAT_OK` | 118,522 | 7,296 |
| seq 424，一次 0 token 回合之后用户发 `continue` | 130,883 | 7,424 |

这两次合计 249,405，占该次 uncached 的 62%，占该次 total 的 1.0%。下一次调用又命中大约 13.5 万 cached token。它们不是 2,377 万的来源。

## 对总量影响很小的部分

- **reasoning。** 三次都是 0。output 合计 194,579，不到 total 的 0.2%。
- **单次工具输出过大。** 只有 `3-ablation-no-patch` 的一条 `exec` 结果超过 2 万字符（63,997 字符）。没有把整份大文件读进上下文。
- **系统提示变长。** no-patch 删去了长任务 yield 与禁止轮询的规则段落，系统提示比 full 更短。多花的 token 在被重读的对话历史上。

## 和现有规则的对应关系

full 的 `papers/case_studies_design/case_study_1/ablation/full/CODING.md` 要求：`status: "running"` 且有 `sessionId` 时调用 `sessions_yield`；不要 poll-loop，也不要用 automation 看守一条还在跑的命令。`process` 只在用户要求查看或中止时使用。

no-patch 的 `AGENTS.md`、`TOOLS.md` 和 `CODING.md` 删去了 `yieldMs`、`sessions_yield` 和禁止 `process` 轮询的说明。未打补丁的 `exec` 结果本身把后续动作指到 `process`。转录与此相符：三次 `sessions_yield` 都是 0，`process` 为 102、227、136。
