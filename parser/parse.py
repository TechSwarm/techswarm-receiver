from timestamp import get_timestamp

def parse_IMU(gyro, accel, magnet):
    payload = {}
    
    payload['timestamp'] = get_timestamp()
    
    data = gyro.split(',')
    payload['gyro_x'] = int(data[1])
    payload['gyro_y'] = int(data[2])
    payload['gyro_z'] = int(data[3])

    data = accel.split(',')
    payload['accel_x'] = int(data[1])
    payload['accel_y'] = int(data[2])
    payload['accel_z'] = int(data[3])

    data = magnet.split(',')
    payload['magnet_x'] = int(data[1])
    payload['magnet_y'] = int(data[2])
    payload['magnet_z'] = int(data[3])
