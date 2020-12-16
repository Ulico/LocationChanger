from geopy.geocoders import Nominatim
import subprocess
import os
import urllib
import zipfile

DEVELOPER_DISK_IMAGE_URL = 'https://github.com/haikieu/xcode-developer-disk-image-all-platforms/raw/master/DiskImages/iPhoneOS.platform/DeviceSupport/{v}.zip'


def coordinates_from_address(address):
    try:
        location = Nominatim(user_agent='changer').geocode(address)
        print("Location entered: " + location.address)
        return str(location.latitude) + ' ' + str(location.longitude)
    except:
        print('Cannot find address.')
        return None


def get_disk_image(version):
    print('Beginning file download...')
    download_loc = os.getcwd() + '\\' + version + '.zip'
    try:
        urllib.request.urlretrieve(
            DEVELOPER_DISK_IMAGE_URL.format(v=version), download_loc)
        print('Unzipping...')
        zipfile.ZipFile(download_loc).extractall()
        os.remove(download_loc)
    except urllib.error.HTTPError as e:
        print('Could not find Developer Disk Image (iOS ' + version + ').')


def mount_image(version):
    if not os.path.exists(os.getcwd() + '\\' + version):
        get_disk_image(version)
    cmd = 'cd ' + os.getcwd() + '\\ & ideviceimagemounter ' + os.getcwd() + '\\' + version + \
        '\\DeveloperDiskImage.dmg ' + os.getcwd() + '\\' + version + \
        '\\DeveloperDiskImage.dmg.signature'
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        print('Developer Disk Image mounted!')
        return True
    except Exception as e:
        if 'Device is locked' in e.output.decode() or 'Could not start' in e.output.decode():
            print('Please unlock your device and try again.')
        return False


def set_location(coordinates):
    try:
        cmd = 'cd ' + os.getcwd() + '\\ & idevicesetlocation -- ' + coordinates
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        print('Device location set to ' + coordinates + '.')
    except Exception as e:
        if 'Device is locked' in e.output.decode():
            print('Please unlock your device and try again.')
        elif 'No device found' in e.output.decode():
            print('Please connect your device.')
        elif 'Make sure a developer disk image is mounted!' in e.output.decode():
            cmd = 'cd ' + os.getcwd() + '\\ & ideviceinfo'
            version = [i for i in subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode(
            ).split('\n') if i.startswith('ProductVersion')][0].split(' ')[1][:4]
            if mount_image(version):
                set_location(coordinates)


coor = coordinates_from_address(input('Enter address: '))
if coor is not None:
    set_location(coor)
