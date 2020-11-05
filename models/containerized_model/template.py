"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
import argparse
import os
import stat
import shutil

from jinja2 import FileSystemLoader, Environment

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def main():
    def create_directories(directory_list: list):
        for directory in directory_list:
            try:
                os.makedirs(os.path.join(BASE_DIR, directory))
            except FileExistsError:
                pass

    def generate_python():

        def apply_template(filename, exec_permission=False, **kwargs):
            _template = env.get_template(filename)
            rendered_template = _template.render(kwargs)
            file_path = os.path.join(BASE_DIR, 'src', filename) if filename in src_files else os.path.join(BASE_DIR,
                                                                                                           filename)
            with open(file_path, 'w') as f:
                f.write(rendered_template)

            if exec_permission:
                _st = os.stat(os.path.join(BASE_DIR, filename))
                os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

        directory_names = {'src', 'model'}
        src_files = {'prediction_service.py'}

        create_directories(list(directory_names))

        # Templates
        file_loader = FileSystemLoader(os.path.join(CURRENT_PATH, 'templates'))
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

            'requirements.txt': {
                'exec_permission': False,
                'kwargs': {}
            },

        }

        for filename, value in file_metadata.items():
            apply_template(filename, value.get('exec_permission'), **value.get('kwargs'))

    def generate_h2o_mojo():

        def apply_template(filename, exec_permission=False, **kwargs):
            _template = env.get_template(filename)
            rendered_template = _template.render(kwargs)

            if filename in src_files:
                file_path = os.path.join(BASE_DIR, 'src', 'prediction_service.py')
            elif filename == 'Dockerfile.h2o_mojo':
                file_path = os.path.join(BASE_DIR, 'Dockerfile')
            elif filename == 'environment_h2o_mojo.yml':
                file_path = os.path.join(BASE_DIR, 'environment.yml')
            else:
                file_path = os.path.join(BASE_DIR, filename)
            with open(file_path, 'w') as f:
                f.write(rendered_template)

            if exec_permission:
                _st = os.stat(os.path.join(BASE_DIR, filename))
                os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

        directory_names = {'src', 'model', 'ext_packages', 'license'}
        src_files = {'prediction_service_h2o_mojo.py'}

        create_directories(list(directory_names))
        # Templates
        file_loader = FileSystemLoader(os.path.join(CURRENT_PATH, 'templates'))
        env = Environment(loader=file_loader)

        file_metadata = {
            'environment_h2o_mojo.yml': {
                'exec_permission': False,
                'kwargs': {}
            },
            'Dockerfile.h2o_mojo': {
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
            'prediction_service_h2o_mojo.py': {
                'exec_permission': False,
                'kwargs': {}
            },

            'requirements.txt': {
                'exec_permission': False,
                'kwargs': {}
            },
        }

        for filename, value in file_metadata.items():
            apply_template(filename, value.get('exec_permission'), **value.get('kwargs'))

    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Directory name to be created for the containerized model.')
    parser.add_argument('--base-docker-image', help='Base docker image for the containerized model.')
    parser.add_argument('--target-docker-image', help='Target docker image to be built.')
    parser.add_argument('--model-type', help='Type of model you want to generate the code for. e.g h20_mojo, python')
    args = parser.parse_args()

    # Base directory
    BASE_DIR = args.dir

    if args.model_type == 'h2o_mojo':
        generate_h2o_mojo()
    else:
        generate_python()

    # Copy readme into the generated directory
    shutil.copyfile(os.path.join(CURRENT_PATH, 'README.md'), os.path.join(BASE_DIR, 'README.md'))


if __name__ == '__main__':
    main()
