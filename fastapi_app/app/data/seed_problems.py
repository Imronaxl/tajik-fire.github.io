from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Language,
    LearningModule,
    LearningProblem,
    News,
    Problem,
    ProblemTranslation,
    TestCase,
    User,
)


DEMO_USER_USERNAME = "demo"
DEMO_USER_PASSWORD_HASH = "$2b$12$SqhRvnJeuePARMzX3weNneh7oMzo00UR/KuWsQdYDydG0ZW5X3.oC"


async def seed_demo_data(db: AsyncSession) -> int:
    result = await db.execute(select(User).where(User.username == DEMO_USER_USERNAME))
    demo_user = result.scalar_one_or_none()
    if demo_user is None:
        demo_user = User(
            username=DEMO_USER_USERNAME,
            email="demo@devstudio.io",
            hashed_password=DEMO_USER_PASSWORD_HASH,
            first_name="Demo",
            last_name="User",
            is_verified=True,
            is_active=True,
            rating=1250,
            solved_count=3,
        )
        db.add(demo_user)
        await db.flush()
    else:
        return 0

    author = User(
        username="problem_author",
        email="author@devstudio.io",
        hashed_password=DEMO_USER_PASSWORD_HASH,
        is_verified=True,
        is_active=True,
    )
    db.add(author)
    await db.flush()

    await _seed_problems(db, author)
    await _seed_learning_modules(db)
    await _seed_news(db, demo_user)

    await db.commit()
    return 1


