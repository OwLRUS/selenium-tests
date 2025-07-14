Создание P12

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650 -nodes -subj "/CN=MyPDFSigner"
--------------------------

openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem -days 36500 -nodes \
  -subj "/CN=MyPDFSigner"
openssl pkcs12 -export -out keystore.p12 \
  -inkey key.pem -in cert.pem \
  -name "MyPDFSigner" \
  -passout pass:supersecretpass



Подпись существующего пдф:
python3 sign_pdf.py input.pdf signed.pdf


1. Сгенерировать тестовый PDF (input.pdf):
python main.py --generate

2. Подписать PDF (input.pdf → signed.pdf):
python main.py --sign

3. Проверить, что PDF подписан именно вашим сертификатом:
python main.py --validate путь_к_файлу.pdf



Зависимости:
pip install -r requirements.txt