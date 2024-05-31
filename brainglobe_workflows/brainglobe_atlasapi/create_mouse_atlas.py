from brainglobe_atlasapi import BrainGlobeAtlas


def create_mouse_atlas():
    atlas = BrainGlobeAtlas("allen_mouse_100um")
    print(atlas.atlas_name)


if __name__ == "__main__":
    create_mouse_atlas()