async def _seed_problems(db: AsyncSession, author: User) -> None:
    problems_data = [
        {
            "title": "A + B",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.RU,
                    "title": "A + B",
                    "statement": "Даны два целых числа A и B. Требуется вычислить их сумму.\n\n### Входные данные\n\nВ единственной строке записаны два целых числа A и B (0 ≤ A, B ≤ 100).\n\n### Выходные данные\n\nВыведите одно целое число — сумму A и B.",
                    "input_format": "Два целых числа A и B",
                    "output_format": "Одно целое число — сумма",
                    "notes": "Пример:\n\nВход: `2 3`\nВыход: `5`",
                },
                {
                    "language": Language.EN,
                    "title": "A + B",
                    "statement": "Given two integers A and B, calculate their sum.\n\n### Input\n\nA single line contains two integers A and B (0 ≤ A, B ≤ 100).\n\n### Output\n\nPrint one integer — the sum of A and B.",
                    "input_format": "Two integers A and B",
                    "output_format": "One integer — the sum",
                    "notes": "Example:\n\nInput: `2 3`\nOutput: `5`",
                },
                {
                    "language": Language.TJ,
                    "title": "A + B",
                    "statement": "Ду адади бутуншудаи A ва B дода шудааст. Йиғинии онҳоро ёбед.\n\n### Додаҳо\n\nДар сатри ягона ду адади бутуншудаи A ва B (0 ≤ A, B ≤ 100) навишта шудаанд.\n\n### Баромад\n\nЯк адади бутуншударо чоп кунед — йиғинии A ва B.",
                    "input_format": "Ду адади бутуншудаи A ва B",
                    "output_format": "Як адади бутуншуда — йиғинӣ",
                    "notes": "Мисол:\n\nВоридот: `2 3`\nХурӯҷ: `5`",
                },
            ],
            "test_cases": [
                (1, "2 3\n", "5\n", True),
                (2, "0 0\n", "0\n", True),
                (3, "100 100\n", "200\n", False),
                (4, "50 75\n", "125\n", False),
            ],
        },
        {
            "title": "Maximum of Two Numbers",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.RU,
                    "title": "Максимум из двух чисел",
                    "statement": "Даны два целых числа. Найдите наибольшее из них.\n\n### Входные данные\n\nДва целых числа (по модулю не превышающие 1000).\n\n### Выходные данные\n\nОдно число — максимум.",
                    "input_format": "Два целых числа",
                    "output_format": "Одно целое число",
                },
                {
                    "language": Language.EN,
                    "title": "Maximum of Two Numbers",
                    "statement": "Given two integers, find the maximum of the two.\n\n### Input\n\nTwo integers (|value| ≤ 1000).\n\n### Output\n\nOne integer — the maximum.",
                    "input_format": "Two integers",
                    "output_format": "One integer",
                },
                {
                    "language": Language.TJ,
                    "title": "Калонтарин аз ду адад",
                    "statement": "Ду адади бутуншуда дода шудааст. Калонтаринашонро ёбед.\n\n### Додаҳо\n\nДу адади бутуншуда (қимати мутлақ ≤ 1000).\n\n### Баромад\n\nЯк адади бутуншуда — калонтарин.",
                    "input_format": "Ду адади бутуншуда",
                    "output_format": "Як адади бутуншуда",
                },
            ],
            "test_cases": [
                (1, "5 10\n", "10\n", True),
                (2, "-5 -10\n", "-5\n", True),
                (3, "100 100\n", "100\n", False),
            ],
        },
        {
            "title": "Factorial",
            "difficulty": "easy",
            "time_limit": 2.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.RU,
                    "title": "Факториал",
                    "statement": "Дано неотрицательное целое число N. Вычислите N!\n\nN! = 1 × 2 × 3 × ... × N\n\n### Входные данные\n\nОдно целое число N (0 ≤ N ≤ 20).\n\n### Выходные данные\n\nОдно целое число — N!.",
                    "input_format": "Одно целое число N",
                    "output_format": "Одно целое число — N!",
                    "notes": "0! = 1 по определению",
                },
                {
                    "language": Language.EN,
                    "title": "Factorial",
                    "statement": "Given a non-negative integer N, calculate N!\n\nN! = 1 × 2 × 3 × ... × N\n\n### Input\n\nOne integer N (0 ≤ N ≤ 20).\n\n### Output\n\nOne integer — N!.",
                    "input_format": "One integer N",
                    "output_format": "One integer — N!",
                    "notes": "0! = 1 by definition",
                },
                {
                    "language": Language.TJ,
                    "title": "Факториал",
                    "statement": "Адади бутуншудаи ғайриманфии N дода шудааст. N!-ро ҳисоб кунед.\n\nN! = 1 × 2 × 3 × ... × N\n\n### Додаҳо\n\nЯк адади бутуншудаи N (0 ≤ N ≤ 20).\n\n### Баромад\n\nЯк адади бутуншуда — N!.",
                    "input_format": "Як адади бутуншудаи N",
                    "output_format": "Як адади бутуншуда — N!",
                    "notes": "0! = 1 аз рӯи таъриф",
                },
            ],
            "test_cases": [
                (1, "0\n", "1\n", True),
                (2, "1\n", "1\n", True),
                (3, "5\n", "120\n", False),
                (4, "10\n", "3628800\n", False),
            ],
        },
        {
            "title": "Sum of Digits",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "implementation",
            "translations": [
                {
                    "language": Language.RU,
                    "title": "Сумма цифр числа",
                    "statement": "Дано натуральное число N. Найдите сумму его цифр.\n\n### Входные данные\n\nОдно натуральное число N (1 ≤ N ≤ 10^9).\n\n### Выходные данные\n\nОдно целое число — сумма цифр числа N.",
                    "input_format": "Одно натуральное число N",
                    "output_format": "Одно целое число",
                },
                {
                    "language": Language.EN,
                    "title": "Sum of Digits",
                    "statement": "Given a natural number N, find the sum of its digits.\n\n### Input\n\nOne natural number N (1 ≤ N ≤ 10^9).\n\n### Output\n\nOne integer — the sum of digits of N.",
                    "input_format": "One natural number N",
                    "output_format": "One integer",
                },
                {
                    "language": Language.TJ,
                    "title": "Йиғинии рақамҳо",
                    "statement": "Адади табиии N дода шудааст. Йиғинии рақамҳои онро ёбед.\n\n### Додаҳо\n\nЯк адади табиии N (1 ≤ N ≤ 10^9).\n\n### Баромад\n\nЯк адади бутуншуда — йиғинии рақамҳои N.",
                    "input_format": "Як адади табиии N",
                    "output_format": "Як адади бутуншуда",
                },
            ],
            "test_cases": [
                (1, "123\n", "6\n", True),
                (2, "100\n", "1\n", True),
                (3, "9999\n", "36\n", False),
                (4, "1000000000\n", "1\n", False),
            ],
        },
        {
            "title": "Prime Number",
            "difficulty": "medium",
            "time_limit": 2.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.RU,
                    "title": "Простое число",
                    "statement": "Дано натуральное число N. Определите, является ли оно простым.\n\nПростое число — это натуральное число больше 1, которое делится только на 1 и на само себя.\n\n### Входные данные\n\nОдно натуральное число N (1 ≤ N ≤ 10^6).\n\n### Выходные данные\n\nВыведите `YES`, если число простое, и `NO` в противном случае.",
                    "input_format": "Одно натуральное число N",
                    "output_format": "YES или NO",
                    "notes": "1 не является простым числом",
                },
                {
                    "language": Language.EN,
                    "title": "Prime Number",
                    "statement": "Given a natural number N, determine if it is prime.\n\nA prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.\n\n### Input\n\nOne natural number N (1 ≤ N ≤ 10^6).\n\n### Output\n\nPrint `YES` if the number is prime, and `NO` otherwise.",
                    "input_format": "One natural number N",
                    "output_format": "YES or NO",
                    "notes": "1 is not a prime number",
                },
                {
                    "language": Language.TJ,
                    "title": "Адади сода",
                    "statement": "Адади табиии N дода шудааст. Муайян кунед, ки оё он сода аст.\n\n### Додаҳо\n\nЯк адади табиии N (1 ≤ N ≤ 10^6).\n\n### Баромад\n\nАгар адад сода бошад `YES` ва дар акси ҳол `NO` чоп кунед.",
                    "input_format": "Як адади табиии N",
                    "output_format": "YES ё NO",
                    "notes": "1 адади сода нест",
                },
            ],
            "test_cases": [
                (1, "2\n", "YES\n", True),
                (2, "17\n", "YES\n", True),
                (3, "1\n", "NO\n", False),
                (4, "4\n", "NO\n", False),
                (5, "997\n", "YES\n", False),
            ],
        },
        {
            "title": "Palindrome Check",
            "difficulty": "medium",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "strings",
            "translations": [
                {
                    "language": Language.RU,
                    "title": "Проверка палиндрома",
                    "statement": "Дана строка S, состоящая из строчных латинских букв. Определите, является ли она палиндромом.\n\n### Входные данные\n\nОдна строка S (1 ≤ |S| ≤ 1000).\n\n### Выходные данные\n\nВыведите `YES` или `NO`.",
                    "input_format": "Строка S",
                    "output_format": "YES или NO",
                },
                {
                    "language": Language.EN,
                    "title": "Palindrome Check",
                    "statement": "Given a string S consisting of lowercase Latin letters, determine if it is a palindrome.\n\n### Input\n\nOne string S (1 ≤ |S| ≤ 1000).\n\n### Output\n\nPrint `YES` or `NO`.",
                    "input_format": "String S",
                    "output_format": "YES or NO",
                },
                {
                    "language": Language.TJ,
                    "title": "Санҷиши палиндром",
                    "statement": "Сатри S, ки аз ҳарфҳои хурди лотинӣ иборат аст, дода шудааст. Муайян кунед, ки оё он палиндром аст.\n\n### Додаҳо\n\nЯк сатри S (1 ≤ |S| ≤ 1000).\n\n### Баромад\n\n`YES` ё `NO` чоп кунед.",
                    "input_format": "Сатри S",
                    "output_format": "YES ё NO",
                },
            ],
            "test_cases": [
                (1, "aba\n", "YES\n", True),
                (2, "abba\n", "YES\n", True),
                (3, "abc\n", "NO\n", False),
                (4, "racecar\n", "YES\n", False),
                (5, "hello\n", "NO\n", False),
            ],
        },
    ]

    for data in problems_data:
        problem = Problem(
            title=data["title"],
            difficulty=data["difficulty"],
            time_limit=data["time_limit"],
            memory_limit=data["memory_limit"],
            is_published=True,
            author_id=author.id,
            category=data["category"],
        )
        db.add(problem)
        await db.flush()

        for trans in data["translations"]:
            db.add(
                ProblemTranslation(
                    problem_id=problem.id,
                    language=trans["language"],
                    title=trans["title"],
                    statement=trans["statement"],
                    input_format=trans.get("input_format"),
                    output_format=trans.get("output_format"),
                    notes=trans.get("notes"),
                )
            )

        for order, input_data, expected, is_sample in data["test_cases"]:
            db.add(
                TestCase(
                    problem_id=problem.id,
                    test_order=order,
                    input_data=input_data,
                    expected_output=expected,
                    is_sample=is_sample,
                )
            )


