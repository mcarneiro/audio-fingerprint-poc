# Fingerprint audio files & identify what's playing

## How to set up this POC

* `$ docker-compose build`
* `$ docker-compose run --rm --entrypoint bash dev`

Inside de container, for the first run, this command will create an empty database:
* `bash-4.2# python reset-database.py`

Add mp3 files to `./mp3` folder and run the command below to make it available for comparison:
* `bash-4.2# python collect-fingerprints-of-songs.py`

Get a recorded input sound to compare and run:
* `bash-4.2# python recognize_from_file.py [file.mp3]`

To test it locally, just run `docker-compose up` to make the lambda local server running and run:

```
$ curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d "$(cat test-request.json)"
```

Where `test-request.json` will have at least:

```
{
  "body": {"data": "[mp3 base64]"}
}
```

You can an example response with base64 of a file by doing:

```
$ echo "{
  \"body\": {"data": \"$(base64 audio.mp3 | sed ':a;N;$!ba;s/\n//g')\"}
}" > test-request.json
```

To run it on Lambda, you'll need to rebuild docker image:

```
$ docker build . -t my-audiofingerprint-poc:latest
```

Install [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html):

```
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install
```

Configure it:

```
$ echo '[default]
aws_access_key_id = [your access key id]
aws_secret_access_key = [your secret access key]
' > ~/.aws/credentials
```

And follow [these steps](https://aws.amazon.com/fr/blogs/aws/new-for-aws-lambda-container-image-support/) to upload the docker image to ECR, considering yout image name is `my-audiofingerprint-poc`, it's:

```
$ aws ecr create-repository --repository-name my-audiofingerprint-poc --image-scanning-configuration scanOnPush=true
```

It'll return something like:

```
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-east-1:1234567890:repository/my-audiofingerprint-poc",
        "registryId": "1234567890",
        "repositoryName": "my-audiofingerprint-poc",
        "repositoryUri": "1234567890.dkr.ecr.us-east-1.amazonaws.com/my-audiofingerprint-poc",
        "createdAt": "2021-03-13T01:31:38-03:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": true
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}
```

Then you tag your container and push it to ECR:

```
$ docker tag my-audiofingerprint-poc:latest 1234567890.dkr.ecr.us-east-1.amazonaws.com/my-audiofingerprint-poc:latest
$ aws ecr get-login-password | docker login --username AWS --password-stdin 1234567890.dkr.ecr.us-east-1.amazonaws.com
$ docker push 1234567890.dkr.ecr.us-east-1.amazonaws.com/my-audiofingerprint-poc:latest
```

On Lambda, you'll need to define `MPLCONFIGDIR` with `/tmp/` value, as matplotlib needs to have write permission to run calculations in parallel.

With 2048MB of memory and with an input of 5s sound it takes around 2.5s to process it inside Lambda function.

To create the page on the front-end, just go to `front-end/` and run `npm install`. Create a `.npmrc` file with:

```
audio-fingerprint-poc:api=[your api gateway url]
```

To test it locally, specially on iPhone, you'll need to use a certificate. You can just send `server.crt` to [your iphone and trust this profile](https://blog.httpwatch.com/2013/12/12/five-tips-for-using-self-signed-ssl-certificates-with-ios/). Or you can [create your own certificate following these steps](https://blog.httpwatch.com/2013/12/12/five-tips-for-using-self-signed-ssl-certificates-with-ios/).

## Thanks to
- This POC was created based on this repo https://github.com/itspoma/audio-fingerprint-identifying-python and some parts of this https://github.com/vmizg/audio-fingerprint-identifying-python
- conference [PaceMaker: BackEnd-2016 conference](http://www.pacemaker.in.ua/BackEnd-2016/about)
- slides are on [slideshare.net/rodomansky/ok-shazam-la-lalalaa](http://www.slideshare.net/rodomansky/ok-shazam-la-lalalaa)
- [How does Shazam work](http://coding-geek.com/how-shazam-works/)
- [Audio fingerprinting and recognition in Python](https://github.com/worldveil/dejavu) - thanks for fingerprinting login via pynum
- [Audio Fingerprinting with Python and Numpy](http://willdrevo.com/fingerprinting-and-audio-recognition-with-python/)
- [Shazam It! Music Recognition Algorithms, Fingerprinting, and Processing](https://www.toptal.com/algorithms/shazam-it-music-processing-fingerprinting-and-recognition)
- [Creating Shazam in Java](http://royvanrijn.com/blog/2010/06/creating-shazam-in-java/)
