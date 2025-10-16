# gen_bin_tree.py
from __future__ import annotations
from typing import Callable, Dict, Deque, Tuple, Optional, TypedDict, NotRequired, Union
from collections import deque

Number = Union[int, float]


class NodeRecord(TypedDict, total=False):
    """Словарь детей узла: ключи могут отсутствовать на последнем уровне."""
    left: NotRequired[Number]
    right: NotRequired[Number]


def variant_params(roll: int) -> tuple[Number, int, Callable[[Number], Number], Callable[[Number], Number]]:
    """Вернуть параметры варианта по номеру студента (1..∞) с циклическим переходом.

    Возвращает кортеж:
        (root, height, left_branch, right_branch)

    Пояснение:
        - Если номер больше числа вариантов, он «закручивается» по кругу.
        - left_branch и right_branch задаются как лямбда-функции,
          чтобы их можно было передавать в генератор дерева.

    Параметры:
        roll: номер студента в списке (целое число начиная с 1).
    """
    variants = [
        (1, 5,  lambda r: r * 2,             lambda r: r + 3),
        (2, 6,  lambda r: r * 3,             lambda r: r + 4),
        (3, 4,  lambda r: r + 2,             lambda r: r * 3),
        (4, 4,  lambda r: r * 4,             lambda r: r + 1),
        (5, 6,  lambda r: r ** 2,            lambda r: r - 2),
        (6, 5,  lambda r: (r * 2) - 2,       lambda r: r + 4),
        (7, 4,  lambda r: r * 3,             lambda r: r - 4),
        (8, 4,  lambda r: r + r / 2,         lambda r: r ** 2),
        (9, 6,  lambda r: r * 2 + 1,         lambda r: 2 * r - 1),
        (10, 5, lambda r: r * 3 + 1,         lambda r: 3 * r - 1),
        (11, 3, lambda r: r ** 2,            lambda r: 2 + r ** 2),
        (12, 4, lambda r: r ** 3,            lambda r: (r * 2) - 1),
        (13, 3, lambda r: r + 1,             lambda r: r - 1),
        (14, 4, lambda r: 3 - r,             lambda r: r * 2),
        (15, 6, lambda r: 2 * (r + 1),       lambda r: 2 * (r - 1)),
        (16, 3, lambda r: r / 2,             lambda r: r * 2),
        (17, 4, lambda r: (r - 4) ** 2,      lambda r: (r + 3) * 2),
        (18, 5, lambda r: (r - 8) * 3,       lambda r: (r + 8) * 2),
    ]
    idx = (roll - 1) % len(variants)
    root, height, lfun, rfun = variants[idx]
    return root, height, lfun, rfun


def gen_bin_tree(
    height: Optional[int] = None,
    root: Optional[Number] = None,
    left_branch: Callable[[Number], Number] = lambda r: r,
    right_branch: Callable[[Number], Number] = lambda r: r,
) -> Dict[Number, NodeRecord]:
    """Сгенерировать бинарное дерево **нерекурсивным** способом и вернуть его как словарь.

    Базовое представление:
        { узел: {"left": левый_потомок, "right": правый_потомок}, ... }

    Алгоритм:
        - Используется обход в ширину (BFS) на очереди `collections.deque`.
        - Расширяем уровни до заданной высоты `height`.
        - Корень (root) находится на уровне 1. Внутренние узлы порождают двух потомков,
          значения которых считаются функциями `left_branch` и `right_branch`.
        - На последнем уровне потомки не создаются.

    Параметры:
        height: высота дерева (количество уровней, должно быть >= 1).
                Если не передано, берётся из варианта студента (по умолчанию вариант №14).
        root: значение в корне. Если не передано, берётся из варианта студента (по умолчанию вариант №14).
        left_branch: функция (лямбда) вычисления левого потомка от значения родителя.
        right_branch: функция (лямбда) вычисления правого потомка от значения родителя.

    Возврат:
        Словарь: ключ — значение узла, значение — словарь с ключами "left"/"right" при наличии потомков.

    Исключения:
        ValueError — если высота меньше 1.

    Примечания:
        - Функция не использует рекурсию; глубина контролируется явной очередью.
        - По требованию задания формулы ветвей параметризуются через аргументы по умолчанию.
    """
    # Если root/height не заданы — используем вариант №14 как дефолт
    if root is None or height is None:
        default_root, default_height, default_left, default_right = variant_params(14)
        root = default_root if root is None else root
        height = default_height if height is None else height
        # Если пользователь не менял функции, оставим дефолтные для варианта 14
        if left_branch.__code__.co_code == (lambda r: r).__code__.co_code and \
           right_branch.__code__.co_code == (lambda r: r).__code__.co_code:
            left_branch = default_left
            right_branch = default_right

    if height < 1:
        raise ValueError("height должно быть >= 1")

    tree: Dict[Number, NodeRecord] = {}
    q: Deque[Tuple[Number, int]] = deque()
    q.append((root, 1))

    while q:
        value, level = q.popleft()
        # Гарантируем, что запись для узла существует в словаре
        tree.setdefault(value, NodeRecord())

        if level < height:
            # Вычисляем значения потомков по параметризованным формулам
            left_val = left_branch(value)
            right_val = right_branch(value)

            # Сохраняем связи в базовом виде
            tree[value]["left"] = left_val
            tree[value]["right"] = right_val

            # Добавляем потомков в очередь для следующего уровня
            q.append((left_val, level + 1))
            q.append((right_val, level + 1))

    return tree

