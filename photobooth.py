from goprocam import GoProCamera, constants
from datetime import datetime
import time, qrcode, keyboard, os, subprocess, platform
# import ffmpeg #for adding overlays etc.

class photoBooth(object):
	def __init__(self, outputPath = "goProVids", videoLength = 3, settings = ("1080p","120"), baseURL = "localhost"):
		try:
			os.mkdir(outputPath)
			print('created output folder' , outputPath)
		except FileExistsError:
			print("Directory ", outputPath, " will be used for video output")
		self.videoLength = videoLength
		self.settings = settings
		self.outputPath = outputPath
		self.baseURL = baseURL # base URL is the external-facing URL the user connects to with the QR code
		self.lastVideo = None
		try:
			self.gpCam = self.connectCamera()
		except:
			print("there was an error connecting to the camera")
			self.gpCam = None

	def connectCamera(self):
		theCamera = GoProCamera.GoPro()
		theCamera.video_settings = self.settings
		# protune turns on more controls on the camera
		theCamera.gpControlSet(constants.Video.PROTUNE_VIDEO, constants.Video.ProTune.ON)
		# sync the time of the camera to the computer
		theCamera.syncTime()
		return theCamera


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
		self.gpCam.downloadLastMedia(path=self.outputPath, custom_filename=self.lastVideo)
		
	def playVideo(self):
		# depending on the platform we can use openCV or a thrird party player like omxplayer on Raspberry Pi
		# TODO append QR to the end of the video with ffmpeg
		videoFilePath = os.path.join(self.outputPath, self.lastVideo)
		# v1 = (ffmpeg
		# 	.input(videoFilePath, r=25)
		# )
		# v2 = (ffmpeg
		# 	.input(qrCodePath, loop=1, t=2)
		# 	.filter("scale", "1920/1080")
		# )
		# c = ffmpeg.concat(v1, v2).output(processedVideoPath, pix_fmt="yuv420p")
		# c.run()

		if platform.system() == 'Darwin':       # macOS
			subprocess.call(('open', videoFilePath))
		elif platform.system() == 'Windows':    # Windows
			os.startfile(videoFilePath)
		else:                                   # linux variants
			subprocess.call(('xdg-open', videoFilePath))

	def showQR(self):
		qrText = "http://" + '/'.join((self.baseURL, self.outputPath, self.lastVideo))
		qr = qrcode.make(qrText)
		qr.show()

	def countDown(self):
		# do fancy countdown shenannigans here, or…
		for i in range(3, 0, -1):
			print(i)
			time.sleep(1)

	def newPhotoBoothSession(self):
		keepTrying = True
		while (not self.gpCam and keepTrying):
			print ("No camera is connected.")
			keepTrying = input("Do you want to try to connect the camera? ").lower() == "y"
			if (keepTrying):
				self.connectCamera()

		if (self.gpCam):
			print ("press spacebar to start") 
			keyboard.wait(" ") # wait for spacebar - use GPIO etc
			self.countDown()
			self.takeVideo()
			self.downloadVideo()
			self.playVideo()
			self.showQR()