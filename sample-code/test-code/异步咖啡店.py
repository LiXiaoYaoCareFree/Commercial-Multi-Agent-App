import asyncio
import time


async def make_coffee_async(customer: str) -> None:
    print(f"开始为 {customer} 煮咖啡...")
    await asyncio.sleep(5)
    print(f"{customer} 的咖啡好了")
    return f"{customer}的咖啡"


async def main_async():
    start_time = time.time()

    # 创建任务清单
    tasks = [
        make_coffee_async("顾客A"),
        make_coffee_async("顾客B"),
        make_coffee_async("顾客C"),
        make_coffee_async("顾客D"),
        make_coffee_async("顾客E"),
        make_coffee_async("顾客F"),
    ]

    results = await asyncio.gather(*tasks)
    print("所有咖啡都准备好了:", results)

    end_time = time.time()
    print(f"异步方式总耗时: {end_time - start_time:.2f}秒")


if __name__ == "__main__":
    asyncio.run(main_async())
