import subprocess
import os

CWD = str(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/')
print CWD
if os.path.isfile(CWD + "/boot2docker.iso"):
    subprocess.call(
        str("docker-machine create -d hyperv --hyperv-boot2docker-url file://" +
            CWD +
            "/boot2docker.iso --hyperv-virtual-switch DockerNAT YANS-machine")
        .split())
else:
    subprocess.call(str("docker build -t my-boot2docker-img " + CWD).split())
    subprocess.call(
        str("docker run --rm my-boot2docker-img > " + CWD +
            "/boot2docker.iso").split())
    subprocess.call(
        str("docker-machine create -d hyperv --hyperv-boot2docker-url file://" +
            CWD +
            "/boot2docker.iso --hyperv-virtual-switch \"DockerNAT\" YANS-machine"
           ).split())
open(CWD + "/complete.txt", "a").close()
