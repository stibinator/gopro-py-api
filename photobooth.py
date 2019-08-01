from goprocam import GoProCamera, constants
from datetime import datetime
import time, qrcode, keyboard, os, subprocess, platform, ffmpeg

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
		self.processedVideo = None
		self.gpCam = self.connectCamera()

	def connectCamera(self):
		theCamera = None
		keepTrying = True
		while (not theCamera and keepTrying):
			print ("Attempting to connect to the camera.")
			if (keepTrying):
				try:
					theCamera = GoProCamera.GoPro()
					theCamera.video_settings = self.settings
					# protune turns on more controls on the camera
					theCamera.gpControlSet(constants.Video.PROTUNE_VIDEO, constants.Video.ProTune.ON)
					# sync the time of the camera to the computer
					theCamera.syncTime()
				except:
					print("problem connecting to the camera. Check your network settings")
					keepTrying = input("Do you want to try again? ").lower() == "y"	
					theCamera = None		
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
		self.gpCam.downloadLastMedia(path='', custom_filename=os.path.join(self.outputPath, self.lastVideo))

	def processVideo(self):
		videoFilePath = os.path.join(self.outputPath, self.lastVideo)
		processedVideoName = self.lastVideo.rsplit(".", 1)[0]+"_processed.MP4"
		processedVideoPath = os.path.join(self.outputPath, processedVideoName)
		try:
			v1 = (ffmpeg
				.input(videoFilePath, r=25)
			)
			v2 = (ffmpeg
				.input(qrCodePath, loop=1, t=2, r=25)
				.filter("scale", "1920/1080")
			)
			c = ffmpeg.concat(v1, v2).output(processedVideoPath, pix_fmt="yuv420p")
			c.run()
			self.processedVideo = processedVideoName
		except:
			print("error processing video")
			self.processedVideo = None
		
	def playVideo(self):
		videoFilePath = None
		if self.processedVideo:
			# depending on the platform we can use openCV or a thrird party player like omxplayer on Raspberry Pi
			videoFilePath = os.path.join(self.outputPath, self.processedVideo)
		elif self.lastVideo:
			videoFilePath = os.path.join(self.outputPath, self.lastVideo)
		if videoFilePath:	
			if platform.system() == 'Darwin':       # macOS
				subprocess.call(('open', videoFilePath))
			elif platform.system() == 'Windows':    # Windows
				os.startfile(videoFilePath)
			else:                                   # linux variants
				subprocess.call(('xdg-open', videoFilePath))
		else:
			print("No video to play")

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
		if (self.gpCam):
			print ("press spacebar to start") 
			keyboard.wait(" ") # wait for spacebar - use GPIO etc
			self.countDown()
			self.takeVideo()
			self.downloadVideo()
			self.processVideo()
			self.playVideo()
			self.showQR()