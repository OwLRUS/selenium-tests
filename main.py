#!/usr/bin/env python3
import os
import sys
import argparse
from reportlab.pdfgen import canvas
from pyhanko.sign.signers import SimpleSigner, PdfSignatureMetadata, PdfSigner
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.general import load_cert_from_pemder

BASE = os.path.dirname(__file__)
INPUT_PDF = os.path.join(BASE, "certificate_filled.pdf")
OUTPUT_PDF = os.path.join(BASE, "signed.pdf")
KEY_PATH = os.path.join(BASE, "private_key.pem")
CERT_PATH = os.path.join(BASE, "self_cert.pem")


def generate_test_pdf(path: str):
    print("[*] Генерируем тестовый PDF...")
    c = canvas.Canvas(path)
    c.drawString(100, 750, "Тестовый PDF для подписи")
    c.save()
    print(f"✅ Готово! Откройте {path}")


def ensure_keys():
    for path in (KEY_PATH, CERT_PATH):
        if not os.path.exists(path):
            sys.exit(f"ERROR: не найден файл {path!r}")


def sign_pdf(input_path=INPUT_PDF, output_path=OUTPUT_PDF, key_path=KEY_PATH, cert_path=CERT_PATH):
    ensure_keys()
    signer = SimpleSigner.load(key_file=key_path, cert_file=cert_path, key_passphrase=None)
    new_field = SigFieldSpec(sig_field_name="Signature1", on_page=0, box=(50, 600, 300, 700))
    meta = PdfSignatureMetadata(field_name="Signature1", reason="Подтверждаю владельца сертификата", location="MyService")
    with open(input_path, "rb") as inf, open(output_path, "wb") as outf:
        w = IncrementalPdfFileWriter(inf)
        append_signature_field(w, new_field)
        pdf_signer = PdfSigner(signature_meta=meta, signer=signer, new_field_spec=new_field)
        pdf_signer.sign_pdf(w, output=outf)
    #print(f"✅ PDF подписан: {output_path}")


def validate_signature_with_cert(pdf_path: str, cert_path: str) -> bool:
    import sys
    import os
    from contextlib import contextmanager
    from pyhanko.sign.general import load_cert_from_pemder
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature
    import warnings

    @contextmanager
    def suppress_stderr():
        """Контекстный менеджер для временного подавления stderr."""
        fd = sys.stderr.fileno()
        def _redirect_stderr(to_fd):
            sys.stderr.close()
            os.dup2(to_fd, fd)
            sys.stderr = os.fdopen(fd, 'w')
        with os.fdopen(os.dup(fd), 'w') as old_stderr:
            with open(os.devnull, 'w') as devnull:
                _redirect_stderr(devnull.fileno())
                try:
                    yield
                finally:
                    _redirect_stderr(old_stderr.fileno())

    my_cert = load_cert_from_pemder(cert_path)
    with open(pdf_path, 'rb') as f:
        reader = PdfFileReader(f)
        for sig in reader.embedded_signatures:
            with warnings.catch_warnings(), suppress_stderr():
                warnings.simplefilter("ignore")
                try:
                    status = validate_pdf_signature(sig)
                except Exception as e:
                    if "non repudiation" in str(e):
                        continue
                    else:
                        print(f"Ошибка при проверке подписи: {e}")
                        continue
            signer_cert = getattr(status, 'signing_cert', None)
            if signer_cert and signer_cert.dump() == my_cert.dump():
                return True
    return False


def main():
    parser = argparse.ArgumentParser(description="PDF подпись: генерация, подписание, проверка подписи вашим сертификатом.")
    parser.add_argument('--generate', action='store_true', help='Сгенерировать тестовый input.pdf')
    parser.add_argument('--sign', action='store_true', help='Подписать input.pdf')
    parser.add_argument('--validate', metavar='PDF_PATH', help='Путь к PDF для проверки подписи именно вашим сертификатом')
    args = parser.parse_args()

    if args.generate:
        generate_test_pdf(INPUT_PDF)
        return
    if args.sign:
        if not os.path.exists(INPUT_PDF):
            print("input.pdf не найден, сначала сгенерируйте его через --generate")
            return
        sign_pdf()
        return
    if args.validate:
        ensure_keys()
        if validate_signature_with_cert(args.validate, CERT_PATH):
            print(f"Подпись в {args.validate} сделана ИМЕННО вашим сертификатом!")
        else:
            print(f"Подпись в {args.validate} НЕ вашим сертификатом или не найдена.")
        return
    parser.print_help()

if __name__ == "__main__":
    main()
