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
        file_names.remove(filename)
        _template = env.get_template(filename)
        rendered_template = _template.render(kwargs)
        with open(os.path.join(BASE_DIR, filename), 'w') as f:
            f.write(rendered_template)

        if exec_permission:
            _st = os.stat(os.path.join(BASE_DIR, filename))
            os.chmod(os.path.join(BASE_DIR, filename), _st.st_mode | stat.S_IEXEC)

    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Directory name to be created for the containerized model.')
    parser.add_argument('--base-docker-image-name', help='Base docker image for the containerized model.')
    parser.add_argument('--base-docker-image-tag', help='Base docker image for the containerized model.')
    args = parser.parse_args()

    # Base directory
    BASE_DIR = args.dir
    try:
        os.mkdir(BASE_DIR)
    except FileExistsError:
        pass

    # Templates
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    file_names = {'environment.yml', 'prediction_service.py', 'container_util.sh', 'Dockerfile'}

    # Dockerfile
    apply_template('Dockerfile', False, BASE_DOCKER_IMAGE_NAME=args.base_docker_image_name,
                   BASE_DOCKER_IMAGE_TAG=args.base_docker_image_tag)

    # Container util
    apply_template('container_util.sh', True, BASE_DOCKER_IMAGE_NAME=args.base_docker_image_name,
                   BASE_DOCKER_IMAGE_TAG=args.base_docker_image_tag)

    # Files without template
    for filename in file_names:
        template = env.get_template(filename)
        file_template = template.render()
        with open(os.path.join(BASE_DIR, filename), 'w') as f:
            f.write(file_template)


if __name__ == '__main__':
    main()
