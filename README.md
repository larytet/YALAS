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
5CA8392C.11FEDD40	5FDE	5FDE	3E8	3E8	0	??	37	kprocess_exec	53A8A5	636125280BA8	0	"./http-server"	["./http-server"]			1
5CA8392C.13C38853	5FDE	5FDE	3E8	3E8	5D419350	http-server	18	syscall_openat	53A8BF	6361296427D0	0	FFFFFFFFFFFFFF9C	80000	0	"/etc/passwd"	3
5CA8392C.13C8AF95	5FDE	5FDE	3E8	3E8	5CA7C1FC	http-server	25	syscall_read	53A8C1	636129707F39	0	3	1000			646
5CA8392C.13D61C8F	5FDE	5FDE	3E8	3E8	5CA7C1FC	http-server	24	syscall_write	53A8C3	63612990A69A	0	1	22			22
5CA8392C.13E53254	5FDE	5FDE	3E8	3E8	5CA7C1FC	http-server	18	syscall_openat	53A8C9	636129B4C746	0	FFFFFFFFFFFFFF9C	0	0	"/etc//localtime"	3
5CA8392C.13E56491	5FDE	5FDE	3E8	3E8	0	http-server	25	syscall_read	53A8CB	636129B53F67	0	3	1000			7F
5CA8392C.13E572B9	5FDE	5FDE	3E8	3E8	5CA7C1FC	http-server	25	syscall_read	53A8CD	636129B5615D	0	3	1000			0
5CA8392C.13E6EF6A	5FDE	5FDE	3E8	3E8	65732D6D	http-server	24	syscall_write	53A8CF	636129B8F12D	0	2	49			49
5CA8392C.13F77C3C	5FDE	5FDE	3E8	3E8	1	http-server	3	syscall_socket	53A8D5	636129E0941D	0	80801	2	6		3
5CA8392C.13F7F5E6	5FDE	5FDE	3E8	3E8	0	http-server	3	syscall_socket	53A8D7	636129E1B74D	0	80801	A	6		3
5CA8392C.13FA0631	5FDE	5FDE	3E8	3E8	64	http-server	3	syscall_socket	53A8DB	636129E6A887	0	80801	A	6		5
5CA8392C.13FA65FB	5FDE	5FDE	3E8	3E8	0	http-server	3	syscall_socket	53A8DF	636129E78DEC	0	80801	A	0		3
5CA8392C.13FE7E78	5FDE	5FDE	3E8	3E8	0	http-server	18	syscall_openat	53A8E1	636129F15D16	0	FFFFFFFFFFFFFF9C	80000	0	"/proc/sys/net/core/somaxconn"	5
5CA8392C.14001452	5FDE	5FDE	3E8	3E8	395A	http-server	25	syscall_read	53A8E3	636129F52916	0	5	10000			4
5CA8392C.1400379E	5FDE	5FDE	3E8	3E8	3E8	http-server	25	syscall_read	53A8E5	636129F57D91	0	5	FFFC			0
5CA8392C.1409F796	5FDE	5FDE	3E8	3E8	5CA7C201	http-server	5	syscall_accept4	53A8EA	63612A0CD747	0	3	70	0		FFFFFFFFFFFFFFF5
```

The log above is translated into the stream of symbols 
```
CFDB AFDB AFDB CCDB ACDB ACDB CFGB AFGB AFGB CFGB AFGB AFGB CFGB AFGB AFGB CFGB....
```

An exploited vulnerability appears in the stream like this 
```
CFGB AFGB AFGB ... CCGB ACGB ... CFGB AFGB AFGB
```

Applying Markov process I get 92% vs 0.15%
```
$ ./is_good.py -c CFGB -m ~/YALAS/model.pki
0.928
$ ./is_good.py -c AFGB -m ~/YALAS/model.pki
0.948
$ ./is_good.py -c CCGB -m ~/YALAS/model.pki
0.017
$ ./is_good.py -c ACGB -m ~/YALAS/model.pki
0.015
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
