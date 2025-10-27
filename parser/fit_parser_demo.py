from garmin_fit_sdk import Decoder, Stream

stream = Stream.from_file("../resource/20251001.fit")
decoder = Decoder(stream)
messages, errors = decoder.read()
print(errors)
print(messages)