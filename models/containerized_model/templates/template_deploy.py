"""
Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
"""
import argparse
import yaml
import os

from jinja2 import Template

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

def main():
    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--resource-name', help='Name to use for prediction service resources')
    parser.add_argument('--namespace', help='K8s namespace to use for the prediction service.')
    parser.add_argument('--deployment-template', help='Deployment template to use for prediction service')
    parser.add_argument('--config-file', help='Configuration yaml to parameterize the deployment')
    parser.add_argument('--output-file', help='Where to write the output deployment yaml')
    args = parser.parse_args()

    with open(args.deployment_template) as deploy_file:
        template = Template(deploy_file.read())
    with open(args.config_file) as config_file:
        config = yaml.safe_load(config_file)
    rendered_template = template.render(config.get('deployment', {}).get('params', {}))

    with open(args.output_file, 'w') as f:
        f.write(rendered_template)


if __name__ == '__main__':
    main()
