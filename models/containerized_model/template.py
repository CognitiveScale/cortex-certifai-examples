"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
import argparse
import os
import stat

from jinja2 import FileSystemLoader, Environment


def main():

    def apply_template(filename, exec_permission=False, **kwargs):
        _template = env.get_template(filename)
        rendered_template = _template.render(kwargs)
        file_path = os.path.join(BASE_DIR, 'src', filename) if filename in src_files else os.path.join(BASE_DIR, filename)
        with open(file_path, 'w') as f:
            f.write(rendered_template)

        if exec_permission:
            _st = os.stat(os.path.join(BASE_DIR, filename))
            os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

    def create_directories(directory_list: list):
        for directory in directory_list:
            try:
                os.makedirs(os.path.join(BASE_DIR, directory))
            except FileExistsError:
                pass

    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Directory name to be created for the containerized model.')
    parser.add_argument('--base-docker-image', help='Base docker image for the containerized model.')
    parser.add_argument('--target-docker-image', help='Target docker image to be built.')
    # parser.add_argument('--model-type', help='Type of model you want to generate the code for. e.g h20_mojo, python')
    args = parser.parse_args()

    # Base directory
    BASE_DIR = args.dir

    directory_names = {'src', 'model'}
    src_files = {'prediction_service.py'}

    create_directories(list(directory_names))

    # Templates
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    file_metadata = {
        'environment.yml': {
            'exec_permission': False,
            'kwargs': {}
        },
        'Dockerfile': {
            'exec_permission': False,
            'kwargs': {
                'BASE_DOCKER_IMAGE': args.base_docker_image
            }
        },
        'container_util.sh': {
            'exec_permission': True,
            'kwargs': {
                'TARGET_DOCKER_IMAGE': args.target_docker_image
            }
        },
        'prediction_service.py': {
            'exec_permission': False,
            'kwargs': {}
        },
    }

    for filename, value in file_metadata.items():
        apply_template(filename, value.get('exec_permission'), **value.get('kwargs'))


if __name__ == '__main__':
    main()
