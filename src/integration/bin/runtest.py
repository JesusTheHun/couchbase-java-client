__author__ = 'Subhashni Balakrishnan'

import argparse
import os
import subprocess

def run_command(command):
    print(command)
    proc = subprocess.Popen(['/bin/bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while proc.poll() is None:
        print(proc.stdout.readline())
    commandResult = proc.wait()
    return commandResult

def run_and_get_command_response(command):
    print(command)
    proc = subprocess.Popen(['/bin/bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = None
    while proc.poll() is None:
        if out == None:
            out = proc.stdout.readline()
            out = out.decode("utf-8")
    proc.wait()
    return out.rstrip()

def writeLine(file, content):
    file.write(content+'\n')

def write_core_test_properties(seedNode, bucket, password, path):
    print(seedNode + ',' + bucket + ',' + password)
    f = open('properties', 'w+')
    writeLine(f, 'seedNode='+seedNode)
    writeLine(f, 'bucket='+bucket)
    writeLine(f, 'username='+bucket)
    writeLine(f, 'password='+password)
    writeLine(f, 'adminUser=Administrator')
    writeLine(f, 'adminPassword=password')
    writeLine(f, 'ci=true')
    writeLine(f, 'mock.enabled=${useMock}')
    f.close()
    run_command('cat properties')
    if run_command('mv properties '+ path) < 0:
        print('unable to replace core test properties')
        os._exit(1)

def build_and_run_tests(seedNode, bucket, password):
    if run_command('git clone http://github.com/couchbase/couchbase-jvm-core') < 0:
        os._exit(1)
    write_core_test_properties(seedNode, bucket, password, 'couchbase-jvm-core/src/test/resources/integration/integration.properties')
    prev = os.getcwd()
    repo = os.getcwd() + "/.repository"
    os.chdir(prev+'/couchbase-jvm-core')
    run_command('mvn -Dmaven.repo.local="'+ repo +'" -Dsurefire.rerunFailingTestsCount=1 install')
    os.chdir(prev)
    if run_command('git clone http://github.com/couchbase/couchbase-java-client') < 0:
        os._exit(1)
    os.chdir(prev + '/couchbase-java-client')
    run_command('mvn  -Dmaven.repo.local="'+ repo +'" -Dsurefire.rerunFailingTestsCount=1 install' + ' -DseedNode=' + seedNode + ' -Dbucket=' + bucket + ' -Dpassword=' + password + ' -Dci=true')
    os.chdir(prev)

parser = argparse.ArgumentParser(description='Run Java Integration tests')
parser.add_argument('-c', '--cluster_versions', nargs='+', required=True)
args = parser.parse_args()
bucketName = 'default'
password = 'password'

for cluster_version in args.cluster_versions:
    CLUSTER_ID = run_and_get_command_response('cbdyncluster allocate --num-nodes=1 --server-version=' + cluster_version)
    print("cluster_id" + CLUSTER_ID)
    if CLUSTER_ID == None:
        print('Unable to allocate using cbdyncluster')
        os._exit(1)
    CB_NODE_FOR_CENTOS = run_and_get_command_response('cbdyncluster ips ' + CLUSTER_ID)
    print(CB_NODE_FOR_CENTOS)
    if CB_NODE_FOR_CENTOS == '':
        print('Unable to get the cb node using cbdyncluster')
        os._exit(1)
    run_command('cbdyncluster setup ' + CLUSTER_ID + ' --node=kv,index,n1ql --bucket=' + bucketName + ' --storage-mode=memory_optimized')
    run_command('curl -u Administrator:password -v -X POST http://' + CB_NODE_FOR_CENTOS + ':8091/pools/default -d "memoryQuota=2048"')
    run_command('curl -u Administrator:password -v -X POST http://' + CB_NODE_FOR_CENTOS + ':8091/pools/default/buckets/' + bucketName + ' -d "flushEnabled=1" -d "ramQuotaMB=100"')
    build_and_run_tests(CB_NODE_FOR_CENTOS, bucketName, password)
    run_command('cbdyncluster rm ' + CLUSTER_ID)
