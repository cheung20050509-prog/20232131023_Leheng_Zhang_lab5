# 操作系统课程设计 - 实验5：网卡驱动 (Network Driver)

## 项目简介

本仓库包含操作系统课程设计实验5（网卡驱动）的完整实现。该项目旨在为 xv6 操作系统（RISC-V 架构）实现 E1000 网卡驱动程序以及支持 UDP/IP 协议的网络套接字接口。

## 目录结构说明

- **`xv6-labs-2024_lab5/`**: 项目主目录，包含 xv6 源代码和本次实验的所有实现。
  - **`kernel/e1000.c`**: E1000 网卡驱动的具体实现（负责数据包的发送与接收处理）。
  - **`kernel/net.c`**: 网络套接字层的实现（包含 `sys_bind`, `sys_recv` 以及 IP/UDP 协议处理逻辑）。
  - **`report.pdf`**: 正式的实验报告（由 LaTeX 生成）。
  - **`USER_MANUAL.md`**: 用户手册，详细说明了系统运行、测试及使用方法。
  - **`DEBUG_LOG.md`**: 调试日志，记录了开发过程中的调试信息与问题解决步骤。
  - **`time.txt`**: 实验耗时记录。

## 核心功能

- **E1000 网卡驱动**: 实现了基于 DMA 环形缓冲区的网络数据包发送与接收功能。
- **网络协议栈**: 支持 ARP、IP、UDP 协议解析，并提供了基于 Socket 的用户态通信接口。
- **测试通过**: 成功通过所有 `nettest` 功能测试点，包括 `txone`（发送）、`arp_rx`/`ip_rx`（接收）、`ping`（ICMP交互）、`dns`（UDP通信）以及内存泄漏检查。
- **评分**: 171/171 (满分)。

## 快速开始

### 运行系统

进入项目目录并启动 QEMU：

```bash
cd xv6-labs-2024_lab5
make qemu
```

### 运行测试

根据实验文档说明，建议使用以下方式进行手动测试：

#### 1. 基础功能测试 (NIC)
*   **测试发送 (Transmit)**:
    1.  打开终端 1，运行服务端脚本：
        ```bash
        python3 nettest.py txone
        ```
    2.  打开终端 2，启动 xv6：
        ```bash
        make qemu
        ```
        在 xv6 命令行中输入：
        ```bash
        nettest txone
        ```
        *预期结果*：终端 1 输出 `txone: OK`。

*   **测试接收 (Receive)**:
    1.  打开终端 1，启动 xv6：
        ```bash
        make qemu
        ```
    2.  打开终端 2，发送测试包：
        ```bash
        python3 nettest.py rxone
        ```
        *预期结果*：终端 1 (xv6) 输出 `arp_rx: received an ARP packet` 和 `ip_rx: received an IP packet`。

#### 2. 完整功能测试 (UDP Receive & Grade)
1.  打开终端 1，启动评分服务端：
    ```bash
    python3 nettest.py grade
    ```
2.  打开终端 2，启动 xv6：
    ```bash
    make qemu
    ```
    在 xv6 命令行中输入：
    ```bash
    nettest grade
    ```
    *预期结果*：通过一系列测试（ping, dns等），最终显示 `free: OK`，表明实验功能完整。

## 相关文档

- [实验报告 (PDF)](xv6-labs-2024_lab5/report.pdf)
- [用户手册 (User Manual)](xv6-labs-2024_lab5/USER_MANUAL.md)
- [调试日志 (Debug Log)](xv6-labs-2024_lab5/DEBUG_LOG.md)
