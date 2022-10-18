"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
import argparse
import os
import stat
import shutil

from jinja2 import FileSystemLoader, Environment
import requirements

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
VALID_TYPES = ['python', 'h2o_mojo', 'python_xgboost_dmatrix', 'r_model', 'proxy']


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
            }
        }
        return file_metadata

    def apply_template(env, filename, exec_permission=False, **kwargs):
        _template = env.get_template(filename)
        if kwargs is not None:
            rendered_template = _template.render(kwargs)
        else:
            rendered_template = _template
        file_path = os.path.join(BASE_DIR, filename)

        with open(file_path, 'w') as f:
            f.write(rendered_template)

        if exec_permission:
            _st = os.stat(os.path.join(BASE_DIR, filename))
            os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

    def apply_templates(template_path, file_metadata):
        file_loader = FileSystemLoader(os.path.join(CURRENT_PATH, template_path))
        env = Environment(loader=file_loader)
        for filename, value in file_metadata.items():
            apply_template(env, filename, value.get('exec_permission'), **value.get('kwargs', {}))

    def generate_base(model_type):
        directory_names = {'src', 'model', 'templates'}
        create_directories(list(directory_names))

        # Common templates
        apply_templates('templates', generate_base_file_metadata())

        # Model-specific templates
        file_metadata = {
            'environment.yml': {
                'exec_permission': False,
            },
            'Dockerfile': {
                'exec_permission': False,
                'kwargs': {
                    'BASE_DOCKER_IMAGE': args.base_docker_image
                }
            },
            'src/prediction_service.py': {
                'exec_permission': False,
            },
            'src/utils.py': {
                'exec_permission': False,
            },
            'requirements.txt': {
                'exec_permission': False,
            },
            'model/metadata.yml': {
                'exec_permission': False,
            },
        }
        apply_templates(f'templates/{model_type}', file_metadata)

    def generate_proxy_base(model_type):
        directory_names = {'src', 'templates'}
        create_directories(list(directory_names))

        # Common templates
        apply_templates('templates', generate_base_file_metadata())

        # Model-specific templates
        file_metadata = {
            'environment.yml': {
                'exec_permission': False,
            },
            'Dockerfile': {
                'exec_permission': False,
                'kwargs': {
                    'BASE_DOCKER_IMAGE': args.base_docker_image
                }
            },
            'src/prediction_service.py': {
                'exec_permission': False,
            },
            'requirements.txt': {
                'exec_permission': False,
            }
        }
        apply_templates(f'templates/{model_type}', file_metadata)

    def generate_r_base(model_type):
        directory_names = {'src', 'model', 'templates'}
        create_directories(list(directory_names))

        # Common templates
        apply_templates('templates', generate_base_file_metadata())

        # Model-specific templates
        file_metadata = {
            'environment.yml': {
                'exec_permission': False,
            },
            'Dockerfile': {
                'exec_permission': False,
                'kwargs': {
                    'BASE_DOCKER_IMAGE': args.base_docker_image
                }
            },
            'src/run_server.R': {
                'exec_permission': False,
            },
            'src/prediction_service.R': {
                'exec_permission': False,
            },
            'requirements_bin.txt': {
                'exec_permission': False,
            },
            'requirements_src.txt': {
                'exec_permission': False,
            },
            'model/metadata.yml': {
                'exec_permission': False,
            },
        }
        apply_templates(f'templates/{model_type}', file_metadata)

    def generate_python(model_type):
        generate_base(model_type)

    def generate_h2o_mojo(model_type):
        generate_base(model_type)
        extra_directory_names = {'ext_packages', 'license'}
        create_directories(list(extra_directory_names))

    def generate_r_model(model_type):
        generate_r_base(model_type)

    def generate_proxy(model_type):
        generate_proxy_base(model_type)

    def copy_requirements_file():
        destination_path = os.path.join(BASE_DIR, 'requirements.txt')
        shutil.copyfile(args.requirements_file, destination_path)
        pyyaml_found = False
        with open(destination_path, 'r') as f:
            for req in requirements.parse(f):
                if (req.name.strip() == 'pyyaml'):
                    pyyaml_found = True
        if not pyyaml_found:
            with open(destination_path, 'a') as f:
                f.write('\npyyaml==5.4.1')

    def copy_prediction_service_file():
        destination_path = os.path.join(BASE_DIR, 'src', 'prediction_service.py')
        shutil.copyfile(args.prediction_service_file, destination_path)

    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Directory name to be created for the containerized model.')
    parser.add_argument('--base-docker-image', help='Base docker image for the containerized model.')
    parser.add_argument('--target-docker-image', help='Target docker image to be built.')
    parser.add_argument('--k8s-resource-name',
                        help='Name to be used as name in k8s resources (service, deployment, etc.).')
    parser.add_argument('--k8s-namespace',
                        help='Name to be used as namespace in k8s resources (service, deployment, etc.).')
    parser.add_argument('--model-type', choices=VALID_TYPES, help='Type of model you want to generate the code for. e.g h2o_mojo, python')
    parser.add_argument('--toolkit-path', help='Certifai toolkit path (unzipped directory)')
    parser.add_argument('--requirements-file', help='requirements.txt needed for model requirements')
    parser.add_argument('--prediction-service-file', help='Prediction service (prediction_service.py) file path')
    args = parser.parse_args()

    # Base directory
    BASE_DIR = args.dir
    model_type = args.model_type
    if model_type not in VALID_TYPES:
        print(f"'--model-type' must be one of {VALID_TYPES}")
        exit(1)

    if args.model_type == 'h2o_mojo':
        generate_h2o_mojo(model_type)
    elif args.model_type == 'r_model':
        generate_r_model(model_type)
    elif args.model_type == 'proxy':
        generate_proxy(model_type)
    else:
        generate_python(model_type)

    # Copy non-template files into the generated directory
    additional_files = ['config_deploy.sh', 'template_deploy.py',
                        'deployment_template.yml', 'deployment_config.yml']
    for file in additional_files:
        shutil.copyfile(os.path.join(CURRENT_PATH, 'templates', file),
                        os.path.join(BASE_DIR, file))

    # Copy readme files into the generated directory
    readme_files = ['README.md', 'DEPLOYMENT.md']
    for readme in readme_files:
        shutil.copyfile(os.path.join(CURRENT_PATH, readme), os.path.join(BASE_DIR, readme))

    # Copy certifai toolkit packages into generated directory
    shutil.copytree(os.path.join(args.toolkit_path, 'packages'), os.path.join(BASE_DIR, 'packages'))

    # Copy requirements file
    if args.requirements_file != "":
        copy_requirements_file()

    # Copy prediction service file
    if args.prediction_service_file != "":
        copy_prediction_service_file()


if __name__ == '__main__':
    main()
