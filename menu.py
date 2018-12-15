from mifeng import Mifeng
import logging,time, os, sys
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


mf = Mifeng()
menu_actions = {}


print """

            _  _
           | )/ )
        \\ |//,' __
        (")(_)-"()))=-
           (\\


"""

def _install_tools():
    mf.install_ab_bench()
    menu_actions['main_menu']()

def _release_wasps():
    instances_amount = raw_input("[+] How many?\n>>")
    try:
       instances_amount = int(instances_amount)
       if instances_amount < 1:
           print "[+] Not a positive integer."
           _release_wasps()
    except:
        "[-] Not an integer"
        _release_wasps()
    mf.create_instances(instances_amount)
    logger.info("Building images...")
    menu_actions['main_menu']()

def _tear_down():
    print "[+] Killing the swarm..."
    for x in mf.get_all_instances(): mf.stop_and_release_instance(x["InstanceId"])
    menu_actions['main_menu']()

def _get_wasp_status():
    result =  mf.get_all_instances()
    if result:
        res_dict = dict()
        for x in result:
            if x["Status"] in res_dict.keys():
                res_dict[x["Status"]] = res_dict[x["Status"]] + 1
            else:
                res_dict[x["Status"]] = 1
        for y in res_dict.keys():
            print "[+]"+ y + ": %s\n" % res_dict[y]
    else:
        print "[-] No instances running."
    menu_actions['main_menu']()


def _swarm():
    url = raw_input("Please enter the URL to be submitted to the Hive.")
    confirm_ah = raw_input("Are you sure you want to submit %s to the Hive (y/n)?"%url)
    if confirm_ah == "y":
        mf.run_ab_get(url)
        menu_actions['main_menu']()
    else:
        menu_actions['main_menu']()


def _swarm_post():
    url = raw_input("Please enter the URL to be submitted to the Hive.")
    post_path = raw_input("Please submit the POST file location to be uploaded.")
    confirm_ah = raw_input("Are you sure you want to submit %s to the Hive (y/n)?"%url)
    if confirm_ah == "y":
        print "submitting post"
        mf.run_ab_post(url,post_path)
        menu_actions['main_menu']()
    else:
        menu_actions['main_menu']()

def _swarm_post_random():
    url = raw_input("Please enter the URL to be submitted to the Hive.")
    confirm_ah = raw_input("Are you sure you want to submit %s to the Hive (y/n)?"%url)
    if confirm_ah == "y":
        mf.run_ab_post_random(url)
        menu_actions['main_menu']()
    else:
        menu_actions['main_menu']()

# =======================
#     MENUS FUNCTIONS
# =======================4

# Main menu
def main_menu():
    print "\n\n\n"
    print "1. Release the wasps"
    print "2. Get wasp status"
    print "3. Kill all wasps"
    print "4. Install tools"
    print "5. Run GET requests against URL"
    print "6. Run POST requests against URL"
    print "7. Run random POST requests against URL"
    print "\n0. Quit"
    choice = raw_input(">>  ")
    exec_menu(choice)
    return


# Execute menu
def exec_menu(choice):
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    return


menu_actions = {
    'main_menu': main_menu,
    '1': _release_wasps,
    '2': _get_wasp_status,
    '3': _tear_down,
    '4': _install_tools,
    '5': _swarm,
    '6': _swarm_post,
    '7': _swarm_post_random,
    '0': exit,
}



if __name__ == "__main__":
    # Launch main menu
    main_menu()