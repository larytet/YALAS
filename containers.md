From https://sysdig.com/press-releases/sysdig-2019-container-usage-report/

50% of containers live less than five minutes
This is a dramatic change from last year, when only 20% of containers lived less than five minutes. Many containers need to only live long enough to execute a function and then terminate when complete. The broader adoption of batch data processing with Kubernetes Jobs and serverless frameworks on Kubernetes have contributed to the growth of short-lived containers. The ephemeral nature of containers is one of the unique advantages of the technology, yet at the same time can be a challenge in managing issues around security, health, and performance. This reaffirms the fact that enterprises need real-time threat prevention as well as detailed auditing and forensics tools.

52% of images scanned by Sysdig have known vulnerabilities
The Sysdig report also finds that 40% of Sysdig customers’ images are from public sources. Considering less than one percent of Docker Hub images are certified trustworthy, using publicly sourced images exposes enterprises to risk. Enterprises need to embed security into the CI/CD pipeline, including scanning during the build phase, as well as checking for new vulnerabilities at runtime.

Containers-per-host density increases 100%
Over the past year, the median number of containers per host doubled to 30, indicating a growth in the number of applications being transitioned to cloud-native infrastructure and an increase in compute “horsepower,” which has enabled more containers to run on each node.

Use of Prometheus metrics increases 130%
Year-over-year, Prometheus metric use grew 130% across Sysdig customers – increasing to 46%. As the use of new programming frameworks expands, alternatives like JMX metrics (for Java applications) and StatsD are diminishing, down 45% and 17% respectively. Prometheus has been widely adopted as a metric standard in projects like Kubernetes, OpenShift, and Istio. In addition, an increasing number of “exporters” are available to provide metrics for a wide range of third-party applications and services. The increased volume of containers and hosts drives the need for tools that enable Prometheus monitoring at scale across clusters and clouds, such as Sysdig Monitor.

11% of customers are operating in multi-cloud
Multi-cloud is here thanks to Kubernetes. Eleven percent of Sysdig customers operate containers across more than one public cloud. Because of Kubernetes, which has been cemented as the de facto operating system of the cloud, enterprises do not have to fear vendor lock in and they are able to make multi-cloud a reality.

Go and Node.js overtake Java as top cloud application frameworks
There are clear winners for programming languages and frameworks. Go and Node.js overtook Java as top cloud app frameworks, neither of which made the top 10 list last year. Java has long been one of the most prominent programming languages, but newer options like Go, created by Google engineers, have gained favor in part because of their ease of use.

“With container density doubling since our last report, it’s evident that the rate of adoption is accelerating as usage matures. With that said, containers are black boxes that work well as application building blocks, but they are invisible to conventional security and visibility tools,” said Suresh Vasudevan, Sysdig Chief Executive Officer. “With this report, we hope to educate enterprises on existing challenges and how to run cloud-native environments in production, which should include a secure DevOps approach.”
