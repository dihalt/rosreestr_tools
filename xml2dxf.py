import ezdxf
from intersection import is_intersect
from xml_parser import RRxml
from random import choice


class RRxml2dxf():
    def __init__(self, rrxml):
        self.rrxml = rrxml
        self.blocks = self.rrxml.blocks
        self.parcels = self.rrxml.parcels
        self.reversed_blocks = reverse_coords(self.blocks)
        self.reversed_parcels = reverse_coords(self.parcels)
        self.dwg = ezdxf.new('R2000')  # create R2000 drawing
        self.msp = self.dwg.modelspace()  # modelspace for dwg
        self.output_file_path = self.rrxml.file_path.rstrip('xml') + 'dxf'
        self.draw_conturs()
        self.save_dxf()

    def draw_contur(self, dic):
        """ Draws iterables from dictionary to modelspace."""
        for k, v in dic.items():
            # Creating block with name ~ '21 02 000000'
            block_name = k.replace(':', ' ')
            dxf_block = self.dwg.blocks.new(name=block_name)
            # Getting random color for every block
            color = get_random_color()
            # Adding parcels polylines
            for contur in v:
                dxf_block.add_lwpolyline(contur, dxfattribs={'color': color})
            # Adding text description
            text_coord = get_middle_of_contur(v)
            if text_coord:
                print('Adding text at:', text_coord)
                dxf_block.add_text(k,
                                   dxfattribs={'height': 10,
                                               'color': color}).\
                    set_pos((text_coord), align='MIDDLE_CENTER')
            # Adding block to modelspace
            self.msp.add_blockref(block_name, insert=(
                0, 0), dxfattribs={'color': 2})
            print('parcel %s drawed' % (block_name))

    def draw_conturs(self):
        """ Draws blocks and parcels from dictionary to modelspace."""
        self.draw_contur(self.reversed_blocks)
        self.draw_contur(self.reversed_parcels)

    def save_dxf(self):
        self.dwg.saveas(self.output_file_path)


def reverse_coords(dic):
    reversed_result = {}
    for k, v in dic.items():
        reversed_result[k] = []
        for contur in v:
            reversed_result[k].append([])
            for (x, y) in contur:
                reversed_result[k][-1].append((y, x))
    return reversed_result


def get_middle_of_contur(v):
    list_of_x = []
    list_of_y = []
    try:
        for contur in v:
            for x, y in contur:
                list_of_x.append(x)
                list_of_y.append(y)
        mid_x = (max(list_of_x) - min(list_of_x)) / 2 + min(list_of_x)
        mid_y = (max(list_of_y) - min(list_of_y)) / 2 + min(list_of_y)
    except ValueError:
        return tuple()
    return mid_x, mid_y


def get_random_color():
    colors = range(10, 250, 10)
    return choice(colors)


if __name__ == '__main__':
    file_path = '21 02 010103.xml'
    xml = RRxml(file_path)
    print(xml)
    dxf = RRxml2dxf(xml)
