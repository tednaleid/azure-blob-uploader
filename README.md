quick demo repo to show one way to upload blobs to azure storage account using the azure-storage-blob python sdk

run it with:

```shell
docker-compose up -d
```

and it'll kick off the main.py script to upload the blobs.

To list the blobs in the container, run:

```shell
docker compose run --rm uploader python list_blobs.py
```


You should see something like this:

```shell
docker compose run --rm uploader python list_blobs.py
[+] Running 2/0
 ⠿ Container azure-blob-uploader-azurite-1  Running                                                                                                                                                      0.0s
 ⠿ Container azure-blob-uploader-db-1       Running                                                                                                                                                      0.0s
[+] Running 1/1
 ⠿ Container azure-blob-uploader-uploader-1  Started                                                                                                                                                     0.2s
INFO:__main__:Listing blobs in container testcontainer:
INFO:azure.core.pipeline.policies.http_logging_policy:Request URL: 'http://azurite:10000/devstoreaccount1/testcontainer?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.24.1 Python/3.11.11 (Linux-6.5.0-15-generic-aarch64-with-glibc2.36)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': '78d51860-efe4-11ef-8b4b-0242ac150005'
    'Authorization': 'REDACTED'
No body was attached to the request
INFO:azure.core.pipeline.policies.http_logging_policy:Response status: 200
Response headers:
    'Server': 'Azurite-Blob/3.33.0'
    'content-type': 'application/xml'
    'x-ms-client-request-id': '78d51860-efe4-11ef-8b4b-0242ac150005'
    'x-ms-request-id': '5a476a7e-540f-4bcc-a3a1-7b59cb15f51c'
    'x-ms-version': 'REDACTED'
    'date': 'Thu, 20 Feb 2025 23:43:23 GMT'
    'Connection': 'keep-alive'
    'Keep-Alive': 'REDACTED'
    'Transfer-Encoding': 'chunked'
INFO:__main__:  1.xml (size: 110 bytes)
INFO:__main__:  10.xml (size: 112 bytes)
INFO:__main__:  100.xml (size: 114 bytes)
INFO:__main__:  1000.xml (size: 116 bytes)
INFO:__main__:  101.xml (size: 114 bytes)
INFO:__main__:  ...
INFO:__main__:
Total blobs: 1000
```

if we install the `az` [command line tool](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-cli) (`brew install azure-cli` on the mac), we can see files with:

```
az storage blob download -c testcontainer -n 1.xml --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;" --output none --no-progress
<root><id>1</id><data>Test data for record 1</data><timestamp>2025-02-20 22:55:08.664026+00</timestamp></root>
```