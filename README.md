# Yet another Linux audit system

If you think your company needs this tool do not hesitate to contact me via [issues](https://github.com/larytet/YALAS/issues) or [LinkedIn](https://www.linkedin.com/in/arkadymiasnikov/)

# What it does 

The tool learns what is the "correct behavior" when the container is under the system test/unitest. The tool creates a set of rules which describe the correct behavior. In the production environment the tool alerts the administrator if the behavior deviates from the the previously observed behavior (breaks the rules).

# Goals

*  Collect critical system information - writing to files, modification of system files, sending data to the outside world, shared memory operations, TTY logging, follow process execution chains.
*  Advanced debug and monitor infrastructure.
*  Collect the system information, filter and aggregate the information, compress it, deliver to an application for further processing. The design targets approximately 1:1000 reduction of the total amount of information. 
*  Support collection of the patterns of I/O requests, network access - applications fingerprints..  
*  Simple deploy, install, update flow. Universal support of the existing Linux distributions and kernels.
* Automatic generation of behaviour models and enforcement.


# Peformace 

*  The design attempts to minimise the performance impact. The code targets system calls latency impact under 5 micro in the worst case and under 1 micro in the typical case. On a heavily loaded 16 core HTTP server performing lot of system calls the driver consumes roughly an equivalent of half a core.
*  Zero-copy communication between kernel and user space.
*  Binary protocol between application and the driver.

# Applications

*  Prevent attempts of rights escalation.
*  Recognize debugger like behaviour.
*  Detect attempts of memory spray, attempts of exploit zero-day Linux kernel vulnerabilities.
*  Fingerprinting, analyzing and comparison of applications behaviour.
*  Monitor containers and VMs peformance.

# Visuals

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
5CAAE95F.BC11A97	4FA3	4FA3	3E8	3E8	CC4FFE6C	??	37	kprocess_exec	29BB2E	5E267BA3BE7C4	0	"./examples/http-server"	["./examples/http-server"]		1
5CAAE95F.11E1E11A	4FA3	4FA3	3E8	3E8	7BAE	http-server	18	syscall_openat	29BC26	5E267CC2640B8	0	FFFFFFFFFFFFFF9C	80000	0	"/proc/sys/net/core/somaxconn"	3
5CAAE95F.11E5AE34	4FA3	4FA3	3E8	3E8	38782F62	http-server	25	syscall_read	29BC28	5E267CC315D69	0	3	10000			4
5CAAE95F.11E67242	4FA3	4FA3	3E8	3E8	7BAE	http-server	25	syscall_read	29BC2A	5E267CC339A96	0	3	FFFC			0
5CAAE95F.12207739	4FA3	4FA3	3E8	3E8	7BAE	http-server	24	syscall_write	29BC2C	5E267CCDD39B4	0	1	11			11
5CAAE95F.12289E5C	4FA3	4FA3	3E8	3E8	D172381E	http-server	18	syscall_openat	29BC42	5E267CCF50F65	0	FFFFFFFFFFFFFF9C	0	0	"/etc//localtime"	3
5CAAE95F.1228D7E0	4FA3	4FA3	3E8	3E8	D174270C	http-server	25	syscall_read	29BC44	5E267CCF5B777	0	3	1000			8D9
5CAAE95F.1228EE60	4FA3	4FA3	3E8	3E8	D1744674	http-server	25	syscall_read	29BC46	5E267CCF5F942	0	3	1000			0
5CAAE95F.1229B145	4FA3	4FA3	3E8	3E8	73752F22	http-server	24	syscall_write	29BC48	5E267CCF8330E	0	2	38			38
5CAAE95F.1232D7F4	4FA3	4FA3	3E8	3E8	3E8	http-server	3	syscall_socket	29BC5E	5E267CD12F3F4	0	80801	2	6		3
5CAAE95F.1233437B	4FA3	4FA3	3E8	3E8	D17EC0C5	http-server	3	syscall_socket	29BC60	5E267CD142E4D	0	80801	A	6		3
5CAAE95F.12343110	4FA3	4FA3	3E8	3E8	D18112E6	http-server	3	syscall_socket	29BC64	5E267CD16E4DC	0	80801	A	6		5
5CAAE95F.1234A6ED	4FA3	4FA3	3E8	3E8	D183290E	http-server	3	syscall_socket	29BC68	5E267CD183D6F	0	80801	A	0		3
5CAAE963.66393DC	4FA7	4FA7	3E8	3E8	5CAADF85	??	37	kprocess_exec	29CF02	5E26A6391FDB1	0	"/usr/bin/curl"	["curl", "http://127.0.0.1:8080/?filepath=./hello.txt"]			1
5CAAE963.91F45B6	4FA3	4FA3	3E8	3E8	0	http-server	25	syscall_read	29D03C	5E26A6B8F8FF1	0	5	1000			63
5CAAE963.92AD4B3	4FA3	4FA3	3E8	3E8	17046F	http-server	24	syscall_write	29D03E	5E26A6BB15A9B	0	2	33			33
5CAAE963.92D3767	4FA3	4FA3	3E8	3E8	4250050	http-server	18	syscall_openat	29D054	5E26A6BB853EC	0	FFFFFFFFFFFFFF9C	80000	0	"/home/arkady/hello.txt"	6
5CAAE963.93707A6	4FA3	4FA3	3E8	3E8	A	http-server	25	syscall_read	29D056	5E26A6BD5049F	0	6	206			6
5CAAE963.93725FC	4FA3	4FA3	3E8	3E8	FFFFFF9C	http-server	25	syscall_read	29D058	5E26A6BD55D37	0	6	200			0
5CAAE963.965E74E	4FA3	4FA3	3E8	3E8	170486	http-server	24	syscall_write	29D05A	5E26A6C5E0DD3	0	5	7A			7A
5CAAE963.98391D6	4FA3	4FA3	3E8	3E8	0	http-server	25	syscall_read	29D06B	5E26A6CB4C8A5	0	5	1000			0
5CAAE964.83D497C	4FA8	4FA8	3E8	3E8	250058	??	37	kprocess_exec	29D380	5E26B173C4BD5	0	"/usr/bin/curl"	["curl", "http://127.0.0.1:8080/?filepath=./hello.txt"]		1
5CAAE964.A313A95	4FA3	4FA3	3E8	3E8	0	http-server	25	syscall_read	29D487	5E26B1CF1E29C	0	5	1000			FFFFFFFFFFFFFFF5
5CAAE964.A6A4820	4FA3	4FA3	3E8	3E8	696C2F22	http-server	25	syscall_read	29D4A2	5E26B1D98AE36	0	5	1000			63
5CAAE964.A6B5228	4FA3	4FA3	3E8	3E8	12612ABA	http-server	24	syscall_write	29D4A4	5E26B1D9BB7F8	0	2	33			33
5CAAE964.A6B9354	4FA3	4FA3	3E8	3E8	12613541	http-server	18	syscall_openat	29D4A6	5E26B1D9C767F	0	FFFFFFFFFFFFFF9C	80000	0	"/home/arkady/hello.txt"	6
5CAAE964.A6BF6A1	4FA3	4FA3	3E8	3E8	1261EC9C	http-server	25	syscall_read	29D4A8	5E26B1D9D98CB	0	6	206			6
5CAAE964.A6C06C9	4FA3	4FA3	3E8	3E8	1261F65F	http-server	25	syscall_read	29D4AA	5E26B1D9DC80B	0	6	200			0
5CAAE964.A6C5F32	4FA3	4FA3	3E8	3E8	732E3562	http-server	24	syscall_write	29D4AC	5E26B1D9ECA80	0	5	7A			7A
5CAAE964.A6CBA4D	4FA3	4FA3	3E8	3E8	3	http-server	25	syscall_read	29D4AE	5E26B1D9FD4D9	0	5	1000			FFFFFFFFFFFFFFF5
5CAAE964.A6FAC28	4FA3	4FA3	3E8	3E8	0	http-server	25	syscall_read	29D4B2	5E26B1DA870C4	0	5	1000			0
```

The log above is translated into the stream of symbols 
```
AQHdhf AQHdhfCQHdof AQHdhfAQHdifCLKdof ...
```

An exploited vulnerability appears in the stream like this 
```
...  AQHdhfAQHdifCLKdof ALKdhf ALKdhfCNKdof ANKdifCLKdof AQHXZCNHXZ ALKdofALKdjfCLKdof ...
```

Applying Markov process I get 69% vs 10% for "good" and "bad" symbol
```
$ ./is_good.py -c ALKdofALKdjfCLKdof -m ~/YALAS/model.pki
0.69
$ ./is_good.py -c ALKdhf -m ~/YALAS/model.pki
0.17
$ ./is_good.py -c AQHXZCNHXZ -m ~/YALAS/model.pki
0.06
$ ./is_good.py -c ALKdhfCNKdof  -m ~/YALAS/model.pki
0.12
$ ./is_good.py -c ANKdifCLKdof  -m ~/YALAS/model.pki
0.11
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

# Links

* https://www4.comp.polyu.edu.hk/~csxluo/DNSINFOCOM18.pdf
* https://github.com/jaegertracing/jaeger
* https://www.twistlock.com/labs-blog/
* https://github.com/draios/sysdig https://www.businessinsider.com/30-cybersecurity-startups-2019-3
* https://www.styra.com/
* https://www.aporeto.com/
