# Mifeng
A load testing tool inspired on Bees with Machine Guns targetted at leveraging Aliyun. Aliyun is Alibaba's cloud environment. I wanted to learn more about how they operate and the services they provide.

The tool I wrote is inspired on [Bees with Machine Guns](https://github.com/newsapps/beeswithmachineguns), which is a load testing tool written leveraging Amazon AWS.

## Some hard-coded values
The hardcoded values currently include the Apache Bench commands:
- The default image used is the ubuntu_16_0402_32_20G_alibase_20180409.vhd
- The instance type is ecs.t5-lc2m1.nano which is a burstable instance with 1 CPU and 512 MB of memory. This is sufficient for ab as it is single threaded.


## Environment variables
To use the tool there are a number of environment variables that need to be set:


| Environment Variables| Explanation           |
| ------------- |-------------|
| AccessKeyId    | [This is your Aliyun AccessKeyId](https://www.alibabacloud.com/help/doc-detail/29009.htm)  |
| AccessKeySecret  | This is the secret that's used together with your Id    |
| SecurityGroup | You will need to create a [Security Group](https://www.alibabacloud.com/help/doc-detail/25468.htm), the security group dictates what ports will be allowed to be open, you should make sure you allow port 22 (SSH).     |
| KeyPairName | When you configure Aliyun, you need to create a [keypair](https://partners-intl.aliyun.com/help/doc-detail/51793.htm). The keypair is used for public key authentication.  |
| VSwitch | The [VSwitch](https://www.alibabacloud.com/help/doc-detail/65387.htm) is used to dictate in what network you will deploy your instances and is Region dependant. Make sure that you deploy your instances in a dedicated VSwitch. The tear down operation of the script doesn't discriminate on instances and doesn't track the ID of the instances it created. Therefore if you mix these instances with existing instances, your existing instances may be deleted.     |
| Region | The [region](https://www.alibabacloud.com/help/doc-detail/40654.htm) is used to configure where the instances should be deployed. |
| SSHKey | This is the path to the SSH key on your machine associated with the KeyPairName you configured in Aliyun and set in the environment variable above.      |


## Gotchas on Aliyun when not using a business account
- Aliyun will allow you to only spin up a few instances, you should, after creating an account, verify your account with Aliyun by uploading your personal information. For instance passports.
- You will only be able to spin up a handful of servers, you need to request them to increase the amount of instances you can spin up. In my case I managed to get them to allow to spin up to 80 instances.

## Using the script
When using the script you will have a few options
