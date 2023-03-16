import CameraStreaming

def main():
    streamer = CameraStreaming.CameraStreamer()
    while True:
        try:
            streamer.show_frame()
            # time.sleep(0.1)
        except AttributeError:
            pass
        
if __name__ == "__main__":
    main()
