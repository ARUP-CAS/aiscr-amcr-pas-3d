import ftplib
import os
import io

# File to be uploaded from the memory
def uploadToFtpFile(hostname, username, password, nazevSouboru, file):
	session = ftplib.FTP(hostname, username, password)
	session.encoding = 'utf-8'
	resp = session.storbinary('STOR ' + os.path.basename(nazevSouboru), file)
	print("FTP RESPONSE: " + str(resp))
	file.close()
	session.quit()

def downloadFromFtpFile(hostname, username, password, nazevSouboru):
	session = ftplib.FTP(hostname, username, password)
	f = io.BytesIO()
	resp = session.retrbinary('RETR ' + os.path.basename(nazevSouboru), f.write)
	print("FTP RESPONSE: " + str(resp))
	session.quit()
	return f
