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

    def generate_base_file_metadata():
        file_metadata = {
            'container_util.sh': {
                'exec_permission': True,
                'kwargs': {
                    'TARGET_DOCKER_IMAGE': args.target_docker_image
                }
            },
            'deployment.yml': {
                'exec_permission': False,
                'kwargs': {
                    'RESOURCE_NAME': args.k8s_resource_name,
                    'NAMESPACE': args.k8s_namespace
                }
            }
        }
        return file_metadata

    def generate_proxy(file_metadata):
        file_metadata.update({
            'environment_proxy.yml': {
                'exec_permission': False,
                'kwargs': {}
            },
            'Dockerfile.proxy': {
                'exec_permission': False,
                'kwargs': {
                    'BASE_DOCKER_IMAGE': args.base_docker_image
                }
            },
            'proxy_service.py': {
                'exec_permission': False,
                'kwargs': {}
            },
            'requirements_proxy.txt': {
                'exec_permission': False,
                'kwargs': {}
            }
        })

        directory_names = {'src'}
        src_files = {'proxy_service.py'}

        def apply_template(filename, exec_permission=False, **kwargs):
            _template = env.get_template(filename)
            rendered_template = _template.render(kwargs)

            if filename in src_files:
                file_path = os.path.join(BASE_DIR, 'src', 'prediction_service.py')
            elif filename == 'Dockerfile.proxy':
                file_path = os.path.join(BASE_DIR, 'Dockerfile')
            elif filename == 'environment_proxy.yml':
                file_path = os.path.join(BASE_DIR, 'environment.yml')
            elif filename == 'requirements_proxy.txt':
                file_path = os.path.join(BASE_DIR, 'requirements.txt')
            else:
                file_path = os.path.join(BASE_DIR, filename)
            with open(file_path, 'w') as f:
                f.write(rendered_template)

            if exec_permission:
                _st = os.stat(os.path.join(BASE_DIR, filename))
                os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

        create_directories(list(directory_names))
        # Templates
        file_loader = FileSystemLoader(os.path.join(CURRENT_PATH, 'templates'))
        env = Environment(loader=file_loader)

        for filename, value in file_metadata.items():
            apply_template(filename, value.get('exec_permission'), **value.get('kwargs'))

    def generate_r_model(file_metadata):
        file_metadata.update({
            'environment_R.yml': {
                'exec_permission': False,
                'kwargs': {}
            },
            'Dockerfile.R': {
                'exec_permission': False,
                'kwargs': {
                    'BASE_DOCKER_IMAGE': args.base_docker_image
                }
            },
            'prediction_service.R': {
                'exec_permission': False,
                'kwargs': {}
            },
            'run_server.R': {
                'exec_permission': False,
                'kwargs': {}
            },
            'requirements_bin_R.txt': {
                'exec_permission': False,
                'kwargs': {}
            },
            'requirements_src_R.txt': {
                'exec_permission': False,
                'kwargs': {}
            },
            'metadata_R.yml': {
                'exec_permission': False,
                'kwargs': {}
            },
            'deployment_R.yml': {
                'exec_permission': False,
                'kwargs': {}
            }
        })

        directory_names = {'src', 'model'}
        src_files = {'prediction_service.R', 'run_server.R'}
        model_files = {'metadata_R.yml'}

        def apply_template(filename, exec_permission=False, **kwargs):
            _template = env.get_template(filename)
            rendered_template = _template.render(kwargs)

            if filename in src_files:
                file_path = os.path.join(BASE_DIR, 'src', filename)
            elif filename in model_files:
                file_path = os.path.join(BASE_DIR, 'model', 'metadata.yml')
            elif filename == 'Dockerfile.R':
                file_path = os.path.join(BASE_DIR, 'Dockerfile')
            elif filename == 'environment_R.yml':
                file_path = os.path.join(BASE_DIR, 'environment.yml')
            elif filename == 'deployment_R.yml':
                file_path = os.path.join(BASE_DIR, 'deployment.yml')
            elif '_R.txt' in filename:
                file_path = os.path.join(BASE_DIR, filename)
            else:
                file_path = os.path.join(BASE_DIR, filename)
            with open(file_path, 'w') as f:
                f.write(rendered_template)

            if exec_permission:
                _st = os.stat(os.path.join(BASE_DIR, filename))
                os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

        create_directories(list(directory_names))
        # Templates
        file_loader = FileSystemLoader(os.path.join(CURRENT_PATH, 'templates'))
        env = Environment(loader=file_loader)

        for filename, value in file_metadata.items():
            apply_template(filename, value.get('exec_permission'), **value.get('kwargs'))

    def generate_python(file_metadata):

        file_metadata.update({
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
            'prediction_service.py': {
                'exec_permission': False,
                'kwargs': {}
            }
        })

        directory_names = {'src', 'model'}
        src_files = {'prediction_service.py'}

        def apply_template(filename, exec_permission=False, **kwargs):
            _template = env.get_template(filename)
            rendered_template = _template.render(kwargs)
            file_path = os.path.join(BASE_DIR, 'src', filename) if filename in src_files else os.path.join(BASE_DIR, filename)
            with open(file_path, 'w') as f:
                f.write(rendered_template)

            if exec_permission:
                _st = os.stat(os.path.join(BASE_DIR, filename))
                os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

        create_directories(list(directory_names))

        # Templates
        file_loader = FileSystemLoader(os.path.join(CURRENT_PATH, 'templates'))
        env = Environment(loader=file_loader)

        for filename, value in file_metadata.items():
            apply_template(filename, value.get('exec_permission'), **value.get('kwargs'))

    def generate_h2o_mojo(file_metadata):

        file_metadata.update({
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
            'prediction_service_h2o_mojo.py': {
                'exec_permission': False,
                'kwargs': {}
            }
        })

        directory_names = {'src', 'model', 'ext_packages', 'license'}
        src_files = {'prediction_service_h2o_mojo.py'}

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

        create_directories(list(directory_names))
        # Templates
        file_loader = FileSystemLoader(os.path.join(CURRENT_PATH, 'templates'))
        env = Environment(loader=file_loader)

        for filename, value in file_metadata.items():
            apply_template(filename, value.get('exec_permission'), **value.get('kwargs'))

    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Directory name to be created for the containerized model.')
    parser.add_argument('--base-docker-image', help='Base docker image for the containerized model.')
    parser.add_argument('--target-docker-image', help='Target docker image to be built.')
    parser.add_argument('--model-type', help='Type of model you want to generate the code. For e.g h20_mojo, python')
    parser.add_argument('--k8s-resource-name', help='Name to be used as name in k8s resources (service, deployment, etc.).')
    parser.add_argument('--k8s-namespace', help='Name to be used as namespace in k8s resources (service, deployment, etc.).')
    args = parser.parse_args()

    # Base directory
    BASE_DIR = args.dir

    file_metadata = generate_base_file_metadata()
    if args.model_type == 'h2o_mojo':
        generate_h2o_mojo(file_metadata)
    elif args.model_type == 'proxy':
        generate_proxy(file_metadata)
    elif args.model_type == 'r_model':
        generate_r_model(file_metadata)
    else:
        generate_python(file_metadata)

    # Copy readme into the generated directory
    readme_files = ['README.md', 'DEPLOYMENT.md']
    for readme in readme_files:
        shutil.copyfile(os.path.join(CURRENT_PATH, readme), os.path.join(BASE_DIR, readme))


if __name__ == '__main__':
    main()
