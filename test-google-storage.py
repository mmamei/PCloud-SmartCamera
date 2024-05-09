from google.cloud import storage
camera = 'cam1'
storage_client = storage.Client.from_service_account_json('credentials.json')
blobs = storage_client.list_blobs('upload-smart-camera', prefix=camera)
blobs = [b.name for b in blobs]
print(blobs)