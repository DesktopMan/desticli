# About

Desticli is a command line interface for Destiny. It's main focus is to help you manage item stacks and collections easily. The script can be configured to run without user interaction. Only PSN authentication is supported at the moment. Xbox Live might come later.

## Installation

Desticli is written in Python and only depends on a recent version the _requests_ library. Install it with _pip_ and you should be good to go.

## Configuration

Copy _config.example_ to _config.py_ and fill in the the fields. If you supply your PSN username and password in the config file the script will run without user interaction. Only API key and display name is required. Get the API key at:

https://www.bungie.net/en/user/api

## Usage

Run _python desticli.py -h_ to get usage options.

### *normalize* - Item normalization

Evenly distributes the given items across all your characters. The vault will not be normalized but it must have one free general slot.

```
python desticli.py normalize all
python desticli.py normalize weapon_parts armor_materials
```

#### Supported groups

See *Item groups*

### *move* - Move items to a character or the vault

Move items stored on characters to a specific character or the vault. Characters are numbered from 1 in the order they were created.

```
python desticli.py move vault all
python desticli.py move 1 weapon_parts armor_materials
python desticli.py move 3 strange_coins
```

#### Supported groups

See *Item groups*

### *missing* - Show missing collection items that are for sale

Checks your collections and compares it to the current vendor items for sale. Vendors checked are: Vanguard Quartermaster, Crucible Quartermaster, Outfitter, Shipwright and Xur.

The items are printed in the order they are sold so should be easy to find.

```
python desticli.py missing all
python desticli.py missing emblems shaders
```

#### Supported collections

* emblems
* shaders
* ships
* vehicles
* exotics

## Item groups

Items are organized into groups. The following groups are supported by *normalize* and *move*:

* materials - Ascendant Shard, Ascendant Energy, Radiant Shard, Radiant Energy, Hadium Flake
* resources - Spinmetal, Helium Filaments, Relic Iron, Spirit Bloom, Wormspore
* synths
* telemetries
* glimmer_boosters
* glimmer_consumables
* weapon_parts
* armor_materials
* strange_coins
* motes_of_light
* exotic_shards
* moldering_shards
* passage_coins

You can supply multiple groups if you want to. The alias _all_ will select all groups.
