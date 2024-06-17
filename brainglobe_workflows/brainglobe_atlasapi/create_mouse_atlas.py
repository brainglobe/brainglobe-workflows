from brainglobe_atlasapi import BrainGlobeAtlas


def create_mouse_atlas(atlas_name):
    atlas = BrainGlobeAtlas(atlas_name)
    print(atlas.atlas_name)


if __name__ == "__main__":
    create_mouse_atlas("allen_mouse_100um")