async def _seed_learning_modules(db: AsyncSession) -> None:
    modules_data = [
        {
            "title": "Introduction to Algorithms",
            "slug": "intro-to-algorithms",
            "description": "Core algorithmic thinking: complexity, big-O notation, problem decomposition.",
            "theory_content": "## Why algorithms?\n\nAn algorithm is a finite sequence of well-defined steps that solves a problem. As an engineer you will be measured not only on whether your code works, but on whether it scales.\n\n### Complexity\n\n- **Time complexity** — how runtime grows with input size, expressed in big-O notation.\n- **Space complexity** — how much memory your solution uses.\n\nA solution that runs in O(n) is generally preferable to one that runs in O(n²) for large inputs.\n\n### Practical tips\n\n1. Read the problem twice. Define inputs and outputs in your own words.\n2. Try a brute-force solution first. It validates your understanding.\n3. Identify the bottleneck — what would make brute-force too slow?\n4. Pick a data structure that eliminates the bottleneck.",
            "order": 1,
        },
        {
            "title": "Working with Numbers",
            "slug": "working-with-numbers",
            "description": "Integer arithmetic, modular arithmetic, primes and basic number theory for competitive programming.",
            "theory_content": "## Integer arithmetic\n\nMost competitive programming problems involve integers. Be careful with overflow — Python handles big integers automatically, but in C++ use `long long` when values may exceed 2^31.\n\n### Modular arithmetic\n\nWhen the result is too large, problems usually ask for it modulo a fixed number (often 10^9 + 7).\n\n### Primes\n\nA prime is a number >1 with no divisors besides 1 and itself. Trial division up to √n is sufficient for n ≤ 10^12.",
            "order": 2,
        },
        {
            "title": "Strings Fundamentals",
            "slug": "strings-fundamentals",
            "description": "String traversal, palindromes, basic pattern matching and complexity traps.",
            "theory_content": "## Strings\n\nA string is a sequence of characters. Most basic operations — traversal, reversal, comparison — are linear in the string length.\n\n### Palindromes\n\nA string is a palindrome if it reads the same forwards and backwards. The simplest check is to compare the string with its reverse.\n\n### Common pitfalls\n\n- In C++, use `std::string::substr` carefully — copying substrings in a loop can become O(n²).\n- In Python, slicing `s[::-1]` is the idiomatic way to reverse a string.",
            "order": 3,
        },
    ]

    problem_titles_for_module = {
        "intro-to-algorithms": ["A + B", "Maximum of Two Numbers"],
        "working-with-numbers": ["Factorial", "Prime Number"],
        "strings-fundamentals": ["Palindrome Check", "Sum of Digits"],
    }

    for module_data in modules_data:
        module = LearningModule(
            title=module_data["title"],
            slug=module_data["slug"],
            description=module_data["description"],
            theory_content=module_data["theory_content"],
            order=module_data["order"],
            is_published=True,
        )
        db.add(module)
        await db.flush()

        titles = problem_titles_for_module.get(module_data["slug"], [])
        for idx, title in enumerate(titles, start=1):
            problem_result = await db.execute(select(Problem).where(Problem.title == title))
            problem = problem_result.scalar_one_or_none()
            if problem is not None:
                db.add(
                    LearningProblem(
                        module_id=module.id,
                        problem_id=problem.id,
                        order=idx,
                    )
                )


