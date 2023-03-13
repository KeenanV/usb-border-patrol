#!/bin/bash


contains_elem () {
	local ids=("$@")
	local target_id="$1"
	unset 'ids[0]'
	for jj in "${ids[@]}"; do
		if [[ "$jj" == "$target_id" ]]; then
			return 0 # true
		fi
	done
	return 1 # false
}


date >> /home/usbbp/devices.log
blocked=(0)

while true; do
	xinput_list=$(xinput list)
	# last_device_id=$(echo "$xinput_list" | grep -Eo 'id=[0-9]+' | sed 's/id=//g' | tail -n 1)
	id_list=($(echo "$xinput_list" | grep -Eo 'id=[0-9]+' | sed 's/id=//g'))
	# echo "ids: ${id_list[@]}" >> /root/block_dev.log

	for ii in "${id_list[@]}"; do
		if [[ "$ii" -ge 6 ]] && ! contains_elem "$ii" "${blocked[@]}"; then
			# xinput disable $ii
			blocked+=($ii)
			echo "Device disabled: $ii blocked list: ${blocked[@]}" >> /home/usbbp/devices.log
			date >> /home/usbbp/devices.log
		fi
	done
done

