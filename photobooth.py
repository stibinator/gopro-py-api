from goprocam import GoProCamera, constants
import time
import qrcode
import ffmpeg
from datetime import datetime

class photoBooth(object):
	def __init__(self, outputPath = "goProVids", videoLength = 5, settings = ("1080p","120"), baseURL = "localhost"):
		try:
			os.mkdir(outputPath)
			print('created output folder' , outputPath)
		except FileExistsError:
			print("Directory ", outputPath, " will be used for video output")
        self.videoLength = videoLength
		self.outputPath = outputPath
		self.gpCam = GoProCamera.GoPro()
		self.gpCam.video_settings = settings
		self.baseURL = baseURL
		self.gpCam.gpControlSet(constants.Video.PROTUNE_VIDEO, constants.Video.ProTune.ON)
        # sync the time of the camera to the computer
        self.gpCam.syncTime()

	def takeVideo(self):
		for i in range(3, 0, -1):
			print(i)
			time.sleep(1)
		now = datetime.now()
		videoName = '{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}.MP4'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
		print("Recording. ")
		gpCam.shoot_video(videoLength)
		print("downloading shot")
		gpCam.downloadLastMedia(path=self.outputPath, custom_filename=videoName)
		return videoName

	def showQR(self, videoName):
		qrText = "http://" + '/'.join(self.baseURL, self.outputPath, videoName)
		qr = qrcode.make(qrText)
		qr.show()


