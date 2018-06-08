import json
import logging
import os
import requests
import sys
from requests_toolbelt.multipart.encoder import MultipartEncoder


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

TTNMAPPER_URL = "https://www.ttnmapper.org/geojson/"


def get_config():
    try:
        config_file = os.environ['CONFIG_FILE']
        with open(config_file, 'r') as fhandle:
            config_data = json.load(fhandle)

        ckan_url = config_data['ckan_url']
        api_key = config_data['api_key']
        gateways = config_data['gateways']

    except json.decoder.JSONDecodeError:
        logging.error("Configuration file does not appear to be "
                      "valid JSON")
        sys.exit(1)

    except FileNotFoundError:
        logging.error("Configuration file was not found at %s"
                      % config_file)
        sys.exit(1)

    except KeyError:
        logging.error("Configuration file is missing required key. "
                      "Check you have url, api_key and gateways")
        sys.exit(1)

    return ckan_url, api_key, gateways


def process_gateway(ckan_url, api_key, gateway):
    logging.info("Fetching gateway's alphashape GeoJSON file")

    gw_url = ('%s%s/alphashape.geojson'
              % (TTNMAPPER_URL, gateway['ttn_id']))
    geojson_resp = requests.get(gw_url)

    if geojson_resp.status_code == 200:
        logging.info("Fetched GeoJSON file successfully")
        geojson_data = geojson_resp.text

    else:
        raise Exception("Unable to process gateway, couldn't fetch "
                        "GeoJSON data from TTNMapper service")

    logging.info("Uploading acquired data to CKAN service")

    multipart_data = MultipartEncoder(
        fields={
                'upload': ('alphashapre.geojson', geojson_data, 'text/plain'),
                'format': 'GeoJSON', 
                'id': gateway['ckan_id'],
                'name': gateway['name']
               }
        )

    headers = {'Content-Type': multipart_data.content_type,
               'Authorization': api_key}
    ckan_resp = requests.post('%sapi/action/resource_update' % ckan_url,
                              data=multipart_data,
                              headers=headers)

    if ckan_resp.status_code == 200:
        logging.info("Successfully updated gateway within CKAN")
    else:
        raise Exception("Error occured uploading data to CKAN: %s"
                        % ckan_resp.text)


def run_updater():
    logging.info("Running CKAN TTNMapper Updater")
    logging.info("Loading configuration file")
    ckan_url, api_key, gateways = get_config()

    logging.info("Updating resources at %s" % ckan_url)
    for gateway in gateways:
        logging.info("Currently processing %s" % gateway['name'])
        try:
            process_gateway(ckan_url, api_key, gateway)
        except Exception as err:
            logging.error("Error occured processing gateway: %s" % str(err))

    logging.info("Completed syncing data from TTNMapper to CKAN")


if __name__ == "__main__":
    run_updater()
