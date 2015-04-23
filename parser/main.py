import config
import parse

pipeout = open(config.PIPE_NAME, 'r')

while True:
    input_record = pipeout.readline()
    if input_record.split(',')[0] == '$GYRO':
        gyro = input_record
    if input_record.split(',')[0] == '$ACCEL':
        accel = pipeout.readline()
    if input_record.split(',')[0] == '$MAGNET':
        magnet = pipeout.readline()
    if input_record.split(',')[0] == '$MBAR':
        pressure = pipeout.readline()
    if all([gyro, accel, magnet, pressure]):
        parse.parse_IMU(gyro, accel, magnet, pressure)
        gyro = accel = magnet = pressure = None
