#
# Copyright (c) 2020. Cognitive Scale Inc. All rights reserved.
# Licensed under CognitiveScale Example Code License https://github.com/CognitiveScale/cortex-certifai-examples/blob/master/LICENSE.md
#

#!/usr/bin/env bash

DIR_NAME=$1
BASE_DOCKER_IMAGE=$2
BASE_DOCKER_TAG=$3

python template.py --dir=$DIR_NAME --base-docker-image-name=$BASE_DOCKER_IMAGE --base-docker-image-tag=$BASE_DOCKER_TAG
