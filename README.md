# About

Desticli is a command line interface for Destiny. It's main focus is to help you manage item stacks and collections easily. The script can be configured to run without user interaction. Only PSN authentication is supported at the moment. Xbox Live might come later.

## Installation

Desticli only depends on a recent version the _requests_ library. Install it with _pip_ and you should be good to go.

## Configuration

Copy _config.example_ to _config.py_ and fill in the the fields. Only API key and display name is required. Get the API key at:

https://www.bungie.net/en/user/api

Optional: If you supply your PSN username and password in the config file the script will run without user interaction.

## Usage

Run _./desticli.py -h_ to get usage options.

See item groups below for a list of supported groups.

### *normalize* - Item normalization

Evenly distributes the given items across all your characters. The vault will not be normalized but it must have one free general slot.

```
./desticli.py normalize all
./desticli.py normalize weapon_parts armor_materials
```

#### Supported groups

See *Item groups*

### *move* - Move items to the vault

Moves items to the vault. Character support is planned.

```
./desticli.py move vault all
./desticli.py move vault weapon_parts armor_materials
```

#### Supported groups

See *Item groups*

### *missing* - Show missing collection items that are for sale

Checks your collections and compares it to the current vendor items for sale. Only the Outfitter and the Shipwright are supported at the moment.

The items are printed in the order they are sold so should be easy to find.

```
./desticli.py missing all
./desticli.py missing emblems shaders
```

#### Supported collections

* emblems
* shaders
* ships
* vehicles

## Item groups

Items are organized into groups. The following groups are supported by *normalize* and *move*:

* materials - Ascendant Shard, Ascendant Energy, Radiant Shard, Radiant Energy
* resources - Spinmetal, Helium Filaments, Relic Iron, Spirit Bloom
* synths
* telemetries
* glimmer_boosters
* weapon_parts
* armor_materials
* strange_coins
* motes_of_light
* exotic_shards

You can supply multiple groups if you want to. The alias _all_ will select all groups.
