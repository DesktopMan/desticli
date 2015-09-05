# About

Desticli is a command line interface for Destiny. It doesn't do much yet but I already find it useful. Maybe you will as well?

## Installation

Desticli only depends on a recent version the _requests_ library. Install it with _pip_ and you should be good to go.

## Configuration

Only PSN authentication is supported at the moment. Xbox Live might come later.

Required: Copy _config.example_ to _config.py_ and fill in the the fields. Only API key and display name is required. Get the API key at:

https://www.bungie.net/en/user/api

Optional: If you supply your PSN username and password in the config file the script will run without user interaction.

## Usage

Run _./desticli.py -h_ to get usage options.

### normalize - Item normalization

The only feature of Desticli at the moment. Evenly destributes the given items across all your characters. The vault will not be normalized but it must have one free slot.

#### Item groups

Items are organized into groups. The following groups are supported:

* materials - Ascendant Shard, Ascendant Energy, Radiant Shard, Radiant Energy
* resources - Spinmetal, Helium Filaments, Relic Iron, Spirit Bloom
* synths
* telemetries
* glimmer_boosters
* weapon_parts
* strange_coins
* motes_of_light
* exotic_shards

You can supply multiple groups if you want to. The alias _all_ will normalize all groups.

#### Examples

```
./desticli.py normalize all
./desticli.py normalize strange_coins weapon_parts
```
