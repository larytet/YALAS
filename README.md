# Yet another Linux audit system (YALAS)

A typical container relies on hundreds and ocassioally thousands of external packages. I routinely examine *go.sum* files 1KLOC and more. This is not feasible to verify all dependencies, proof read the code of hundreds of packages. Some packages have binary parts and can not be verified. The problem affects companies  small and large. R&D saves time by incorporating the 3rd party code. This is inevitable. The alternative is an expensive "not invented here" syndrom.

YALAS helps to generate and enforce the set of rules a container should follow.

YALAS has two components - a small kernel driver and an agent running in the VM's user space and taking care of the behavioural model.  YALAS learns what is the "correct behaviour" when the container is under the system test/unitest. YALAS automatically generates a set of rules describing the expected behaviour. In the production environment the tool alerts the administrator if the behaviour deviates from the previously observed behaviour (breaks the rules). Yes, YALAS is as good as it sounds. 

The code base is producton grade and ready for deployment. If your company needs this tool do not hesitate to contact me via **[Issues](https://github.com/larytet/YALAS/issues)** or **[LinkedIn](https://www.linkedin.com/in/arkadymiasnikov/)**. 

# Goals

*  Collect critical system information - writing to files, modification of system files, sending data to the outside world, shared memory operations, TTY, follow process execution chains.
*  Advanced debug and monitor infrastructure.
*  Collect the system information, filter and aggregate the information, compress it, deliver to an application for further processing. The design targets approximately 1:1000 reduction of the total amount of information. 
*  Support collection of the patterns of I/O requests, network access - applications fingerprints.
*  Simple deploy, install, update flow. Universal support of the existing Linux distributions and kernels.
* Automatic generation of behaviour models and enforcement.

# Applications

*  Prevent attempts of rights escalation.
*  Recognize debugger like behaviour.
*  Detect attempts of memory spray, attempts of exploit zero-day Linux kernel vulnerabilities.
*  Fingerprinting, analyzing, and comparison of the applications behaviour.
*  Monitor containers and VMs performance.

# Performace 

*  The design attempts to minimise the performance impact. The code targets system calls latency impact under 5 micro in the worst case and under 1 micro in the typical case. On a heavily loaded 16 core HTTP server performing lot of system calls the driver consumes roughly an equivalent of half a CPU core.
*  Zero-copy communication between kernel and user space.
*  Binary protocol between application and the driver.


# Running samples

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
5CAAE95F.BC11A97		CC4FFE6C	??	37	kprocess_exec	29BB2E	5E267BA3BE7C4	0	"./examples/http-server"	["./examples/http-server"]		1
5CAAE95F.11E1E11A		7BAE	http-server	18	syscall_openat	29BC26	5E267CC2640B8	0	FFFFFFFFFFFFFF9C	80000	0	"/proc/sys/net/core/somaxconn"	3
5CAAE95F.11E5AE34		38782F62	http-server	25	syscall_read	29BC28	5E267CC315D69	0	3	10000			4
5CAAE95F.11E67242		7BAE	http-server	25	syscall_read	29BC2A	5E267CC339A96	0	3	FFFC			0
5CAAE95F.12207739		7BAE	http-server	24	syscall_write	29BC2C	5E267CCDD39B4	0	1	11			11
5CAAE95F.12289E5C		D172381E	http-server	18	syscall_openat	29BC42	5E267CCF50F65	0	FFFFFFFFFFFFFF9C	0	0	"/etc//localtime"	3
5CAAE95F.1228D7E0		D174270C	http-server	25	syscall_read	29BC44	5E267CCF5B777	0	3	1000			8D9
5CAAE95F.1228EE60		D1744674	http-server	25	syscall_read	29BC46	5E267CCF5F942	0	3	1000			0
5CAAE95F.1229B145		73752F22	http-server	24	syscall_write	29BC48	5E267CCF8330E	0	2	38			38
5CAAE95F.1232D7F4		3E8	http-server	3	syscall_socket	29BC5E	5E267CD12F3F4	0	80801	2	6		3
5CAAE95F.1233437B		D17EC0C5	http-server	3	syscall_socket	29BC60	5E267CD142E4D	0	80801	A	6		3
5CAAE95F.12343110		D18112E6	http-server	3	syscall_socket	29BC64	5E267CD16E4DC	0	80801	A	6		5
5CAAE95F.1234A6ED		D183290E	http-server	3	syscall_socket	29BC68	5E267CD183D6F	0	80801	A	0		3
5CAAE963.66393DC	4FA7	4FA7	3E8	3E8	5CAADF85	??	37	kprocess_exec	29CF02	5E26A6391FDB1	0	"/usr/bin/curl"	["curl", "http://127.0.0.1:8080/?filepath=./hello.txt"]			1
5CAAE963.91F45B6		0	http-server	25	syscall_read	29D03C	5E26A6B8F8FF1	0	5	1000			63
5CAAE963.92AD4B3		17046F	http-server	24	syscall_write	29D03E	5E26A6BB15A9B	0	2	33			33
5CAAE963.92D3767		4250050	http-server	18	syscall_openat	29D054	5E26A6BB853EC	0	FFFFFFFFFFFFFF9C	80000	0	"/home/arkady/hello.txt"	6
5CAAE963.93707A6		A	http-server	25	syscall_read	29D056	5E26A6BD5049F	0	6	206			6
5CAAE963.93725FC		FFFFFF9C	http-server	25	syscall_read	29D058	5E26A6BD55D37	0	6	200			0
5CAAE963.965E74E		170486	http-server	24	syscall_write	29D05A	5E26A6C5E0DD3	0	5	7A			7A
5CAAE963.98391D6		0	http-server	25	syscall_read	29D06B	5E26A6CB4C8A5	0	5	1000			0
5CAAE964.83D497C	4FA8	4FA8	3E8	3E8	250058	??	37	kprocess_exec	29D380	5E26B173C4BD5	0	"/usr/bin/curl"	["curl", "http://127.0.0.1:8080/?filepath=./hello.txt"]		1
5CAAE964.A313A95		0	http-server	25	syscall_read	29D487	5E26B1CF1E29C	0	5	1000			FFFFFFFFFFFFFFF5
5CAAE964.A6A4820		696C2F22	http-server	25	syscall_read	29D4A2	5E26B1D98AE36	0	5	1000			63
5CAAE964.A6B5228		12612ABA	http-server	24	syscall_write	29D4A4	5E26B1D9BB7F8	0	2	33			33
5CAAE964.A6B9354		12613541	http-server	18	syscall_openat	29D4A6	5E26B1D9C767F	0	FFFFFFFFFFFFFF9C	80000	0	"/home/arkady/hello.txt"	6
5CAAE964.A6BF6A1		1261EC9C	http-server	25	syscall_read	29D4A8	5E26B1D9D98CB	0	6	206			6
5CAAE964.A6C06C9		1261F65F	http-server	25	syscall_read	29D4AA	5E26B1D9DC80B	0	6	200			0
5CAAE964.A6C5F32		732E3562	http-server	24	syscall_write	29D4AC	5E26B1D9ECA80	0	5	7A			7A
5CAAE964.A6CBA4D		3	http-server	25	syscall_read	29D4AE	5E26B1D9FD4D9	0	5	1000			FFFFFFFFFFFFFFF5
5CAAE964.A6FAC28		0	http-server	25	syscall_read	29D4B2	5E26B1DA870C4	0	5	1000			0
```

Pay attention to */etc//localtime*. This is not a bug: https://github.com/golang/go/issues/36640 

Another example of the consistent behaviour of the Golang runtime is the 1000/80000 buffer size in the read/write operations. 

The log above is translated into the stream of symbols 
```
ASLdhwf ASLdhwf  ASLdhwf CMLdowf AMLdjrf AMLdiwf BSLdhwf ASLdhwf ...
 ...
```

This is how an exploited vulnerability appears in the events stream 
```
...  ASLdhwf ASLdhwf ASLdhwf  COLdowf AOLdjwf AOLdiwf BSLdhwf ASLdhwf ...
```

Applying Markov process I get 59% vs 1.4% for "good" and "bad" symbol
```
... 0.591 0.591 0.591 0.014 0.012 0.012 0.591 0.591 ...
```

# Links

* https://www4.comp.polyu.edu.hk/~csxluo/DNSINFOCOM18.pdf
* https://github.com/jaegertracing/jaeger
* https://www.twistlock.com/labs-blog/
* https://github.com/draios/sysdig https://sysdig.com/opensource/falco/ https://www.businessinsider.com/30-cybersecurity-startups-2019-3
* https://www.styra.com/
* https://www.aporeto.com/
* https://gvisor.dev/
* https://www.aquasec.com/
* https://www.guardicore.com/ 
* Kata containers, gVisor, seccomp filters, Canonical's LXD, 
* https://caylent.com/50-useful-kubernetes-tools-for-2020
* Presentation https://docs.google.com/presentation/d/1SbedZdJR9A78U-MkATPCbj5dN6MRX0HBQbU4xk-q0Qw/edit?usp=sharing
* Video (Hebrew) https://www.youtube.com/watch?v=sPUehb_3kyU&feature=youtu.be&t=238
* According to this ad CrowdStrike attempts to do something similar: "This role will be part of the team designing and implementing new features to surface containers as logical end-points in the end-to-end Falcon product. These features will deliver the power of the Falcon end-point protection platform for Docker and other container implementations built on top of LXC". https://www.linkedin.com/jobs/view/2282865203  https://www.linkedin.com/jobs/view/2313573544
* https://sentry.io/
* https://newrelic.com/
* Kernel data flow diagram https://the-linux-channel.the-toffee-project.org/i/LINKS/1/Network%20API%20and%20data%20flow%20within%20Linux%20kernel.png
* https://www.upwind.io/


# Issues discovered by YALAS

* https://github.com/golang/go/issues/36640

# Q&A

* Is it like Prometheus?

No, YALAS is a generic system monitor which does not require any dedicated code in the container. YALAS collects system calls performed by the applications.YALAS goal is to catch zero days targeting containers. 

YALAS facilitates incident response, forensics. The engine allow placing an arbitrary test point in the code and monitoring the performance of the code in this point. There is no need to rebuild anything. Any system call the application performs will be collected, time stamped by the kernel.

The engine dedups the events, figures out repetitive patters, catches deviations from the previous behavior
This is done for any process/kernel thread in the container and for any container on a VM.

The engine allows to freeze a process if a certain condition met in order to help investigating. 

* Is it like Jaeger?

YALAS can collect and store packets using an arbiratry set of rules. YALAS does not require any modification of the sources code. YALAS observes the k8s pods from the outside, without a need for a code in the pod. Adding support for protobuf is in progress.

* Is YALAS aware of light threads, Go routines?

Go routines support is in progress. The kernel driver collects address of the user stack. The application maps all stacks, follows Go routines lifecycle. The model reflects the Go routines life cycle.

* Guardicore ?

Guardicore Centra carefully watches networking, maps end points communication, enforces a set of rules defined by the client. The existing product has minimal support for docker, does not collect file system events, does not follow process/thread life cycle, does not perform DPI. 

* Veronis/Imperva?

There is a small overlap between WAP/DAP and YALAS. YALAS can be used for logging of network events, audit of the transactions. YALAS out of box does not have application layer awareness.

* Calico? Istio?

The behavior of a pod is not simply the sum of the behaviors of its containers from a security perspective. What one container in a pod is allowed to do is not necessarily what another container should do. For instance, a main container in a pod may read/write to Redis, connect to Kafka, or load secrets. The Jaeger sidecar in the same pod, however, won't and shouldn’t perform any of those actions. If the Jaeger code is compromised, the way to minimize damage is by enforcing policies at a finer granularity level. Few products offer kernel thread-level granularity, which is what YALAS provides. Thread-level awareness is missing from Linux security solutions, but I believe that eventually, systems with such fine-grained control will become routine in VMs.

* Sysdig Falco?

YALAS and Sysdig Falco have a significant overlap. YALAS supports the run-time detection and prevention. One of the YALAS main goals is an automatic generation of formal enforcement policies and rules.
