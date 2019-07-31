from goprocam import GoProCamera, constants
import time
import qrcode
# import ffmpeg
import os
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
		self.lastVideo = None
		try:
			self.gpCam = GoProCamera.GoPro()
			self.gpCam.video_settings = settings
			self.baseURL = baseURL
			self.gpCam.gpControlSet(constants.Video.PROTUNE_VIDEO, constants.Video.ProTune.ON)
			# sync the time of the camera to the computer
			self.gpCam.syncTime()
		except:
			print("there was a problem connecting to the camera.") #well duh
			#do some error handling stuff here..?

	def takeVideo(self):
		now = datetime.now()
		videoName = '{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}.MP4'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
		print("Recording. ")
		try:
			self.gpCam.shoot_video(self.videoLength)
			self.lastVideo = videoName
		except:
			self.lastVideo = None

	def downloadVideo(self):
		print("downloading shot")
		self.gpCam.downloadLastMedia(custom_filename=self.lastVideo)

	def showQR(self):
		qrText = "http://" + '/'.join((self.baseURL, self.outputPath, self.lastVideo))
		qr = qrcode.make(qrText)
		qr.show()

	def newSession(self):
		for i in range(3, 0, -1):
			print(i)
			time.sleep(1)
		self.takeVideo()
		self.downloadVideo()
		self.showQR()
