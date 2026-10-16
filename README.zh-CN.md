# AI Factory Engineering

面向 AI 基础设施的跨层调试与验收：证明 **计算 -> 网络 -> 运行时 (Compute -> Fabric -> Runtime)** 能持续满足声明的工作负载 SLO，并将结果封存为可重播的证据。

本项目聚焦“硬件已安装”与“AI 工厂实际交付可用、可衡量输出”之间的工程差距。

## 中文文档

本项目的英文原始文档见仓库根目录与 `docs/`。中文版文档包括：

- [贡献指南](CONTRIBUTING.zh-CN.md)
- [开发者工作流](DEVELOPMENT.zh-CN.md)
- [安全说明](SECURITY.zh-CN.md)
- [知识库索引](docs/zh-CN/README.md)

## 为什么存在这个项目

现代 GPU 集群在单层看可能看起来健康，但作为系统仍可能失败：

- GPU 通过基础健康检查，但 NVLink/NVSwitch 性能不足。
- RDMA 链路已连通，但重试/符号错误破坏集体通信性能。
- NCCL 带宽达标，但推理 TTFT/TPOT 未达到工作负载 SLO。
- 各项检查均通过，但缺少将证据与决策绑定的签名跨层验收制品。

本仓库将这些检查串成一条验收链路。

## 黄金路径

```text
Native collector commands
  -> raw stdout/stderr artifacts
  -> EvidenceBundle
  -> schema validation
  -> TestOutcome
  -> Compute Gate
  -> Fabric Gate
  -> Runtime Gate
  -> AcceptanceDecision
  -> AcceptanceArtifact
  -> attestation
  -> verification / replay
```

Reference evidence adapters currently cover:

当前参考证据适配器涵盖：

- DCGM GPU health
- NVLink health/bandwidth
- RDMA port/error health
- NCCL collective bandwidth/correctness
- Inference SLO: TTFT P99, TPOT P99, success ratio

Thresholds are declared inputs. The framework does not hard-code a universal "good" NCCL bandwidth or latency target.

阈值为声明输入。框架不硬编码通用的“良好”NCCL 带宽或延迟目标。

## 五分钟演示

Requirements: Python 3.11+.

```bash
make setup
make test
make demo
```

确定性演示无需 GPU 硬件，输出写入：

```text
.artifacts/demo/acceptance.json
```

它使用仓库固件 (fixtures) 演示完整的验收契约。

## 真实命令烟雾测试路径

拷贝委托模板并替换每个站点占位符：

```bash
cp acceptance/examples/real-command-commissioning.template.json \
   acceptance/examples/my-site-commissioning.json
```

然后运行：

```bash
make smoke MANIFEST=acceptance/examples/my-site-commissioning.json
```

该清单可调用批准的站点命令，如 `dcgmi`、`nvidia-smi nvlink`、RDMA 工具和 `nccl-tests`。原始命令输出会被保留为证据。

## 架构

```text
                    AI Factory Acceptance Plane

  Compute                    Fabric                     Runtime
┌────────────┐            ┌────────────┐            ┌──────────────┐
│ DCGM       │            │ RDMA       │            │ Inference SLO│
│ NVLink     │            │ NCCL       │            │ TTFT / TPOT  │
└─────┬──────┘            └─────┬──────┘            └──────┬───────┘
      │                         │                          │
      └──────────────┬──────────┴──────────────┬──────────┘
                     ▼                         ▼
                EvidenceBundle            Gate DAG
                      │                         │
                      └──────────────┬──────────┘
                                     ▼
                            AcceptanceDecision
                                     ▼
                            AcceptanceArtifact
                                     ▼
                                Attestation
                                     ▼
                          Verification / Replay
```

## 设计原则

- **先失败，后通过 (Fail closed).** 证据缺失或不完整时不得静默变为 PASS。
- **证据优先 (Evidence first).** 在推导验收前先保留原始工件与来源。
- **跨层，而非仅设备 (Cross-layer, not device-only).** 验收单元是交付的系统/工作负载路径。
- **阈值显式 (Thresholds are explicit).** 站点拓扑和合同 SLO 定义验收底线。
- **可移植运行器边界 (Portable runner boundary).** 原生命令保持在域逻辑之外。
- **可重播决策 (Replayable decision).** 验收制品内容寻址且可验证。

## 仓库地图

