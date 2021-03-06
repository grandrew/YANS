import docker

from logging import debug
import sys
import subprocess
import os
import json
import ctypes
import sys
import time

docker_client = None
CWD = str(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/')


def exists(exe):
    debug('Checking if ' + exe + ' exists')
    if subprocess.call(exe, stdout=open('nul', 'w')) == 0:
        return True
    else:
        return False


def is_linux():
    return sys.platform == 'linux' or sys.platform == 'linux2'


def run(cmd, cont=False, popen=False):
    debug('Running command: ' + cmd)
    import shlex
    args = shlex.split(cmd)
    if cont:
        return subprocess.call(
            args, stdout=open('nul', 'w'), stderr=open('nul', 'w'))
    elif popen:
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    else:
        return subprocess.check_output(args)


def docker_machine_run(cmd, cont=False, popen=False):
    if is_linux():
        return run(cmd, cont, popen)
    else:
        return run('docker-machine ssh YANS-machine ' + cmd, cont, popen)


def create_links(links):
    for lnk in links:
        docker_machine_run('sudo brctl addbr ' + lnk.bridge_name)
        docker_machine_run('sudo ip link set ' + lnk.bridge_name + ' up')


def destroy_links(links):
    for lnk in links:
        docker_machine_run('sudo ip link set ' + lnk.bridge_name + ' down')
        docker_machine_run('sudo brctl delbr ' + lnk.bridge_name)


def create_nodes(nodes):
    if docker_machine_run("docker image inspect yans-node") != 0:
        docker_machine_run("docker load -i /data/yans-node.tar")
    for node in nodes:
        if docker_machine_run("docker inspect " + node.container_name) != 0:
            docker_machine_run("docker run --privileged -d --name " +
                               node.container_name +
                               " yans-node sleep 3153600000")


def destroy_nodes(nodes):
    for node in nodes:
        try:
            docker_machine_run(
                "docker container rm -f " + node.container_name, cont=True)
        except docker.errors.ContainerError:
            pass
    try:
        docker_machine_run("docker image rm -f yans-node", cont=True)
    except docker.errors.ImageNotFound:
        pass


def exec_in_node(node, args, will_return=False):
    import shlex
    set_docker_machine_env()
    args = "docker-machine ssh YANS-machine docker exec --privileged " + \
        node.container_name + " " + args
    debug('Running command: ' + args)
    if will_return:
        return subprocess.check_output(shlex.split(args))
    else:
        subprocess.call(shlex.split(args), stdout=sys.stdout)


def bind_interface(interface):
    docker_machine_run('sudo ip link add ' + interface.name +
                       ' type veth peer name ' + interface.peer_name)
    docker_machine_run('sudo ip link set ' + interface.peer_name + ' up')
    docker_machine_run('sudo brctl addif ' + interface.link.bridge_name + ' ' +
                       interface.peer_name)
    container_pid = str(
        json.loads(
            docker_machine_run(
                "docker inspect " + interface.node.container_name,
                cont=False,
                popen=True))[0]["State"]["Pid"])
    docker_machine_run('sudo ip link set netns ' + container_pid + ' dev ' +
                       interface.name)


def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def ensure_docker_machine():
    if not isAdmin():
        print "Must be ran with admin rights"
        sys.exit()
    if is_linux():  # docker machine not required on linux
        return
    if not exists('docker-machine'):
        sys.exit(
            "docker-machine is required to run yans on Mac OS X. Please make sure it is installed and in $PATH"
        )

    # create docker machine needed for YANS if one doesn't exist
    if run('docker-machine inspect YANS-machine', cont=True) != 0:
        print('Creating docker machine that will host all YANS containers')
        run("powershell -Command \"Start-Process PowerShell -Verb RunAs \"" +
            CWD + "/boot2docker/build-iso.py\"\"",
            cont=True)
        print "Please wait while YANS-machine is set up \nThis may take some time..."
        default_err = sys.stderr
        prog = 0
        while True:
            sys.stdout.write('.')
            prog += 1
            if prog >= 30:
                print "\n"
                prog = 0
            time.sleep(5)
            try:
                if os.path.isfile(CWD + "/boot2docker/complete.txt"):
                    os.remove(CWD + "/boot2docker/complete.txt")
                    sys.stderr = default_err
                    print "Complete"
                    break
            except Exception as e:
                pass
                # make sure YANS-machine is started
    run('docker-machine start YANS-machine', cont=True)


def client():
    ensure_docker_client()
    return docker_client


def ensure_docker_client():
    global docker_client
    if not docker_client:
        set_docker_machine_env()
        docker_client = docker.from_env()


def set_docker_machine_env():
    if not is_linux():
        out = run('docker-machine env YANS-machine')
        import re
        for (name, value) in re.findall('export ([^=]+)="(.+)"', out):
            os.environ[name] = value
