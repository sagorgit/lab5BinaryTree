# test_gen_bin_tree.py
import unittest
from collections import deque

# Импорт из того же каталога, где лежит gen_bin_tree.py
from gen_bin_tree import (
    gen_bin_tree,
    gen_bin_tree_nested,
    build_as_defaultdict,
    variant_params,
)


class TestGenBinTreeBeginner(unittest.TestCase):
    """Простые тесты для базовой проверки функциональности и соответствия заданию."""

    def test_variant_14_params(self):
        """Проверяем, что вариант №14 возвращает ожидаемые root/height и формулы ветвей."""
        root, height, left_fun, right_fun = variant_params(14)
        self.assertEqual(root, 14)
        self.assertEqual(height, 4)
        self.assertEqual(left_fun(14), 3 - 14)   # 3 - root
        self.assertEqual(right_fun(14), 14 * 2)  # root * 2

    def test_flat_tree_has_root_and_children_on_internal_levels(self):
        """Строим плоское дерево по варианту №14 и проверяем наличие детей на внутренних уровнях."""
        root, height, left_fun, right_fun = variant_params(14)
        tree = gen_bin_tree(
            height=height,
            root=root,
            left_branch=left_fun,
            right_branch=right_fun,
        )

        # Корень должен присутствовать в словаре
        self.assertIn(root, tree)

        # Обойдём уровни до height-1. Для внутренних узлов ожидаем ключи 'left' и 'right'.
        q = deque([(root, 1)])
        while q:
            value, level = q.popleft()
            self.assertIn(value, tree)
            if level < height:
                node = tree[value]
                # ВАЖНО: обычный assert, чтобы типовый анализатор понял, что ключи существуют
                assert "left" in node and "right" in node
                left = node["left"]
                right = node["right"]
                q.append((left, level + 1))
                q.append((right, level + 1))

    def test_nested_representation_basic(self):
        """Проверяем вложенное представление: правильный корень и наличие первого уровня детей."""
        root, height, left_fun, right_fun = variant_params(14)
        nested = gen_bin_tree_nested(
            height=height,
            root=root,
            left_branch=left_fun,
            right_branch=right_fun,
        )

        # В корне должно быть значение root
        self.assertEqual(nested.get("value"), root)
        # На первом уровне ожидаем 'left' и 'right' и у них ключ 'value'
        self.assertIn("left", nested)
        self.assertIn("right", nested)
        self.assertIn("value", nested["left"])
        self.assertIn("value", nested["right"])

    def test_defaultdict_container_basic(self):
        """Проверяем альтернативное хранение в defaultdict(list):
        у корня минимум два потомка, и первые два — это левые/правые дети корня."""
        root, height, left_fun, right_fun = variant_params(14)
        dd = build_as_defaultdict(
        height=height,
        root=root,
        left_branch=left_fun,
        right_branch=right_fun,
        )

        self.assertIn(root, dd)

        # Ожидаемые дети корня по формулам варианта
        expected_left = left_fun(root)
        expected_right = right_fun(root)

        # Из-за совпадений значений на более глубоких уровнях список может удлиняться.
        # Но первые два элемента — это дети корня от первичного расширения.
        self.assertGreaterEqual(len(dd[root]), 2)
        self.assertEqual(dd[root][0], expected_left)
        self.assertEqual(dd[root][1], expected_right)

        # Дополнительно можно проверить, что оба ожидаемых значения встречаются в списке.
        self.assertIn(expected_left, dd[root])
        self.assertIn(expected_right, dd[root])


if __name__ == "__main__":
    unittest.main()
