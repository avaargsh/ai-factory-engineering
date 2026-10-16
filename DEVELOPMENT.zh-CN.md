# 开发者工作流

```bash
make setup
make test
make demo
```

演示为确定性的，不需要 GPU 硬件。其输出写入 `.artifacts/demo/acceptance.json`。

对于真实站点烟雾运行，拷贝并编辑 `acceptance/examples/real-command-commissioning.template.json`，然后：

```bash
make smoke MANIFEST=acceptance/examples/my-site-commissioning.json
```

`make smoke` 执行该清单中声明的原生命令。在生产或共享 GPU 环境上运行前，请逐条审查每个命令和验收基线。
