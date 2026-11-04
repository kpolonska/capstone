# M2 budget

Prices: t3.micro $0.0104/h, public IPv4 $0.005/h, gp3 \~$0.08/GB-month. 24/7 month = 730 h.
Plan: servers and disks are deleted after each session (ADR-002), 4 h/day x 30 days = +- 120 h/month.

|Service|M2 role|Calculation (120 h)|Lab hours|Worst case: 24/7|
|-|-|-|-|-|
|EC2 t3.micro x3|coordinator + 2 shards|0.0104 x 120 x 3|$3.74|$22.78|
|EBS gp3 8 GB x3|server disks|0.08 x 8 GB x 3 x (120/730)|$0.32|$1.92|
|Public IPv4 x1|coordinator only|0.005 x 120|$0.60|$3.65|
|Data transfer|benchmark traffic across AZs|\~10 GB x \~$0.02|$0.20|$0.20|
|S3|code package|<1 GB|$0.02|$0.02|
|VPC, subnets, IGW, CloudFormation|M1 network|free|$0|$0|
|CI/CD (GitHub Actions)|pipeline|free minutes|$0|$0|
|**Total per month**|||**\~$4.9**|**\~$28.6**|
|**Share of $50 credit**|||**\~10%**|**\~57%**|

One 4-hour session (servers + disks + IP): \~$0.16.

## Conclusion

Realistic cost is \~$4.9/month, about 10% of the $50 credit. The 24/7 column is the worst case if kv-app is left running, and is the reason I delete it after every session. The network stack costs $0.
