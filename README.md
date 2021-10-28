S3 WINDOWS RIGHT CLICK UPLOAD
============================

DESCRIPTION
--------------------------

This script allow you upload file to Amazon S3 bucket with one click (two, to be fair)


BUILD
--------------------------

You must have ANSI64.dll in project root (dll from ansicon)

    pyinstaller.exe --exclude-module _bootlocale --onefile --add-binary ANSI64.dll;. --clean  s3up.py

INSTALL
--------------------------

- download exe from `dist` folder
- next to him create .env file with credentials, see `.env.example`
- open `windows explorer` and type `shell:sendto` in path
- create there a `S3.cmd` file (with appropriate path to exe)

      @echo off
      cls
      cd /d <exe dir>
      s3up.exe %1
      taskkill /IM s3up.exe -F
    
- now you can right-click on any file, choose `Sent-to` and send it to S3 bucket
- link to download will be copy to buffer after upload