# Mifeng
A load testing tool inspired on Bees with Machine Guns targetted at leveraging Aliyun. Aliyun is Alibaba's cloud environment. I wanted to learn more about how they operate and the services they provide. The tool I wrote is inspired on [Bees with Machine Guns](https://github.com/newsapps/beeswithmachineguns), which is a load testing tool written leveraging Amazon AWS.

## Some hard-coded values
The hardcoded values currently include the Apache Bench commands:
- The default image used is the ubuntu_16_0402_32_20G_alibase_20180409.vhd
- The instance type is ecs.t5-lc2m1.nano which is a burstable instance with 1 CPU and 512 MB of memory. This is sufficient for ab as it is single threaded.


## Environment variables
To use the tool there are a number of environment variables that need to be set:


| Environment Variables| Explanation           |
| ------------- |-------------|
| ALICLOUD_ACCESS_KEY   | [This is your Aliyun AccessKeyId](https://www.alibabacloud.com/help/doc-detail/29009.htm)  |
| ALICLOUD_SECRET_KEY  | This is the secret that's used together with your Id    |
| MIFENG_SECURITY_GROUP | You will need to create a [Security Group](https://www.alibabacloud.com/help/doc-detail/25468.htm), the security group dictates what ports will be allowed to be open, you should make sure you allow port 22 (SSH).     |
|MIFENG_VSWITCH| This is the [Vswitch](https://www.alibabacloud.com/help/doc-detail/65387.htm) that's defined within the region you intend to deploy on. Note that you should use a dedicated vswitch as the script will use this to trace the machines it can leverage for doing the testing. This means that if you have deployed other instances for other usage on the same vswitch, they may be killed after usage!|
| ALICLOUD_KEYPAIR_NAME | When you configure Aliyun, you need to create a [keypair](https://partners-intl.aliyun.com/help/doc-detail/51793.htm). The keypair is used for public key authentication.  |
| MIFENG_REGION | The [VSwitch](https://www.alibabacloud.com/help/doc-detail/65387.htm) is used to dictate in what network you will deploy your instances and is Region dependant. Make sure that you deploy your instances in a dedicated VSwitch. The tear down operation of the script doesn't discriminate on instances and doesn't track the ID of the instances it created. Therefore if you mix these instances with existing instances, your existing instances may be deleted.     |
| ALICLOUD_REGION| The [region](https://www.alibabacloud.com/help/doc-detail/40654.htm) is used to configure where the instances should be deployed. |
| MIFENG_SSH_KEY | This is the path to the SSH key on your machine associated with the ALICLOUD_KEYPAIR_NAME you configured in Aliyun and set in the environment variable above.      |

I added these to my .bashrc so they get loaded automatically every time I logon:

```
#Alibaba credentials
export ALICLOUD_ACCESS_KEY="youraccesskey"
export ALICLOUD_SECRET_KEY="yoursecret"
export MIFENG_SECURITY_GROUP="securitygroup"
export MIFENG_VSWITCH="vswitch"
export MIFENG_REGION="region"
export MIFENG_SSH_KEY="/home/user/.ssh/id_rsa" 
export ALICLOUD_KEYPAIR_NAME="my_keypair_name"
```


## Using the script
When using the script you will have a few options:


```
            _  _
           | )/ )
        \ |//,' __
        (")(_)-"()))=-
           (\


1. Release the wasps
2. Get wasp status
3. Kill all wasps
4. Install tools
5. Run GET requests against URL 
6. Run POST requests against URL 
7. Run random POST requests against URL 

0. Quit
```

To use the script you first spin up the `monitor.py` script on your local machine (or another machine, but preferably outside Aliyun). This script will periodically poll the website you have configured to test and log the response time. The reason I didn't include this (like Bees with Machineguns does) within the script executed on the machines, is that when people are using CloudFront or Akamai to protect their websites, inaccurate results can be shown (e.g. when the IP is blocked the request would time out. 

| Menu Item| Explanation           |
| ------------- |-------------|
|1. Release the wasps | Once you have launched the script you will need to first release your wasps which launch a bunch of machines. Note that if you already have machines running, they will be added to the farm. Also note that there is an auto-release after 60 minutes, that will automatically shut down your machines when deploying. |
|2. Get Wasp status|After deploying you can check on the status with option number 2. This will display if the instances are stopped (just created), starting or running. Wait until all your machines are running before proceeding. |
|3. Kill all wasps| This will kill all your machines that are running on the vswitch.|
|4. Install Tools|Once the machines are running, proceed with installing the tools with option 3. This will deploy all required tools (including apache bench, etc...). Note that there is no check in the script to verify if the tools have been installed. So if you get errors or don't see requests while running the POST requests, this may be due to tools still being installed.|
|5. Run GET Requests| This will run a lot of GET Requests for the given URL on the machine. If you are providing a URL without page, you should include a trailing `/`: http://example.com (won't work), but http://example.com/ (works). This is a limitation from Apache Bench unfortunately. |
|6. Run POST Requests| For this item you need to prepare a POST requests file on your local machine compliant with the Apache Bench format.|
|7. Run random POST requests| This generates a random POST file with the maximum size for a POST requests. The idea is that random POST requests are generated and submitted to the application with an overly large size (exhausting the webserver).|

## Gotchas on Aliyun when not using a business account
- Aliyun will allow you to only spin up a few instances, you should, after creating an account, verify your account with Aliyun by uploading your personal information. For instance passports.
- You will only be able to spin up a handful of servers, you need to request them to increase the amount of instances you can spin up. In my case I managed to get them to allow to spin up to 80 instances.
