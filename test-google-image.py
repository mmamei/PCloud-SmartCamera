import io
from google.cloud import vision

# Instantiates a client
client = vision.ImageAnnotatorClient.from_service_account_json('credentials.json')
# The name of the image file to annotate
file_name = 'tmp/PXL_20231203_065456467.jpg'

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

#image = vision.Image(content=content)

image = vision.Image()
image.source.image_uri = 'gs://upload-smart-camera/cam1-14_20_07'
response = client.face_detection(image=image)
faces = response.face_annotations
print('Faces',len(faces))