async def _seed_news(db: AsyncSession, author: User) -> None:
    now = datetime.now(timezone.utc)
    items = [
        {
            "title": "DevStudio Pro 1.0 is here",
            "content": "After months of iteration we are shipping the first stable release of DevStudio Pro.\n\nThe platform now ships with a sandboxed code judger, a problem archive with three difficulty tiers, structured learning tracks and a social layer for friends and direct messages.\n\nGrab the `demo / Demo1234!` account already loaded with sample submissions to explore everything without setting up SMTP.",
            "published_at": now - timedelta(days=2),
        },
        {
            "title": "New: Submission feed and rating system",
            "content": "Every submission now flows into a public activity feed visible on the dashboard. Accepted solutions grant rating points scaled by difficulty — easy +5, medium +12, hard +25.\n\nClimb the leaderboard by solving harder problems consistently.",
            "published_at": now - timedelta(days=1),
        },
        {
            "title": "Tips: writing your first submission",
            "content": "Pick `A + B` from the problem archive. Choose Python 3 — it is the friendliest language for getting started.\n\nRead the input with `input().split()`, convert to integers, print the sum. Hit Submit and watch the verdict arrive on the submissions page.\n\nIf you get WA, double-check the output format — extra whitespace is fine, extra text is not.",
            "published_at": now - timedelta(hours=6),
        },
    ]

    for item in items:
        db.add(
            News(
                title=item["title"],
                content=item["content"],
                author_id=author.id,
                is_published=True,
                published_at=item["published_at"],
            )
        )
