S3 WINDOWS RIGHT CLICK UPLOAD

How to use:
- install python
- create dir for program and put here a script (s3up.py)
- `python -m pip install --upgrade pip`
- `pip install pipenv`
- run `pipenv install`
- run explorer and go to `shell:sendto`
- put here a cmd file (with appropriate path)

        @echo off
        cls
        c:\Users\<user>\.virtualenvs\s3upload-<unique>\Scripts\activate.bat && python C:\Users\<user>\s3upload\s3up.py %1
        cmd /k
    
- now you can right-click on any file and send it to S3 bucket