from typing import Any
from collections import defaultdict, namedtuple, deque

def gen_bin_tree_nested(
    height: int,
    root: Number,
    left_branch: Callable[[Number], Number],
    right_branch: Callable[[Number], Number],
) -> dict[str, Any]:
    """Построить **вложенное** представление дерева итеративно (без рекурсии)."""
    flat = gen_bin_tree(height=height, root=root,
                        left_branch=left_branch, right_branch=right_branch)

    nested: dict[str, Any] = {"value": root}
    q: Deque[tuple[Number, dict[str, Any], int]] = deque()
    q.append((root, nested, 1))

    while q:
        value, handle, level = q.popleft()
        if level < height:
            node_rec = flat[value]
            # Сообщаем типовому анализатору, что на внутренних уровнях ключи существуют.
            assert "left" in node_rec and "right" in node_rec, \
                "Ожидались ключи 'left' и 'right' на внутренних уровнях"

            left_val = node_rec["left"]
            right_val = node_rec["right"]
            handle["left"] = {"value": left_val}
            handle["right"] = {"value": right_val}
            q.append((left_val, handle["left"], level + 1))
            q.append((right_val, handle["right"], level + 1))
    return nested


Node = namedtuple("Node", "value left right")

def build_as_defaultdict(
    height: int,
    root: Number,
    left_branch: Callable[[Number], Number],
    right_branch: Callable[[Number], Number],
) -> defaultdict[Number, list]:
    """Сохранить дерево в контейнере defaultdict(list) для демонстрации альтернативы.

    Ключ — значение узла; значение — список из двух потомков для внутренних узлов.
    Для листьев создаётся пустой список.

    Итеративно с использованием очереди (BFS).
    """
    dd: defaultdict[Number, list] = defaultdict(list)
    q: Deque[tuple[Number, int]] = deque([(root, 1)])

    while q:
        v, lvl = q.popleft()
        if lvl < height:
            l, r = left_branch(v), right_branch(v)
            dd[v].extend([l, r])
            q.append((l, lvl + 1))
            q.append((r, lvl + 1))
        else:
            dd.setdefault(v, [])
    return dd


if __name__ == "__main__":
    # ---------------- CLI и (при необходимости) интерактивный ввод ----------------
    # Идея:
    # 1) Если пользователь ничего не передал — спросим номер по списку (roll),
    #    затем используем параметры варианта.
    # 2) Если указаны флаги --roll, --root, --height — применяем их.
    # 3) Формулы ветвей по умолчанию берём из варианта. Пользователь при желании
    #    может заменить root/height флагами, но ветви останутся параметризованными
    #    как в варианте (что соответствует требованиям).
    #
    # Пример запуска:
    #   python gen_bin_tree.py                 # спросит roll интерактивно
    #   python gen_bin_tree.py --roll 14       # возьмёт вариант №14 без вопросов
    #   python gen_bin_tree.py --root 10 --height 3
    #
    import argparse

    parser = argparse.ArgumentParser(
        description="Нерекурсивная генерация бинарного дерева с параметризацией ветвей."
    )
    parser.add_argument("--roll", type=int, help="Номер студента (вариант 1..∞, циклично)")
    parser.add_argument("--root", type=float, help="Значение корня (перекрывает вариант)")
    parser.add_argument("--height", type=int, help="Высота дерева (перекрывает вариант)")
    args = parser.parse_args()

    # Шаг 1: получить базовые параметры варианта
    if args.roll is not None:
        v_root, v_height, v_left, v_right = variant_params(args.roll)
    else:
        # Интерактивно спросим номер, если флагов нет
        try:
            roll_str = input("Введите номер по списку (roll), например 14: ").strip()
            roll_val = int(roll_str)
        except Exception:
            # На случай пустого ввода/ошибки — используем №14 по умолчанию
            roll_val = 14
        v_root, v_height, v_left, v_right = variant_params(roll_val)

    # Шаг 2: применить возможные переопределения root/height
    use_root = v_root if args.root is None else args.root
    use_height = v_height if args.height is None else args.height

    # Шаг 3: сгенерировать дерево — ветви оставляем из варианта (лямбда по умолчанию)
    t = gen_bin_tree(
        height=int(use_height),
        root=use_root,
        left_branch=v_left,
        right_branch=v_right,
    )

    # Печать результата
    print("Базовое представление дерева (словарь узел -> {left, right}):")
    for node, children in t.items():
        print(f"{node} -> {children}")
    # вложенную форму:
    nested = gen_bin_tree_nested(
        height=int(use_height), root=use_root,
        left_branch=v_left, right_branch=v_right
    )
    print("\nВложенное представление:")
    print(nested)

    # И альтернативный контейнер:
    dd = build_as_defaultdict(
        height=int(use_height), root=use_root,
        left_branch=v_left, right_branch=v_right
    )
    print("\ndefaultdict-представление:")
    for k, v in dd.items():
        print(f"{k} -> {v}")    
