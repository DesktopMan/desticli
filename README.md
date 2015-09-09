# About

Desticli is a command line interface for Destiny. It's main focus is to help you manage item stacks easily. The script can be configured to run without user interaction. Only PSN authentication is supported at the moment. Xbox Live might come later.

## Installation

Desticli only depends on a recent version the _requests_ library. Install it with _pip_ and you should be good to go.

## Configuration

Copy _config.example_ to _config.py_ and fill in the the fields. Only API key and display name is required. Get the API key at:

https://www.bungie.net/en/user/api

Optional: If you supply your PSN username and password in the config file the script will run without user interaction.

## Usage

Run _./desticli.py -h_ to get usage options.

See item groups below for a list of supported groups.

### normalize - Item normalization

Evenly destributes the given items across all your characters. The vault will not be normalized but it must have one free general slot.

```
./desticli.py normalize all
./desticli.py normalize weapon_parts armor_materials
```

### move - Move items to character/vault

Only vault is supported at the moment. Characters will come soon.

```
./desticli.py move vault all
./desticli.py move vault weapon_parts armor_materials
```

## Item groups

Items are organized into groups. The following groups are supported for all commands:

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
