import os

def check_folders():
  if not os.path.exists("result"):
      os.makedirs("result")
    