:::writing{variant="document" id="73104"}
設定画面で通知をオフにして保存しても、再表示するとオンに戻っていた。保存済みのfalseを未設定として扱う既定値処理が原因だった。

通知設定の既定値を適用する条件を、値がundefinedの場合だけに変更した。保存済みのfalseとtrueは保持し、undefinedは従来どおりtrueになる。保存済みデータの書き換えは不要。

false、true、undefinedの単体テスト3件が通過した。実機でのプッシュ通知配信は未確認。
:::
