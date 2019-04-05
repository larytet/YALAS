Yet Another Linux Audit System

The goals of the system:

*  Collect critical system information - writing to files, modification of system files, sending data to the outside world, shared memory operations, TTY logging, follow process execution chains.
*  The design attempts to minimise the performance impact. The code targets system calls latency impact under 5 micro in the worst case and under 1 micro in the typical case. On a heavily loaded 16 core HTTP server performing lot of system calls the driver consumes roughly an equivalent of one core.
*  Zero-copy communication between kernel and user space.
*  Binary protocol between application and the driver.
*  Advanced debug and monitor infrastructure.
*  Collect the system information, filter and aggregate the information, compress it, deliver to an application for further processing. The design targets approximately 1:1000 reduction of the total amount of information. 
*  Support collection of the patterns of I/O requests, network access - applications fingerprints..  
*  Simple deploy, install, update flow. Universal support of the existing Linux distributions and kernels.
 

# Applications

*  Prevent attempts of rights escalation.
*  Recognize debugger like behaviour.
*  Detect attempts of memory spray, attempts of exploit zero-day Linux kernel vulnerabilities.
*  Fingerprinting, analyzing and comparison of applications behaviour.
*  Monitor containers and VMs peformance.



Typical performance impact (single core VM) 

```
Tasks: 223 total,   1 running, 190 sleeping,   0 stopped,   0 zombie
%Cpu(s):  3.4 us,  3.1 sy,  0.0 ni, 93.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem :  4039720 total,   514340 free,  1766684 used,  1758696 buff/cache
KiB Swap:  1505860 total,  1505860 free,        0 used.  1908960 avail Mem 
  PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND                                                                                                                        
20700 arkady    20   0 1914484 251484 121416 S  5.3  6.2 106:15.68 firefox                                                                                                                                  
 1270 arkady    20   0 3080504 333312  84412 S  3.6  8.3   9:40.31 gnome-shell                                                                                                                              
 1101 arkady    20   0  545680 156048  82492 S  2.6  3.9  16:49.05 Xorg                                                                                                                                     
 1945 arkady    20   0  837280  49892  30032 S  1.6  1.2   2:02.64 gnome-terminal-                                                                                                                          
26931 root      rt   0  341216  67556  23176 S  1.6  1.7   0:01.12 yalas   <------ This is YALAS                                                                                                                                 
26943 arkady    20   0   49028   3816   3064 R  1.3  0.1   0:00.08 top                                                                                                                                      
```

Example of the log for a simple HTTP server in Golang
```
000000005CA793D9.0000000006D5E7D0	00001165	00001165	000003E8	000003E8	00000000	??	0000000000000037	kprocess_exec	0000000000004FD0	0000073634852D11	00	"/usr/bin/sudo"	["sudo", "LISTEN_ADDR=:8080", "USER=arkady", "ROOT=/home/arkady", "GOPATH=/home/arkady/go", "./http-server"]			0000000000000001
000000005CA793DD.0000000028D50363	00001166	00001166	00000000	00000000	00000000	??	0000000000000037	kprocess_exec	00000000000052F1	00000738C143050D	00	"./http-server"	["./http-server"]			0000000000000001
000000005CA793DD.000000002AEEE998	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000018	syscall_openat	0000000000005343	00000738C64BE55E	00	FFFFFFFFFFFFFF9C	0000000000080000	0000000000000000	"/proc/sys/net/core/somaxconn"	0000000000000003
000000005CA793DD.000000002AF99164	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000025	syscall_read	0000000000005345	00000738C6656D71	00	0000000000000003	0000000000010000			0000000000000004
000000005CA793DD.000000002AF9C194	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000025	syscall_read	0000000000005347	00000738C665E0A9	00	0000000000000003	000000000000FFFC			0000000000000000
000000005CA793DD.000000002B5DAE44	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000024	syscall_write	000000000000537D	00000738C7554F89	00	0000000000000001	0000000000000019			0000000000000019
000000005CA793DD.000000002B68761C	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000018	syscall_openat	0000000000005383	00000738C76F2458	00	FFFFFFFFFFFFFF9C	0000000000000000	0000000000000000	"/etc//localtime"	0000000000000003
000000005CA793DD.000000002B68AD8A	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000025	syscall_read	0000000000005385	00000738C76FA906	00	0000000000000003	0000000000001000			000000000000007F
000000005CA793DD.000000002B68BCA3	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000025	syscall_read	0000000000005387	00000738C76FCD42	00	0000000000000003	0000000000001000			0000000000000000
000000005CA793DD.000000002B68E79A	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000024	syscall_write	0000000000005389	00000738C7703426	00	0000000000000002	0000000000000040			0000000000000040
000000005CA793DD.000000002B775E26	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000003	syscall_socket	000000000000538F	00000738C792DC1F	00	0000000000080801	0000000000000002	0000000000000006		0000000000000003
000000005CA793DD.000000002B77EB3C	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000003	syscall_socket	0000000000005391	00000738C7942E0B	00	0000000000080801	000000000000000A	0000000000000006		0000000000000003
000000005CA793DD.000000002B783716	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000003	syscall_socket	0000000000005395	00000738C794E3BB	00	0000000000080801	000000000000000A	0000000000000006		0000000000000005
000000005CA793DD.000000002B787E68	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000003	syscall_socket	0000000000005399	00000738C7958EA3	00	0000000000080801	000000000000000A	0000000000000000		0000000000000003
000000005CA793DD.000000002B81AC20	00001166	00001166	00000000	00000000	00000000	http-server	0000000000000005	syscall_accept4	000000000000539E	00000738C7AB8CFE	00	0000000000000003	0000000000000070	0000		000000000		0FFFFFFFFFFFFFFF5
```

