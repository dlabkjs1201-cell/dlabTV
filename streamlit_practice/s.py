from pydub import AudioSegment

# 'input.mp3'를 'output.wav'로 변환
sound = AudioSegment.from_mp3("dddd.mp3")
sound.export("break.wav", format="wav")