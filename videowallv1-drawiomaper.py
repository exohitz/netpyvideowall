import xml.etree.ElementTree as ET
import json


def extract_tiles_from_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tiles = []

        # Find all mxCell elements with a vertex attribute
        for cell in root.findall('.//mxCell[@vertex="1"]'):
            tile = {}
            tile['id'] = cell.attrib.get('id')

            # Extract tile name from the value attribute
            value = cell.attrib.get('value', '')
            start = value.find('Tile')
            if start != -1:
                end = start + 6  # TileXX has a fixed length of 6 characters
                tile['name'] = value[start:end]
            else:
                tile['name'] = 'Unknown'

            # Find the mxGeometry element inside the cell
            geometry = cell.find('.//mxGeometry')
            if geometry is not None:
                tile['x'] = int(float(geometry.attrib.get('x', '0')))
                tile['y'] = int(float(geometry.attrib.get('y', '0')))
                tile['width'] = int(float(geometry.attrib.get('width', '0')))
                tile['height'] = int(float(geometry.attrib.get('height', '0')))

            # Extract rotation from the style attribute
            style = cell.attrib.get('style', '')
            rotation = '0'  # Default rotation
            if 'rotation=' in style:
                rotation_start = style.find('rotation=') + len('rotation=')
                rotation_end = style.find(';', rotation_start)
                if rotation_end == -1:
                    rotation_end = len(style)
                rotation = style[rotation_start:rotation_end]
                tile['rotation'] = int(rotation)
            else:
                tile['rotation'] = 0

            tiles.append(tile)

        # Convert to JSON and return
        return json.dumps(tiles, indent=4)

    except Exception as e:
        print(f"Error processing XML: {e}")
        return None


# Example usage
if __name__ == "__main__":
    xml_file = "input2.xml"  # Update with your file path
    result = extract_tiles_from_xml(xml_file)
    if result:
        print("Generated JSON:")
        print(result)
        with open("tiles.json", "w") as outfile:
            outfile.write(result)
        print("JSON saved to tiles.json.")
