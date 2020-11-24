"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""

import os
import pickle
import yaml
from certifai.common.file.locaters import make_generic_locater
from certifai.common.file.interface import FilePath

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
ROOT_PATH=os.path.normpath(os.path.join(CURRENT_PATH,'..'))

def read_and_save_file(source_path, destination_path):
    if source_path is None:
        return
    # Fetch file as binary
    locater = make_generic_locater(FilePath(source_path))
    if locater.isfile():
        with locater.reader() as f:
            contents = f.read()
        with open(destination_path, 'wb') as f:
            f.write(contents)

def read_yaml(source_path):
    if source_path is None:
        return {}
    # Read file
    locater = make_generic_locater(FilePath(source_path))
    try:
        with locater.text_reader() as f:
            contents = f.read()
        return yaml.safe_load(contents)
    except FileNotFoundError:
        return {}


def load_metadata(root_path=ROOT_PATH):
    """
    Loads metadata from a yaml file at a location specified by METADATA_PATH.
    Defaults to 'model/metadata.yml' relative to root_path if no path is set.

    :param str root_path: Path to top of generated folder
    :return: metadata object
    """
    default_metadata_path = os.path.normpath(os.path.join(root_path,
        'model/metadata.yml'))
    metadata_path = os.getenv('METADATA_PATH', default_metadata_path)
    metadata = read_yaml(metadata_path)
    if metadata is None:
        metadata = {}
    return metadata


def fetch_model(root_path=ROOT_PATH):
    """
    Fetches the file at the location specified by MODEL_PATH, and saves
    it in the 'model' folder relative to root_path, with the same filename.

    :param str root_path: Path to local folder (must be writable)
    :return: the path to the model saved locally
    """
    model_path = os.getenv('MODEL_PATH')
    if model_path is not None:
        # Copy files from remote path to local
        local_model_path = os.path.normpath(os.path.join(root_path,
            'model', os.path.basename(model_path)))
        read_and_save_file(model_path, local_model_path)
    else:
        # allows local testing
        local_model_path = os.path.normpath(os.path.join(root_path,
            'model/pipeline.mojo'))
    return local_model_path

def setup_license_file(root_path=ROOT_PATH):
    """
    Fetches the license file at the url specified by the H2O_LICENSE_PATH
    environment variable, and saves
    it in the 'model' folder relative to root_path, with the same filename.
    Sets the H2O_LICENSE_PATH environment variable to this local path.

    :param str root_path: Path to local folder (must be writable)
    """
    license_path = os.getenv('H2O_LICENSE_PATH')
    if license_path is not None:
        default_license_path = os.path.normpath(
            os.path.join(root_path, 'license', os.path.basename(license_path)))
        read_and_save_file(license_path, default_license_path)
    else:
        default_license_path = os.path.normpath(os.path.join(root_path,
            'license/license.txt'))
    os.environ['DRIVERLESS_AI_LICENSE_FILE'] = default_license_path