A sample of the driver stats

```
incidents                      43082075 bytes_total                  3640989272 socket.create.return                830
syscall.socket                      828 syscall.socket.return               828 syscall.accept4                       1
syscall.accept4                       7 syscall.accept.return                 1 syscall.accept4.return                7
syscall.bind                         29 syscall.bind.return                  29 syscall.connect                     206
syscall.connect.return              206 syscall.listen                        7 udp.sendmsg                          55
udp.recvmsg                          89 tcp.recvmsg                          72 syscall.recvfrom                   1272
syscall.recvfrom.return            1272 syscall.recv                          0 syscall.recvmmsg                      0
syscall.recvmsg                21846061 syscall.recv.return                   0 syscall.recvmmsg.return               0
syscall.recvmsg.return         21846061 syscall.sendto                      198 syscall.sendto.return               198
syscall.send                          0 syscall.sendmmsg                      9 syscall.sendmsg                  874207
syscall.send.return                   0 syscall.sendmmsg.return               9 syscall.sendmsg.return           874207
tcp.receive                          79 tcp.sendmsg                          27 syscall.creat                         0
syscall.open                          0 syscall.openat                  6913815 syscall.open.return                   0
syscall.creat.return                  0 syscall.openat.return           6913815 inode_err                             0
syscall.pipe                      32763 syscall.pipe.return               32763 syscall.dup                          40
syscall.dup2                      33115 syscall.dup3                          8 syscall.dup.return                   40
syscall.dup2.return               33115 syscall.dup3.return                   8 syscall.epoll_create                  3
syscall.eventfd                     206 syscall.shmget                        2 syscall.signalfd                      1
syscall.timerfd_create              276 syscall.close                   2431715 scheduler.process_exit            32825
syscall.write                   9251179 syscall.writev                   976471 syscall.pwrite                     1962
syscall.pwritev                       0 syscall.read                   12127586 syscall.read.return            12127583
syscall.write.return            9251179 syscall.writev.return            976471 syscall.pwrite.return                 0
syscall.pwritev.return                0 syscall.ptrace                        0 syscall.prctl                       152
syscall.seccomp                       0 kernel.syscall.uselib                 0 syscall.chown                        16
syscall.chmod                         9 syscall.rename                       65 syscall.renameat                      0
syscall.renameat2                     0 syscall.symlink                       2 syscall.symlinkat                     0
syscall.link                          0 syscall.linkat                        0 syscall.rmdir                        40
syscall.unlink                      121 syscall.unlinkat                     10 syscall.init_module                   0
syscall.finit_module                  0 syscall.delete_module                 0 syscall.clone.return              32820
scheduler.process_fork            32828 kprocess.exec                     95252 kernel.function_do_execve         95252
kprocess.exec_complete            95251 syscall.vfork                         0 syscall.exit                         90
syscall.exit_group                32059 vm.write_shared                 3062736 vm.mmap                          190604
vm.munmap                        351597 signal.syskill                       63 tty.write                       2201899
tty.read                        5167145 syscall.getcwd                    15664 syscall.getcwd.return             15664
syscall.chdir                        17 syscall.chdir.return                 17 syscall.fchdir                        0
syscall.fchdir.return                 0 syscall.mprotect                 365021 last_probe                           37
result_probe                   21508247 alloc_failed                          0 fifo_alloc                     43082063
fifo_alloc_normal              43082036 fifo_alloc_normal_ok           43082036 fifo_alloc_normal_fail                0
fifo_alloc_fail_1                     0 fifo_alloc_fail_2                     0 fifo_alloc_skip                      27
fifo_alloc_skip_lt                   15 fifo_alloc_race                       0 fifo_commit_race                      0
fifo_spinlock_fail                    0 shm_page_fault                   121151 sockaddr_len_err                      4
sockaddr_err                          0 sockaddr_copy_err                     0 sockaddr_copy_ok                    239
sockaddr_len_copy_err                 0 fork_same_pid                        96 kprocess_exec_miss                    0
kprocess_doexecve_hit                 0 begin                                 1 end                                   0
never                                 0 timer.ms                         236531 timer.sec                          2363
timer.jiffies                4297103664 
```

Links
* https://www4.comp.polyu.edu.hk/~csxluo/DNSINFOCOM18.pdf