```text
src/ai_factory_engineering/   acceptance, collectors, runner, reports, replay
acceptance/tests/             AcceptanceTest specs
acceptance/examples/          plans, templates and reference manifests
examples/                     runnable demos
tests/                        unit, contract and integration tests
casebook/                     reference engineering cases
docs/                         architecture and AI Factory engineering notes
```

## 外部验收契约

`AcceptanceArtifact` 是面向仓库外消费者的可移植输出边界。其 JSON 契约发布于 `schemas/acceptance-artifact.schema.json`。

外部控制平面应消费封存的制品，而非重新运行 AI Factory 阈值逻辑：

```text
raw evidence
  -> AI Factory Gate DAG
  -> AcceptanceArtifact
       + caseId
       + disposition / accepted
       + per-gate status
       + evidenceRefs
       + content digest
  -> external evidence binding
```

Schema 验证确立制品形状；制品摘要确立内容完整性。生产信任/真实性是单独的证明关注点，不由摘要验证单独隐含。

## 验收证明信任边界

`AcceptanceArtifact.digest` 证明内容完整性，不证明生产者身份。单独的 `AcceptanceAttestation` 将制品摘要绑定到密钥身份。

参考实现目前对受控集成/实验室证明使用 HMAC-SHA256。签名消息包括：

```text
apiVersion
kind
artifactDigest
keyId
algorithm
```

因此重写 `keyId` 或 `algorithm` 会使签名失效。

外部契约发布于 `schemas/acceptance-attestation.schema.json`。

HMAC 为参考机制。生产部署应将签名者/验证者替换为非对称 KMS/Sigstore/Cosign 后端实现，且不改变 AcceptanceArtifact 边界。

## 封存受控实验室验收结果

在真实委托运行产生 `AcceptanceArtifact` 后，可不在命令行上暴露共享密钥的前提下创建参考证明：

```bash
export AI_FACTORY_ATTESTATION_SECRET='...'

ai-factory attest acceptance.json \
  --key-id commissioning-lab \
  --output acceptance.attestation.json

ai-factory verify-attestation \
  acceptance.json \
  acceptance.attestation.json \
  --expected-key-id commissioning-lab
```

CLI 仅从指定环境变量读取密钥，且永不将其写入制品或证明。输出的证明仅包含制品摘要、密钥身份、算法和签名。

这仍是受控集成的 HMAC 参考路径。生产签名应使用非对称 KMS/Sigstore/Cosign 验证器。

## 受控实验室交接

最小真实硬件路径已有意收窄：

```text
GPU telemetry -> Compute Gate
Inference JSON summary -> Runtime Gate
              -> AcceptanceArtifact
              -> AcceptanceAttestation
```

使用：

```bash
ai-factory validate-lab-manifest /path/to/lab.json

export AI_FACTORY_ATTESTATION_SECRET='...'
make lab-smoke \
  MANIFEST=/path/to/lab.json \
  ATTESTATION_KEY_ID=commissioning-lab
```

模板 `acceptance/examples/controlled-lab-minimum.template.json` 在站点身份、版本、资产、命令和 SLO 基线被明确填写前为 fail-closed。最小路径中 Fabric 报告为 Not Evaluated，而非静默通过。

`commission` 现在会发出内容寻址的 `acceptance-artifact.json`，其证据引用绑定标准 EvidenceBundle 加上原始采集器 stdout/stderr 的 SHA-256 校验和。

## 当前状态

v0.1 发布候选版。

已实现：

- 原生采集器执行边界
- EvidenceBundle 架构/验证
- DCGM/NVLink/RDMA/NCCL/推理适配器
- fail-closed 跨层 Gate DAG
- 确定性 576-GPU 参考验收演示
- AcceptanceArtifact 摘要 + 参考证明
- 真实命令委托清单模板
- `make demo` / `make smoke` 开发者工作流

尚未声明：

- 真实 576-GPU 生产委托运行
- 通用性能阈值
- 生产 KMS/Sigstore/Cosign 签名
- 覆盖每个供应商/版本的硬件特定解析器
- 替代供应商诊断或站点委托流程

参见 [DEVELOPMENT.zh-CN.md](DEVELOPMENT.zh-CN.md) 和 [RELEASE_READINESS.md](RELEASE_READINESS.md)。

## 范围

更广泛的工程模型保持：

```text
MW -> Facility -> Rack/Pod -> GPU -> Fabric -> Cluster
   -> Runtime -> Model -> Token / Model Progress -> SLO / Economics
```

本仓库当前将可执行代码集中在跨层委托和验收部分。
