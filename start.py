import subprocess,threading,dataHandling,downloader
ans = subprocess.Popen(["py","server.py"])
threading.Thread(target=dataHandling.DataHandler, daemon=True).start()
threading.Thread(target=downloader.downloader, daemon=True).start()
ans.wait()