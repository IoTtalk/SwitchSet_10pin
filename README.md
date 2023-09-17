# SwitchSet_10pin

Device model: 'SwitchSet10'

Output device features: 'Switch-O1' ~ 'Switch-O10'

在Arduino端要先燒入 SwitchSet_10pin_.ino 程式。

然後ssh登入到AR9331上面的OpenWRT上，依序執行下列指令進行DA安裝：

    wget http://yun.iottalk.tw/yunDAinstall.sh
    chmod 700 yunDAinstall.sh
    ./yunDAinstall.sh

執行 yunDAinstall.sh 會需要運作一段時間，尤其執行到pip安裝時，會等很久，要有耐心等候，不要將之中斷。 安裝完畢後自動進入編輯config.py的畫面(vi config.py)，
在這邊填入需要的對應資訊後，按下 ESC 輸入 :wq 存檔退出即可。
