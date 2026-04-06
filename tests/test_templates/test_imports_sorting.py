"""Проверка, что импорты в сгенерированных файлах отсортированы одинаково."""

from types import SimpleNamespace


def _build_fake_model(*, relative_imports, lazy_imports):
    return SimpleNamespace(
        relative_imports=relative_imports,
        lazy_imports=lazy_imports,
        additional_properties=None,
        is_multipart_body=False,
        class_info=SimpleNamespace(name="MyClass", module_name="my_module"),
        title=None,
        description=None,
        example=None,
        required_properties=[],
        optional_properties=[],
    )


def _ordered_indices(output: str, items):
    """Return the index of the first occurrence of each item in ``output``."""
    return [output.index(item) for item in items]


def test_model_template_renders_relative_imports_sorted(env):
    relative_imports = [
        "from ..models.charlie import Charlie",
        "from ..models.alpha import Alpha",
        "from ..models.bravo import Bravo",
    ]
    fake_model = _build_fake_model(relative_imports=relative_imports, lazy_imports=[])

    output = env.get_template("model.py.jinja").render(model=fake_model)

    sorted_imports = sorted(relative_imports)
    indices = _ordered_indices(output, sorted_imports)
    assert indices == sorted(indices), (
        "relative_imports must be rendered in sorted order, got order: "
        f"{[imp for _, imp in sorted(zip(indices, sorted_imports))]}"
    )


def test_model_template_renders_lazy_imports_sorted(env):
    lazy_imports = [
        "from ..models.echo import Echo",
        "from ..models.delta import Delta",
        "from ..models.foxtrot import Foxtrot",
    ]
    fake_model = _build_fake_model(relative_imports=[], lazy_imports=lazy_imports)

    output = env.get_template("model.py.jinja").render(model=fake_model)

    sorted_imports = sorted(lazy_imports)
    # lazy_imports appear at the top of the file *and* inside to_dict / from_dict.
    # We only assert ordering on the first occurrence of each import.
    indices = _ordered_indices(output, sorted_imports)
    assert indices == sorted(indices), (
        "lazy_imports must be rendered in sorted order, got order: "
        f"{[imp for _, imp in sorted(zip(indices, sorted_imports))]}"
    )


def test_model_template_render_is_deterministic_across_input_order(env):
    """Rendering with the same imports in different input order produces the
    same file - the bug being fixed."""
    imports_a = [
        "from ..models.alpha import Alpha",
        "from ..models.beta import Beta",
        "from ..models.gamma import Gamma",
    ]
    imports_b = list(reversed(imports_a))

    out_a = env.get_template("model.py.jinja").render(
        model=_build_fake_model(relative_imports=imports_a, lazy_imports=[])
    )
    out_b = env.get_template("model.py.jinja").render(
        model=_build_fake_model(relative_imports=imports_b, lazy_imports=[])
    )

    assert out_a == out_b, "model.py.jinja output depends on import iteration order"
