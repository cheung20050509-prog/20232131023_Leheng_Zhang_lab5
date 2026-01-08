# XV6 网络系统用户手册 (User Manual)

**版本**: 1.0  
**适用系统**: XV6 (Lab 5 Network)

## 1. 系统概述
本系统是基于 XV6 操作系统扩展的网络支持版本，集成了 Intel E1000 网卡驱动程序和简化的 TCP/IP 网络协议栈（支持 ARP, IP, UDP）。用户进程可以通过提供的 Socket API 进行网络通信。

## 2. 功能特性
- **网卡驱动**: 支持 E1000 网卡的 DMA 数据包发送与接收。
- **协议支持**:
  - **ARP**: 自动处理 ARP 请求与应答。
  - **IP**: 支持 IPv4 数据包的路由与分发。
  - **UDP**: 提供无连接的数据报传输服务。
- **并发控制**: 采用自旋锁和睡眠锁机制，支持多核环境下的网络操作。
- **系统调用**: 提供标准化的网络编程接口。

## 3. 编译与运行
### 3.1 环境要求
- Linux 环境 (推荐 Ubuntu 20.04+)
- RISC-V Toolchain (gcc, qemu-system-riscv64)
- Python 3 (用于测试脚本)

### 3.2 编译指令
在源码根目录下执行：
```bash
# 编译并运行 QEMU
make qemu

# 编译并运行评分测试
make grade
```

## 4. API 接口说明
本系统为用户程序提供了以下核心网络系统调用，定义在 `user/user.h` 中。

### 4.1 `bind` (绑定端口)
```c
int bind(short port);
```
- **描述**: 将当前进程绑定到指定的 UDP 端口。
- **参数**: `port` - 本地 UDP 端口号。
- **返回值**: 成功返回 0，失败返回 -1（如端口已被占用）。

### 4.2 `send` (发送数据)
```c
int send(short sport, int dst, short dport, char *buf, int len);
```
- **描述**: 发送 UDP 数据包。
- **参数**:
  - `sport`: 源端口号。
  - `dst`: 目的 IP 地址 (主机字节序)。
  - `dport`: 目的端口号。
  - `buf`: 数据缓冲区指针。
  - `len`: 数据长度。
- **返回值**: 成功返回 0，失败返回 -1。

### 4.3 `recv` (接收数据)
```c
int recv(short dport, int *src, short *sport, char *buf, int maxlen);
```
- **描述**: 从绑定端口接收 UDP 数据包。如果缓冲区为空，进程将阻塞等待。
- **参数**:
  - `dport`: 本地端口号（必须先调用 `bind`）。
  - `src`: 输出参数，存放发送方 IP 地址。
  - `sport`: 输出参数，存放发送方端口号。
  - `buf`: 接收缓冲区。
  - `maxlen`: 缓冲区最大长度。
- **返回值**: 成功返回实际读取的字节数，失败返回 -1。

## 5. 测试方法
系统内置了 `nettest` 用户程序用于功能验证。

### 5.1 单包发送测试
1. 主机端运行监听脚本: `python3 nettest.py txone`
2. XV6 终端运行: `nettest txone`
3. 预期结果: 主机收到数据包，XV6 显示 OK。

### 5.2 接收测试
1. XV6 终端运行: `nettest rxone` (会阻塞等待)
2. 主机端发送数据: `python3 nettest.py rxone`
3. 预期结果: XV6 收到 ARP 及 IP 包并打印日志。

### 5.3 综合测试 (DNS/Ping)
1. 直接运行: `make grade`
2. 系统将自动测试所有网络功能，包括 DNS 请求模拟和 Ping 测试。

## 6. 注意事项
- 本系统 IP 地址硬编码为 `10.0.2.15`，网关为 `10.0.2.2`。
- 接收缓冲区大小有限（Socket 接收队列长度为 16），高速发包可能导致丢包。
- 请勿在未 `bind` 的情况下调用 `recv`。
