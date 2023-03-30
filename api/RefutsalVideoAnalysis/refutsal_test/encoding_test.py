import subprocess

input_file = 'test_265.avi'
output_file = 'output_264.avi'

command = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-strict', '-2', output_file]

subprocess.run(command)