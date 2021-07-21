import os
import sys
import time
import requests
from pprint import pprint
from kubernetes import config
from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.config import ConfigException

JFROG_API_KEY = ""
def get_remote_sha(image):
    repo_name = image.split("/")[0]
    container_name = image.split("/")[-1].split(":")[0]
    container_tag = image.split("/")[-1].split(":")[-1]
    url = "https://" + repo_name + "api/docker/krish/v2/" + container_name + "/manifests/" + container_tag
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json', 'X-Jfrog-Art-Api': JFROG_API_KEY}
    r = requests.head(url, headers=headers)
    r.raise_for_status()
    return r.headers["Docker-Content-Digest"].split(':')[-1]

def kill_pod(api, pod):
    result = api.delete_namespaced_pod(
        name = pod.metadata.name,
        namespace = pod.metadata.namespace,
        body = client.V1DeleteOptions(),
        pretty= 'true'
    )
    pprint(result)

    return result

    

def check_pods(conn, ret):
    for i in ret.items:
        try:
            current_sha = i.status.container_statuses[0].image_id.split(':')[-1]
            remote_sha  = get_remote_sha(i.status.container_statuses[0].image)
            if current_sha != remote_sha:
                print("New SHA:" , remote_sha)
                print("restarting pod to update them to use latest image version")
                kill_pod(conn,i)
        except Exception as error:
            print("ERROR: %s" % str(error))

def main():
    global JFROG_API_KEY
    
    try:
        JFROG_API_KEY = os.environ['JFROG_API_KEY']  # This api key can be passed as an environment variable in Pod deployment file
    except KeyError as ke:
        sys.exit("ERROR: Cannot load Jfrog Api Key")
    
    try:
        config.load_incluster_config()
    except ConfigException as ce:
        print("Cannot load in-cluster config, loading default config"+ str(ce))
        config.load_kube_config()    #It will load the default kube_config file, we can also pass the path of kube-config file
    try:
        sleep_time = os.environ['sleep_time']
    except KeyError as ke:
        print("sleep time not set, loading default sleep_time")
        sleep_time = 60.0
    
    while True:
        try:
           conn = client.CoreV1Api()  # makes a connection to kubernetes cluster
           ret = conn.list_pod_for_all_namespaces(watch=False, label_selector='nginx')
           check_pods(conn, ret)
        except ApiException as ae:
            print("Error API failure occured: "+ str(ae))
        
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()