# BraviaGlass 1.3.1 — сборка APK с Android-телефона

Исходники и ключ подписи специально разделены: ZIP с исходниками разрешено загрузить в публичный репозиторий, но ключ **никогда не загружайте как обычный файл или коммит**. Ключ хранится только в GitHub Actions Secrets.

## Настройка с Xiaomi 17 Ultra

1. Скачайте из чата файл `BraviaGlass-public-source.zip` (безопасный ZIP с кодом и ресурсами; около 8,6 МБ) и `BraviaGlass-GitHub-Secrets-PRIVATE.txt` (секретный; не публиковать).
2. На телефоне откройте [Repository Actions Secrets](https://github.com/Usmanhalu/tvlauncher/settings/secrets/actions). Создайте два **Repository secrets**:
   - `BRAVIA_KEYSTORE_BASE64` — длинное значение после `BRAVIA_KEYSTORE_BASE64=` в приватном TXT.
   - `BRAVIA_SIGNING_PASSWORD` — значение после `BRAVIA_SIGNING_PASSWORD=`.
   Скопируйте только содержимое после `=`, без имени переменной, пробелов и кавычек. Секреты не отправляйте в сообщения.
3. Откройте [корень репозитория](https://github.com/Usmanhalu/tvlauncher), выберите **Add file → Upload files**, выберите **только `BraviaGlass-public-source.zip`**, нажмите **Commit changes** на ветке `main`. Не путайте его с приватным файлом и полным архивом, где есть ключ!
4. Загрузка ZIP автоматически запускает workflow [BraviaGlass — signed APK](https://github.com/Usmanhalu/tvlauncher/actions/workflows/braviaglass-apk.yml). Откройте последний запуск, дождитесь зелёной галочки и скачайте артефакт `BraviaGlass-1.3.1-APK`.
5. Распакуйте артефакт на Xiaomi: внутри `BraviaGlass-1.3.1.apk` и SHA-256. Передайте APK на Sony TV. Устанавливайте поверх предыдущей версии, **не удаляйте** приложение и не очищайте данные.

## Публикация в кнопке «Обновить» на Sony

После успешной проверки APK на Sony:
1. Перейдите в [Actions → BraviaGlass — signed APK](https://github.com/Usmanhalu/tvlauncher/actions/workflows/braviaglass-apk.yml).
2. Нажмите **Run workflow**. Выберите **Publish signed v1.3.1 APK = true**. Запустите работу.
3. Подписанный APK будет создан заново и опубликован в GitHub Releases как `v1.3.1`, после чего BraviaGlass 1.3.0 (и ниже) сможет обнаружить его в `Настройки → О приложении → Обновить BraviaGlass`. Для уже установленной версии 1.3.1 нужно будет выпустить версию новее.

## Безопасность и сохранность настроек

- Исходный ZIP для публичной загрузки не содержит ключ `.jks` и пароли.
- GitHub Action проверяет SHA-256 отпечаток сертификата, совпадающий с `BraviaGlass-1.3.0.apk`.
- Сборка останавливается, если секреты не созданы или подпись другая.
- `applicationId` остаётся `com.usman.braviaglass`, `versionCode` повышен с 11 до 12.
- Установка должна выполняться как обновление, с системным подтверждением Sony. Только при совпадении пакета и цифровой подписи Android сохраняет данные без удаления.
- Полный исходный архив `BraviaGlass-Source-1.3.1.zip` содержит ключ и **не должен загружаться в публичный репозиторий**.
- Готовый APK ещё не собран и на телевизоре не испытан; успешный запуск GitHub Actions необходим.

