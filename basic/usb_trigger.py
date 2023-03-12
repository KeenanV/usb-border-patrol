import os
import time

# checks every 5 seconds for two storage devices to be plugged in
while True:
  # check for newly mounted devices
  stream = os.popen('lsblk')
  output = stream.readlines()

  # maintain a count of partitions
  sdaCount = 0
  sdbCount = 0

  # check for 1st and 2nd mounted devices
  for line in output:
    if line.includes('sda'):
      sdaCount++
    elif line.includes('sdb'):
      sdbCount++

  if sdaCount > 0 and sdbCount > 0:
    paths = []
    for i in (sdaCount - 1):
      paths.append('/dev/sda{}'.format(i + 1))
    for i in (sdbCount - 1):
      paths.append('/dev/sdb{}'.format(i+1))

    # TODO: change how paths are saved/sent to next script(s)
    print(paths)
    
    # prevent future temporarily, will need to change or final script needs to restart script
    break
  else:
    # missing at least one trigger condition
    time.sleep(5)
