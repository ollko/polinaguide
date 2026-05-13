from collections import namedtuple

Product = namedtuple(
    "Product", ["products_name", "yookassa_products_id", "link", "amount"])

PRODUCTS = {
    "free_guide_1": Product(
        'Настоящая Сербия: где природа чарует.',
        "free_guide_1",
        "https://drive.google.com/file/d/1cnhBYRJuYmCvBdblAfD9qEfTz7X86Zng/view",
        0,
    ),
    "guide_1": Product(
        'Путеводитель "Западная Сербия на машине: по лучшим местам за 3 дня."',
        "guide_1",
        "https://drive.google.com/file/d/1RqhHPJ9YxCj2ZZBI7lLO-v4tCVN5GBUQ/view",
        10000,
    ),
    "Западная Сербия на машине": Product(
        'Путеводитель "Западная Сербия на машине: по лучшим местам за 3 дня."',
        "guide_1",
        "https://drive.google.com/file/d/1RqhHPJ9YxCj2ZZBI7lLO-v4tCVN5GBUQ/view",
        0,
    ),
}
