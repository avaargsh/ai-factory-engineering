# AI Factory Engineering — 关于本项目

## 一句话概述

面向 AI 基础设施的跨层调试与验收工具包：证明 **计算 -> 网络 -> 运行时 (Compute -> Fabric -> Runtime)** 能持续满足声明的工作负载 SLO，并将结果封存为可重播、可验证的证据。

## 项目使命

现代 GPU 集群在单层看可能看起来健康，但作为系统仍可能失败：

- GPU 通过基础健康检查，但 NVLink/NVSwitch 性能不足。
- RDMA 链路已连通，但重试/符号错误破坏集体通信性能。
- NCCL 带宽达标，但推理 TTFT/TPOT 未达到工作负载 SLO。
- 各项检查均通过，但缺少将证据与决策绑定的签名跨层验收制品。

本项目把这些分散的层面检查串成一条可审计、可重播的跨层验收链路，缩小“硬件已安装”与“AI 工厂实际交付可用、可衡量输出”之间的工程差距。

## 核心原则

| 原则 | 说明 |
|------|------|
| 先失败，后通过 (Fail closed) | 证据缺失或不完整时不得静默变为 PASS。 |
| 证据优先 (Evidence first) | 在推导验收前，先保留原始采集工件与来源。 |
| 跨层，而非仅设备 | 验收单元是交付的系统/工作负载路径，而非单台设备。 |
| 阈值显式 | 站点拓扑与合同 SLO 定义验收底线，框架不硬编码通用阈值。 |
| 可移植运行器边界 | 原生命令保持在域逻辑之外。 |
| 可重播决策 | 验收制品内容寻址且可验证，支持离线回放。 |

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

## 参考证据适配器

- DCGM GPU health
- NVLink health/bandwidth
- RDMA port/error health
- NCCL collective bandwidth/correctness
- Inference SLO: TTFT P99, TPOT P99, success ratio

## 外部验收契约

`AcceptanceArtifact` 是面向仓库外消费者的可移植输出边界，其 JSON 契约发布于 `schemas/acceptance-artifact.schema.json`。外部控制平面应消费封存的制品，而非重新运行 AI Factory 阈值逻辑。

`AcceptanceArtifact.digest` 证明内容完整性，不证明生产者身份；单独的 `AcceptanceAttestation` 将制品摘要绑定到密钥身份。参考实现使用 HMAC-SHA256，生产部署应替换为非对称 KMS/Sigstore/Cosign 后端。

## 快速开始

要求：Python 3.11+

```bash
make setup
make test
make demo
```

确定性演示无需 GPU 硬件，输出写入 `.artifacts/demo/acceptance.json`。

真实站点烟雾测试：

```bash
cp acceptance/examples/real-command-commissioning.template.json \
   acceptance/examples/my-site-commissioning.json
make smoke MANIFEST=acceptance/examples/my-site-commissioning.json
```

## 仓库地图

```text
src/ai_factory_engineering/   acceptance, collectors, runner, reports, replay
acceptance/tests/             AcceptanceTest specs
acceptance/examples/          plans, templates and reference manifests
examples/                     runnable demos
tests/                        unit, contract and integration tests
casebook/                     reference engineering cases
docs/                         architecture and AI Factory engineering notes
schemas/                      JSON schemas for artifacts, evidence, gates, plans
```

## 中文文档索引

- [项目总览 (README)](README.md)
- [贡献指南](CONTRIBUTING.zh-CN.md)
- [开发者工作流](DEVELOPMENT.zh-CN.md)
- [安全说明](SECURITY.zh-CN.md)
- [知识库索引](docs/zh-CN/README.md)

## 当前状态

v0.1 发布候选版。

**已实现**：原生采集器执行边界、EvidenceBundle 架构/验证、DCGM/NVLink/RDMA/NCCL/推理适配器、fail-closed 跨层 Gate DAG、确定性 576-GPU 参考验收演示、AcceptanceArtifact 摘要 + 参考证明、真实命令委托清单模板、`make demo` / `make smoke` 开发者工作流。

**尚未声明**：真实 576-GPU 生产委托运行、通用性能阈值、生产 KMS/Sigstore/Cosign 签名、覆盖每个供应商/版本的硬件特定解析器、替代供应商诊断或站点委托流程。

## 许可证

Apache License 2.0。详见 [LICENSE](LICENSE)。
