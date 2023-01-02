#!/bin/bash

# Device info
IS_ARMBIAN=0
IS_ROCK64=0
IS_ROCKPRO64=0
IS_RASPI=0
IS_RASPI3=0
IS_RASPI4=0
IS_RASPI4_ARM64=0
IS_ROCKPI4=0
IS_X86=0
IS_32_BIT=0
IS_64_BIT=0
DEVICE_TYPE="unknown"
DEVICE_ARCH=$(uname -m) # Examples: armv7l aarch64 x86_64
MODEL=$(tr -d '\0' < /proc/device-tree/model) || MODEL="unknown"
DEBIAN_VERSION=$(lsb_release -c -s) || DEBIAN_VERSION="unknown"
uname -a | grep x86_64 && IS_X86=1 && IS_64_BIT=1 || true
if [[ $MODEL == *"Rock64"* ]]; then 
    IS_ARMBIAN=1
    IS_ROCK64=1
    IS_64_BIT=1
elif [[ $MODEL == *"RockPro64"* ]]; then 
    IS_ARMBIAN=1
    IS_ROCKPRO64=1
    IS_64_BIT=1
elif [[ $MODEL == *"Raspberry Pi 3"* ]]; then
    IS_RASPI=1
    IS_RASPI3=1
    IS_32_BIT=1
elif [[ $MODEL == *"Raspberry Pi 4"* ]]; then
    IS_RASPI=1
    IS_RASPI4=1
    IS_32_BIT=1
    UNAME=$(uname -a)
    if [[ $UNAME == *"aarch64"* ]]; then
        IS_RASPI4_ARM64=1
        IS_32_BIT=0
        IS_64_BIT=1
    fi
elif [[ $MODEL == *"ROCK Pi 4"* ]]; then
    IS_ARMBIAN=1
    IS_ROCKPI4=1
    IS_64_BIT=1
fi

if [ $IS_RASPI3 -eq 1 ]; then
    DEVICE_TYPE="raspi3"
elif [ $IS_RASPI4 -eq 1 ]; then
    DEVICE_TYPE="raspi4"
elif [ $IS_ROCKPI4 -eq 1 ]; then
    DEVICE_TYPE="rockpi4"
elif [ $IS_ROCK64 -eq 1 ]; then
    DEVICE_TYPE="rock64"
elif [ $IS_ROCKPRO64 -eq 1 ]; then
    DEVICE_TYPE="rockpro64"
elif [ $IS_X86 -eq 1 ]; then
    DEVICE_TYPE="debian"
fi

TOTAL_RAM_GB=$(free --giga | grep Mem | awk '{print $2}')

SERIAL_NUM=$(mynode-get-device-serial)
