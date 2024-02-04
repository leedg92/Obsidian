
1. github 사이트에서 저장소 만들기

2. git 설치 후 로컬 디렉토리에 git 설정

3. 옵시디언 설정

## **github 사이트에서 저장소 만들기**

git과 github에 대한 설명은 이미 이 블로그에 찾아오신 것만으로도 충분히 알고 계실 거라 생각되어 생략하겠습니다.

깃헙 사이트는 아래 링크를 통해서 들어가시거나 구글에서 github을 검색하시면 됩니다.

 [GitHub: Let’s build from here

GitHub is where over 100 million developers shape the future of software, together. Contribute to the open source community, manage your Git repositories, review code like a pro, track bugs and fea...

github.com](https://github.com/)

▲ 먼저 깃헙 사이트에서 로그인을 합니다. 혹 회원 가입을 안 하셨다면 [Sign up] 버튼을 클릭하셔서 회원 가입 절차를 진행하시면 됩니다. 

![Create new... 버튼 클릭](https://blog.kakaocdn.net/dn/eRT8WD/btsvaq1Zdi1/VxeycoNJpdkSkZCrl5plk1/img.jpg)

<Create new... 버튼>

로그인 후 [Create new...] 버튼을 클릭합니다.

![New repository 버튼](https://blog.kakaocdn.net/dn/dRWwxR/btsvdn4JniE/KxEFf3KNVqZ5JRpqVbZc7K/img.jpg)

<New repository 버튼>

[New repository] 버튼을 클릭합니다.

![저장소 생성 폼](https://blog.kakaocdn.net/dn/qu96N/btsu7OIXOK1/SLeJJEqTcfz4ugwmAUq5EK/img.jpg)

<저장소 생성 폼>

신규 저장소를 생성하기 위한 입력 폼이 나옵니다.

① 저장소 이름 : 저 같은 경우 obsidian으로 생성했습니다.

② 저장소 설명 : 설명 입력은 옵션이기에 생략하셔도 됩니다.

③ 저장소 공개여부 : 다른 사람에게 내용을 전부 공개할 것이 아니라면 Private으로 설정합시다.

④ README 파일 생성 여부 : 향후 설정 편의를 위해 체크해 줍니다.

⑤ 위 과정이 완료되었다면 [Create repository] 버튼을 클릭합니다.

![생성된 저장소](https://blog.kakaocdn.net/dn/b5agUa/btsuZ0XUKba/f2YRczkVx3avTgV7iLKPM1/img.jpg)

<생성된 저장소>

짜잔~ 여러분의 노트가 저장될 깃헙 개인 저장소가 생성되었습니다.

생각보다 쉽죠??

## **git 설치 후 로컬 디렉토리에 git 설정**

이제 위에서 만든 깃헙 개인 저장소를 로컬 디렉토리에 연동시켜 보겠습니다.

로컬 디렉토리에 연결시키기 위해서는 git을 설치해야 하는데요.

git을 설치하기 위해서는 아래 링크로 들어가시거나 구글에서 git을 검색하시면 됩니다.

사이트에 들어가면 우측 중간에 다음과 같은 이미지가 있는데요.

![Download for Windows](https://blog.kakaocdn.net/dn/c0RtQJ/btsuSg72kkU/UCM8sCb4mR5WpGa315bQ9K/img.jpg)


[Download for Windows] 버튼을 클릭합시다.

![다운로드 설치 파일 선택](https://blog.kakaocdn.net/dn/4msO6/btsuTNYIWom/akpf8ipUNzPd39ygrk6ISK/img.jpg)


본인 운영체제에 맞는 설치 파일을 선택하시면 됩니다. 요즘에는 거의 [64-bit Git for Windows Setup.] 버튼을 클릭하시면 될 겁니다. 다운로드가 받아지면 해당 파일을 실행합니다.

![Git Setup](https://blog.kakaocdn.net/dn/tCJml/btsvaDtnvo3/QwKXE7ETUBL2AmDNSoyU1k/img.jpg)


파일을 실행하면 위와 같은 화면이 나옵니다. [Install]을 클릭합니다.

![설치 완료](https://blog.kakaocdn.net/dn/61xRC/btsuZSFqN1a/cNr2QxvOv7CrSNfDG3J900/img.jpg)

<설치 완료>

설치가 완료되었습니다. 참 쉽죠??

![폴더 생성](https://blog.kakaocdn.net/dn/bwkIkJ/btsu8jWzCyX/zsXWTSFrVAYmjfG8HIowp1/img.jpg)

<폴더 생성>

로컬에 앞으로 옵시디언 노트 파일을 저장하고자 하는 폴더를 생성합니다. 저 같은 경우 C 드라이브에 obsidian 폴더를 만들었습니다. 그리고 만든 폴더에 들어가서 우클릭하시고 [터미널에서 열기] 버튼을 클릭합니다. 혹 터미널 열기가 안된다면 [윈도우버튼 + R]을 누르신 후 cmd를 입력하여 터미널 창을 열 수 있습니다. 이런 경우에는 해당 폴더 경로까지 직접 이동하셔야 됩니다.

![git 명령어](https://blog.kakaocdn.net/dn/TBurp/btsuZ2ajEPF/E7DwKSdfySzPhmCpFYTCr1/img.jpg)


명령은 위와 같이 순서대로 입력하면 됩니다.

> git init  
> git remote add origin {새로 만든 깃헙 저장소 주소**}  
> git pull  
> git switch main

각 순서대로, 새로운 로컬 깃 저장소를 생성하는 명령, 로컬 저장소에서 깃헙 저장소를 연결하는 명령, 깃헙 저장소의 내용을 가져오는 명령, 브랜치를 변경하는 명령입니다.

참고로 {새로 만든 깃헙 자정소 주소}는 다음과 같이 알 수 있습니다.

![깃헙 저장소 URL](https://blog.kakaocdn.net/dn/Bwv7k/btsu2cDwifE/ZPoXksn61pUfrAPYX1Y8Q1/img.jpg)

<깃헙 저장소 URL>

아까 만들어진 깃헙 저장소에 들어가면 [< > Code ▼] 버튼을 클릭하면 URL이 나오는데 ② 버튼을 클릭하면 복사가 됩니다. 이 주소를 이용하여 위의 git remote add origin 명령을 수행하면 됩니다.

![성공 후 화면](https://blog.kakaocdn.net/dn/ljASx/btsvb3L7tAH/CvgXl1ceasayLdd7JVqt01/img.jpg)

<성공 후 화면>

성공하면 깃헙 원격 저장소와 연동되어 README 파일이 생깁니다.

![README 파일 삭제](https://blog.kakaocdn.net/dn/xbI1U/btsuZ2OXrAJ/kPhXFXMGpF7UWd5Zp7nfGk/img.jpg)

<README 파일 삭제>

README 파일은 굳이 필요 없으니 삭제를 해줍시다.

이로서 로컬 디렉토리 git 설정까지 끝났습니다.

여기까지 따라오느라 고생하셨습니다.

이제 마지막으로 옵시디언 설정이 남았네요.

## **옵시디언 설정**

옵시디언 역시 아래 링크로 들어가시거나 구글에서 obsidian을 검색하시면 됩니다.

 [Download - Obsidian

Obsidian is available on all major platforms. Download Obsidian for iOS, Android, macOS, Windows and Linux.

obsidian.md](https://obsidian.md/download)

![Download for Windows](https://blog.kakaocdn.net/dn/be4QF7/btsvfAXeh97/4o7rdIVwfBqmwxkMKO9xH0/img.jpg)


[Download for Windows] 버튼을 클릭하여 다운로드 받은 후 파일을 실행하여 설치를 합니다.

![언어 변경](https://blog.kakaocdn.net/dn/bumfqX/btsvdpasyea/Dt3eE7QtCqXdsieqoEVM00/img.jpg)

<언어 변경>

설치 후 위와 같은 화면이 나오는데요.

일단 우리는 한국인이니 언어부터 변경합시다.

빨간 박스 부분을 클릭하고 '한국어'를 선택하시면 됩니다.

![보관소 폴더 열기](https://blog.kakaocdn.net/dn/AxGWQ/btsvfCncUDT/AOedhXykIR9eE7QN6kFQik/img.jpg)

<보관소 폴더 열기>

[열기] 버튼을 클릭하여 위에서 설정한 git 디렉터리를 열어줍니다.

![폴더 생성](https://blog.kakaocdn.net/dn/bKubrr/btsuZRftxRO/igE0PlYi6kaeYB7C0EpsUk/img.jpg)

<폴더 생성>

정상적으로 진행되었다면 .git(깃 설정 폴더)와 .obsidian(옵시디언 설정 폴더)가 생성됩니다.

![설정](https://blog.kakaocdn.net/dn/xVWt1/btsuTPI52B1/DahiwoqYodyBRLD7KKX2q0/img.jpg)

<설정>

이제 옵시디언 화면이 열렸을 텐데요.

좌측 하단의 [설정] 버튼을 클릭해 줍시다.

![커뮤니티 플러그인 사용](https://blog.kakaocdn.net/dn/dZSqHc/btsu7PgPN4W/GWxUZFidLwBA9BzzrfzJo1/img.jpg)

<커뮤니티 플러그인 사용>

설정 화면에서 [커뮤니티 플러그인] 클릭 후 [커뮤니티 플러그인 사용] 버튼을 클릭합니다.

![커뮤니티 플러그인 탐색](https://blog.kakaocdn.net/dn/dep5bk/btsu0FeWmnT/buJqk1pgNOOcdWGwaah4bK/img.jpg)

<커뮤니티 플러그인 탐색>

[탐색] 버튼을 클릭합니다.

![git 검색](https://blog.kakaocdn.net/dn/QkTc9/btsvdpasyet/bvRrMkMxKqvkjdUDvoG1p1/img.jpg)

<git 검색>

git으로 검색하면 오늘의 주인공 Obsidian Git이 보입니다.

현시점에서 59만 다운로드를 기록하고 있네요. 저희도 받아줍시다.

[설치] 버튼을 클릭합니다.

![활성화](https://blog.kakaocdn.net/dn/bKfaSz/btsuSnGbWkx/rkRkaqmlheiywi7m2ZrRck/img.jpg)

<활성화>

플러그인을 사용하기 위해서는 활성화가 필요한데요.

[활성화] 버튼을 클릭합니다.

![옵션](https://blog.kakaocdn.net/dn/vYWZa/btsu0qBXvdy/onadyfmlsn9SDkNMp8jCGK/img.jpg)

<옵션>

설정을 위해서 [옵션] 버튼을 클릭합니다.

![자동화 설정](https://blog.kakaocdn.net/dn/c15l0h/btsu7V2qWbT/hkhEwSJ6JSYtNC2kMCrb9k/img.jpg)

<자동화 설정>

위 설정을 해주면 이제 끝입니다.

① 자동으로 commit과 push를 해주는 설정입니다. ON으로 바꿉시다.

②.③ commit과 push 주기입니다. 동일한 시간으로 맞추시면 됩니다. 5로 맞추면 5분마다 변경된 파일이 있으면 깃헙 저장소에 전송을 한다고 생각하시면 됩니다.

④ pull 주기입니다. 저는 1로 설정하였습니다. 1분마다 깃헙 저장소에서 내용들을 끌고 옵니다.

그 외에도 아래로 스크롤을 내리면 Commit message 및 Commit Author 설정이 있는데요.

필요한 경우 해주시면 됩니다.

![동기화 완료](https://blog.kakaocdn.net/dn/9X2ji/btsu8lUuCU2/bwEdWUzpi9Zlp0WBpLnMh1/img.jpg)

<동기화 완료>

참고 >> (https://cross-the-line.tistory.com/16 -> 깃허브 연결끊기)


# [[다른 PC환경일때 git 원격 세팅 방법]]
