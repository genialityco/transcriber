import sys
import subprocess
import os

def main():
    video_path = sys.argv[1]
    audio_path = video_path.replace(".mp4", ".wav")

    env = os.environ.copy()
    env["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-ar", "16000", "-ac", "1", audio_path],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    print(audio_path)

if __name__ == "__main__":
    main()