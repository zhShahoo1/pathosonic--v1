import cv2

def getcamidx():
	cidx = 1
	return cidx
  
  
def displayvideo():
	# define a video capture object
	vid = cv2.VideoCapture(getcamidx())

	while(True):

		# Capture the video frame
		# by frame
		ret, frame = vid.read()

		# Display the resulting frame
		cv2.imshow('frame', frame)

		# the 'q' button is set as the
		# quitting button you may use any
		# desired button of your choice
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	  
	# After the loop release the cap object
	vid.release()
	# Destroy all the windows
	cv2.destroyAllWindows()
	return


def gen_frames():
	camera = cv2.VideoCapture(getcamidx())  
	while True:
		success, frame = camera.read()  # read the camera frame
		
		if not success:
			break
		else:
			ret, buffer = cv2.imencode('.jpg', frame)
			frame = buffer.tobytes()
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')		

