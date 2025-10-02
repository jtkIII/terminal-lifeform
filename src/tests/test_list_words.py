from utils.world_loader import list_worlds


def test_list_worlds():
    worlds = list_worlds()
    for world in worlds:
        print(world)
    assert isinstance(worlds, list)
    assert len(worlds) >= 10  # Expecting at least 10 worlds
    for world in worlds:
        assert "name" in world
        assert "description" in world
        assert "icon" in world
        assert "resource_availability" in world
        assert "resource_regeneration_rate" in world
        assert "density_efficiency" in world
        assert "memory_sensitivity" in world
        assert isinstance(world["name"], str)  # pyright: ignore[reportArgumentType]
        assert isinstance(world["description"], str)  # pyright: ignore[reportArgumentType]
        assert isinstance(world["icon"], str)  # pyright: ignore[reportArgumentType]
        assert isinstance(world["resource_availability"], (int, float))  # pyright: ignore[reportArgumentType]
        assert isinstance(world["resource_regeneration_rate"], (int, float))  # pyright: ignore[reportArgumentType]
        assert isinstance(world["density_efficiency"], (int, float))  # pyright: ignore[reportArgumentType]
        assert isinstance(world["memory_sensitivity"], (int, float))  # pyright: ignore[reportArgumentType]
