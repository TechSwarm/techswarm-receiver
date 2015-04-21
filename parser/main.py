import config
import parse

pipeout = open(config.PIPE_NAME, 'r')

while True:
    input_record = pipeout.readline()
    if input_record.split(',')[0] == '$GYRO':
        gyro = input_record
        accel = pipeout.readline()
        magnet = pipeout.readline()
        pressure = pipeout.readline()
        parse.parse_IMU(gyro, accel, magnet, pressure)
