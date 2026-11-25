# 金豆豆日記 V5 發佈版

保留 V5 美術、主題、橫向選樽與交易功能。新訪客從空白賬簿開始；原本同一網域的訪客資料會讀取。示範回收價仍非即時金價。

## Firebase（先完成）
1. https://console.firebase.google.com/ 建立獨立專案，例如 goldbean-diary（ID 需全球唯一），不需 Google Analytics。
2. Project settings > General > Your apps > Web (`</>`) > Register app。無須 Firebase Hosting。
3. 已將你提供的 Firebase Web App config 填入 `firebase-config.js`，專案 goldbean-diary。保留原先整合的 Firebase SDK 11.10.0；不額外啟用 Analytics。只使用公開 Web config，切勿提供服務帳戶私鑰、OAuth secret、管理員 token。
4. Authentication > Get started > Sign-in method > Google > Enable；選擇支援電郵並儲存。Settings > Authorized domains 加入 `你的GitHub帳號.github.io`（無路徑、無 https://）。
5. Firestore Database > Create database > Production mode，選擇合適的地區（可選香港如提供；建立後地區不能隨意變更）。Rules 頁完整貼入 `firestore.rules` 並 Publish。若是已有其他 App 的專案，不可覆蓋其規則；建議建立獨立專案。

## GitHub Pages
1. 建立 public repository `goldbean-diary`（GitHub Free 公開 repo 可用 Pages；只放程式，不能上載私人的記錄或備份）。
2. 解壓 ZIP，將資料夾內檔案和子目錄上載至 main 根目錄，不要直接上載 ZIP。完成 config 先再上載。
3. Settings > Pages > Build and deployment > Deploy from a branch > main > /(root) > Save。
4. 打開 Pages 顯示的 HTTPS URL；Safari / Chrome 可加入主畫面。測試 Google 登入請用完整瀏覽器，避免內嵌瀏覽器阻擋彈窗。

## 同步邏輯
- 訪客維持本機記錄；登入後使用 UID 獨立的 Firestore 文件 `users/{uid}/diary/main`。
- 首次登入且無雲端文件，可選擇複製非示範訪客記錄；已有雲端文件不會自動覆蓋。可匯出／匯入 JSON 手動遷移，匯入會替換目前帳戶資料。
- 編輯後自動嘗試上傳；登入時下載，設定 > 個人 > 同步／檢查更新 可主動拉取其他裝置更新。不是即時多人協作。
- revision 交易檢查避免舊資料靜默覆蓋；衝突時先匯出本機 JSON，確認後才拉取雲端；不會自動合併交易。
- 斷網後已登入頁面的未同步內容保留在 UID 專屬本機暫存，重新連線可重試；重新開啟 App 若無法驗證雲端，回到訪客，不提供離線登入。
- PIN 不上傳也不匯出，僅本機畫面鎖，不是加密；帳戶資料仍可能在該瀏覽器暫存，請勿使用公用裝置。
- 目前單文件快照，程式以 750 KB JSON 為保守上限；大型賬簿需日後改成分文件儲存。頭像縮放至 128x128。

## 上線驗收（必做）
- 帳戶 A 建立交易，第二裝置登入 A 後讀到同一筆。
- 帳戶 B 不可讀取 A 的資料；登出切換回訪客不顯示 A 記錄。
- 測試兩裝置同時寫入的衝突，確定沒有無聲覆蓋。
- 驗證 PIN 不在 Firestore、示範價明確標示、Google 登入、音效和各手機的 PWA。
- 即時金行回收報價及英文完整翻譯尚未接駁。Firebase Web Config 已填入，仍須在 Console 啟用 Authentication、建立 Firestore 並發布規則，以及授權 GitHub Pages 網域；不能把本機測試當成真實雲端驗收。
