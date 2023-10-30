
	if (res_X.value!=old_resolution_x or res_Y.value!=old_resolution_y):
		if (w % 2 == 0): 
			k = 0;
			for i in range (-w//2, w//2+1):
				if (i<0):
					j=i+0.5
					X_axis[k] = j*res_X.value           
					k = k+1           
				else:
					if (i>0):
						j=i-0.5
						X_axis[k] = j*res_X.value             
						k = k+1
		else:
			for i in range (-w//2, w//2):
				X_axis[i+w/2 + 1] = i*res_X.value

		for i in range (0,h-1):
			Y_axis[i] = i*res_Y.value;

			old_resolution_x = res_X.value;
			old_resolution_y = res_X.value; 
