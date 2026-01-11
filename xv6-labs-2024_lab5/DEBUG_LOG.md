# OS Lab 5 调试日志 (Debug Log)

**日期**: 2026-01-07  
**作者**: Jacob  
**环境**: Linux (Ubuntu), QEMU, RISC-V Toolchain

## 1. 初始环境搭建与探索
- **操作**: 切换到 `net` 分支，运行 `make qemu` 确认环境正常。
- **观察**: `xv6` 启动正常。运行 `nettest` 提示并未实现相关功能。
- **分析**: 阅读 `e1000_dev.h` 和 `e1000.c`，确定 E1000 网卡的寄存器映射地址和 Ring Buffer 结构。需要实现 `e1000_transmit` 和 `e1000_recv`。

## 2. 阶段一：实现网卡发送 (e1000_transmit)
- **代码编写**:
  - 获取 `E1000_TDT` (Transmit Descriptor Tail) 索引。
  - 检查当前描述符是否即 `E1000_TXD_STAT_DD` 状态。
  - **问题**: 第一次运行时，忘记检查 `DD` 标志，导致直接覆盖了未发送的数据包。
  - **修正**: 增加 `if((tx_ring[idx].status & E1000_TXD_STAT_DD) == 0)` 判断，如果未完成则返回错误。
  - **内存管理**: 发现如果不释放旧的 `tx_bufs[idx]`，会导致内存泄漏。使用了 `mbuffree` (实验中为 `kfree`)。
  - 更新 `cmd` 字段为 `EOP | RS` (End of Packet | Report Status)。
- **调试**:
  - 运行 `python nettest.py txone` 和 `xv6: nettest txone`。
  - **现象**: 主机端未收到包。
  - **排查**: 检查 `regs[E1000_TDT]` 更新逻辑，发现未进行 `__sync_synchronize()` 内存屏障，导致硬件可能未立即看到更新。
  - **修正**: 增加内存屏障。测试通过。

## 3. 阶段二：实现网卡接收 (e1000_recv)
- **代码编写**:
  - 获取 `E1000_RDT` 并加一取模得到下一个待处理的描述符索引。
  - 循环检查 `status & E1000_RXD_STAT_DD`。
  - **问题**: 接收到一个包后，没有重新分配 `mbuf` 给描述符，导致同一个缓冲区被复用，数据混乱。
  - **修正**: 在提取数据传给 `net_rx` 后，立即调用 `kalloc()` 分配新 buffer 挂载到 RX Ring 中。
  - **死锁问题**: 在 `e1000_recv` 中调用 `net_rx`，`net_rx` 可能会再次涉及到锁的操作。虽然目前没死锁，但要注意锁的粒度。这里仅持有 `e1000_lock` 保护 Ring Buffer。
  - **修正**: 在调用 `net_rx` 之前释放锁，调用结束后重新获取锁，以防 `net_rx` 处理耗时过长或导致死锁。

## 4. 阶段三：实现 UDP 套接字层
- **Syscall 实现**:
  - `sys_bind`: 遍历 `sockets` 数组，找到空闲位并绑定端口。
    - **Bug**: 忘记初始化锁，导致 `acquire` 时 panic。
    - **修正**: 在 `netinit` 中初始化所有 socket 的锁。
  - `sys_recv`:
    - 实现 `sleep` 等待机制。当 `rxq` 为空时，调用 `sleep(&s->rxq, &s->lock)`。
    - **Bug**: 唤醒机制失效，进程一直睡眠。
    - **原因**: `ip_rx` 中收到包放入队列后，忘记调用 `wakeup`。
    - **修正**: 在 `ip_rx` 放入数据包后调用 `wakeup(&s->rxq)`。
  - `ip_rx`:
    - 负责分发 IP 包到 UDP socket。
    - **解析错误**: 初始代码直接假设 IP 头长度固定，导致计算 UDP 头偏移错误。
    - **修正**: 使用 `ip->ip_vhl` 计算各种长度的头部偏移。
    - **竞争条件检查**: 多个 CPU 同时接收包时，访问 `sockets` 数组需要加锁。使用了全局 `netlock` 保护 Socket 查找过程。


## 5. 总结
本次实验主要难点在于理解软硬件协同工作的 Ring Buffer 机制以及并发环境下的锁管理。通过逐步调试和日志分析，解决了问题。
