#!/bin/bash
# Datapack CLI Examples
# This script demonstrates how to use the Datapack CLI for various conversions

# Create a directory for output files
mkdir -p output

# Create some sample files for conversion
echo '{
  "title": "Sample JSON Document",
  "author": "Datapack User",
  "data": {
    "items": [
      {"id": 1, "name": "Item 1", "value": 10.5},
      {"id": 2, "name": "Item 2", "value": 20.75}
    ],
    "total": 31.25
  }
}' > sample.json

echo '<?xml version="1.0" encoding="UTF-8"?>
<document>
  <metadata>
    <title>Sample XML Document</title>
    <author>Datapack User</author>
  </metadata>
  <content>
    <section>This is sample XML content</section>
  </content>
</document>' > sample.xml

echo 'id,name,value
1,Item 1,10.5
2,Item 2,20.75
3,Item 3,30.0' > sample.csv

echo 'title: Sample YAML Document
author: Datapack User
data:
  items:
    - id: 1
      name: Item 1
      value: 10.5
    - id: 2
      name: Item 2
      value: 20.75
  total: 31.25' > sample.yaml

echo '---
title: Sample Markdown Document
author: Datapack User
date: 2023-06-01
tags: [markdown, sample, datapack]
---

# Sample Markdown Document

This is a sample markdown document with frontmatter.

## Section 1

Content of section 1.

## Section 2

Content of section 2.' > sample.md

echo "# Datapack CLI Examples"
echo "======================="
echo ""

# Basic conversion examples
echo "Basic Conversion Examples:"
echo "-------------------------"

echo "1. Converting JSON to MDP:"
datapack convert -i sample.json -o output/json_example.mdp
echo ""

echo "2. Converting XML to MDP:"
datapack convert -i sample.xml -o output/xml_example.mdp
echo ""

echo "3. Converting CSV to MDP:"
datapack convert -i sample.csv -o output/csv_example.mdp
echo ""

echo "4. Converting YAML to MDP:"
datapack convert -i sample.yaml -o output/yaml_example.mdp
echo ""

echo "5. Converting Markdown to MDP:"
datapack convert -i sample.md -o output/markdown_example.mdp
echo ""

# Advanced conversion examples
echo "Advanced Conversion Examples:"
echo "---------------------------"

echo "1. Converting CSV with statistics:"
datapack convert -i sample.csv -o output/csv_with_stats.mdp --include-stats
echo ""

echo "2. Converting Markdown with preserved frontmatter:"
datapack convert -i sample.md -o output/markdown_with_frontmatter.mdp --preserve-frontmatter
echo ""

echo "3. Converting JSON with custom metadata:"
datapack convert -i sample.json -o output/json_with_metadata.mdp -m "title=Custom Title,author=Custom Author,tags=[custom,metadata,example]"
echo ""

echo "4. Converting with explicit format specification:"
datapack convert -i sample.yaml -o output/explicit_format.mdp -f yaml
echo ""

# Clean up sample files
echo "Cleaning up sample files..."
rm sample.json sample.xml sample.csv sample.yaml sample.md

echo "All examples completed. Output files are in the './output' directory." 