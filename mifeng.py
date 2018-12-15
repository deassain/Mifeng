from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526 import CreateInstanceRequest, DeleteInstanceRequest, RunInstancesRequest, \
    CreateSecurityGroupRequest, DescribeInstancesRequest, DescribeInstanceStatusRequest
import os, logging, json,math
import paramiko
from threading import Thread
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreadWithReturnValue(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)

    def join(self):
        Thread.join(self)
        return self._return

class Mifeng(object):
    client = None
    security_group = None
    vswitch = None
    region = None
    keypair_name = None
    ssh_key = None

    def __init__(self):
        self.client = self.get_client()

    def get_client(self):
        """

        :return: Alyun client id
        """
        try:
            self.keypair_name = os.environ["ALICLOUD_KEYPAIR_NAME"]
        except:
            logger.error("ALICLOUD_KEYPAIR_NAME environment variable not set")
            quit()
        try:
            self.access_key_id = os.environ["ALICLOUD_ACCESS_KEY"]
        except:
            logger.error("ALICLOUD_ACCESS_KEY environment variable not set")
            quit()
        try:
            self.access_secret = os.environ["ALICLOUD_SECRET_KEY"]
        except:
            logger.error("ALICLOUD_SECRET_KEY not set")
            quit()
        logger.info("Retrieved the access key id and secret")
        try:
            self.region = os.environ["MIFENG_REGION"]
        except:
            logger.error("MIFENG_REGION environment variable not set")
            quit()
        try:
            self.security_group = os.environ["MIFENG_SECURITY_GROUP"]
        except:
            logger.error("MIFENG_SECURITY_GROUP environment variable not set")
            quit()
        try:
            self.vswitch = os.environ["MIFENG_VSWITCH"]
        except:
            logger.error("MIFENG_VSWITCH environment variable not set")
            quit()
        try:
            self.ssh_key = os.environ["MIFENG_SSH_KEY"]
        except:
            logger.error("MIFENG_SSH_KEY variable not set")
            quit()
        try:
            client = AcsClient(self.access_key_id, self.access_secret, self.region)
        except Exception, e:
            logger.error("Couldn't initiate the client, wrong credentials?")
            logger.exception(e)
            quit()
        return client

    def create_instances(self, amount):
        """

        :param amount: the amount of instances that should be created
        :return: list of instance IDs created
        """
        request = RunInstancesRequest.RunInstancesRequest()
        release_time = datetime.utcnow() + timedelta(minutes=60)
        release_time = release_time.strftime("%F%ZT%R:%SZ")
        request.set_Amount(amount)
        request.set_AutoReleaseTime(release_time)
        request.set_SecurityGroupId(self.security_group)
        request.set_InternetMaxBandwidthOut(1)
        request.set_KeyPairName(self.keypair_name)
        request.set_VSwitchId(self.vswitch)
        request.set_ImageId("ubuntu_16_0402_32_20G_alibase_20180409.vhd")
        request.set_InstanceType("ecs.t5-lc2m1.nano")
        response = self.client.do_action_with_exception(request)
        logger.info(response)
        json_doc = json.loads(response)
        result = json_doc["InstanceIdSets"]["InstanceIdSet"]
        return result

    def stop_and_release_instance(self, instance_id):
        request = DeleteInstanceRequest.DeleteInstanceRequest()
        request.set_InstanceId(instance_id)
        request.set_Force(True)
        response = self.client.do_action_with_exception(request)
        logger.info(response)

    def get_instance_description(self, instance_list):
        """

        :param instance_list: must be of type list
        :return: returns the json response
        """
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_PageSize(50)
        request.set_InstanceIds(json.dumps(instance_list))
        response = self.client.do_action_with_exception(request)

        result = json.loads(response)
        total_instances = float(result["TotalCount"])
        if total_instances > 50:
            pages = math.ceil(total_instances/50)
            page = 2
            while(page <= pages):
                request = DescribeInstancesRequest.DescribeInstancesRequest()
                request.set_PageNumber(page)
                request.set_PageSize(50)
                response = self.client.do_action_with_exception(request)
                jsonify = json.loads(response)
                print "2   %s" % jsonify
                result["Instances"]["Instance"] = result["Instances"]["Instance"] + jsonify["Instances"]["Instance"]
                page = page + 1
        return result

    def get_instance_ip_addresses(self, instance_list):
        """
        :param instance_list: the list of instance ids for which the info needs to be retrieved
        :return: list of tuples (instance_name, ip_address)
        """
        print instance_list
        x = self.get_instance_description(instance_list)
        instances = x["Instances"]["Instance"]
        print instances
        hosts = list()
        for i in instances:
            hosts.append((i["InstanceId"], i["PublicIpAddress"]["IpAddress"][0]), )
        return hosts

    def get_ip_addresses(self):
        instance_name_ip_addresses = self.get_instance_ip_addresses([x["InstanceId"] for x in self.get_all_instances()])
        return [x[1] for x in instance_name_ip_addresses]

    def get_all_instances(self):
        """
        :return: a list of instances in the form of [{u'Status': u'Running', u'InstanceId': u'i-t4nj1nslzb2xi2rx5020'}]
        """
        request = DescribeInstanceStatusRequest.DescribeInstanceStatusRequest()
        request.set_PageSize(50)
        response = self.client.do_action_with_exception(request)
        jsonify = json.loads(response)
        result = jsonify["InstanceStatuses"]["InstanceStatus"]

        total_instances = float(jsonify["TotalCount"])
        if total_instances > 50:
            pages = math.ceil(total_instances/50)
            page = 2
            while(page <= pages):
                request = DescribeInstanceStatusRequest.DescribeInstanceStatusRequest()
                request.set_PageNumber(page)
                request.set_PageSize(50)
                response = self.client.do_action_with_exception(request)
                jsonify = json.loads(response)
                result = result + jsonify["InstanceStatuses"]["InstanceStatus"]
                page = page + 1
        return result


    def _execute_ssh_command(self,ip_address,command):
        """

        :param ip_address:
        :param command:
        :return: stdin, stdout stderr
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
        ssh_client.connect(username="root", hostname=ip_address,
                           pkey=paramiko.RSAKey.from_private_key_file(filename=self.ssh_key))
        logger.info("Executing {}".format(command))
        stdin, stdout, stderr = ssh_client.exec_command(command)
        return (stdin, stdout, stderr)

    def _upload_file(self,ip_address,file_path_local,file_path_remote):
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
        ssh_client.connect(username="root", hostname=ip_address,
                           pkey=paramiko.RSAKey.from_private_key_file(filename=self.ssh_key))

        sftp = ssh_client.open_sftp()
        sftp.put(file_path_local, file_path_remote)
        sftp.close()

    def _execute_on_all_wasps(self,command):
        # Create a threadlist and subsequently execute instaling tools concurently in each machine, subsequently join the threads before proceeding
        thread_list = list()
        ip_addresses = self.get_ip_addresses()
        print "[+] Executing in %s ip address"%len(ip_addresses)
        result_list = list()
        print ip_addresses
        for ip in ip_addresses:
            t = ThreadWithReturnValue(target=self._execute_ssh_command, args=(ip,command))
            thread_list.append(t)
        for t in thread_list: t.start()
        for t in thread_list:
           result_list.append(t.join())
        return result_list

    def _upload_file_on_all_wasps(self,file_path):
        print file_path
        thread_list = list()
        ip_addresses = self.get_ip_addresses()
        result_list = list()
        for ip in ip_addresses:
            t = ThreadWithReturnValue(target=self._upload_file, args=(ip, file_path,'/tmp/post.data'))
            thread_list.append(t)
        for t in thread_list: t.start()
        for t in thread_list:
            result_list.append(t.join())
        return result_list

    def install_ab_bench(self):
        self._execute_on_all_wasps("apt-get update && apt-get -y install apache2-utils")

    def run_ab_get(self,url):
        ab_command = 'ab -t 600 -n 100000 -c 20 -H "User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36" %s' % url
        self._execute_on_all_wasps(ab_command)

    def run_ab_post_random(self,url):
        generate_post_data="""echo -e "import urllib,random,string\noutfile = open('/tmp/post.data', 'w')\ndata = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1000000))\nparams = ({ 'auth_token': data })\nencoded=urllib.urlencode(params)\noutfile.write(encoded)\noutfile.close()" | python """
        ab_command = 'ab -t 900 -n 1000000 -c 20 -p /tmp/post.data -H "User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36" %s' % url
        self._execute_on_all_wasps(generate_post_data)
        self._execute_on_all_wasps(ab_command)

    def run_ab_post(self,url,file_path):
        print "uploading file"
        self._upload_file_on_all_wasps(file_path)
        ab_command = 'ab -t 900 -n 1000000 -c 20 -p /tmp/post.data -H "User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36" %s' % url
        self._execute_on_all_wasps(ab_command)