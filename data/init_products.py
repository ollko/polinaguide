import asyncio
from models import Product
from data.data import Session


async def init_products():
    # Данные из вашего словаря PRODUCTS, адаптированные под модель
    products_to_add = [
        Product(
            products_name='Настоящая Сербия',
            description='Настоящая Сербия: где природа чарует.',
            url="https://drive.google.com/file/d/1cnhBYRJuYmCvBdblAfD9qEfTz7X86Zng/view",
            free=True,
        ),
        Product(
            products_name='Западная Сербия на машине',
            description='Путеводитель "Западная Сербия на машине: по лучшим местам за 3 дня."',
            url="https://drive.google.com/file/d/1RqhHPJ9YxCj2ZZBI7lLO-v4tCVN5GBUQ/view",
            free=False,
            yookassa_total_amount=10000  # в копейках для ЮKassa
        )
    ]
    async with Session() as session:
        session.add_all(products_to_add)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_products())
