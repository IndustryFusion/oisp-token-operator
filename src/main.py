import kopf
import logging
import os
import yaml
import kubernetes
import time
import oisp

OISP_API_ROOT = os.environ.get('OISP_API_ROOT')
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')

client = oisp.Client(api_root=OISP_API_ROOT)
client.auth(USERNAME, PASSWORD)


@kopf.on.create('Pod')
def create_fn_pod(spec, name, namespace, logger, **kwargs):
    time.sleep(1)

    for i in spec.get('containers'):
        if namespace == "oisp-devices" and i.get('name') == "oisp-iot-agent":

            for item in i.get('env'):
                if item.get('name') == "OISP_DEVICE_ACTIVATION_CODE":
                    secret_name = item.get('valueFrom').get('secretKeyRef').get('name')

            
            accounts = client.get_accounts()

            device_token = accounts[0].get_activation_code()

            path = os.path.join(os.path.dirname(__file__), 'secret.yaml')
            tmpl = open(path, 'rt').read()

            text = tmpl.format(device_token=str(device_token), secret_name=str(secret_name))
            data = yaml.safe_load(text)
            
            print(data)
            api = kubernetes.client.CoreV1Api()
            obj = api.patch_namespaced_secret(
                name=secret_name,
                namespace=namespace,
                body=data
            )

            logger.info(f"Token updated successfully: {obj}")
