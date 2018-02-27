import ezdxf
from intersection import is_intersect
from os import path


class RRxml2dxf():
    def __init__(self, rrxml, settings):
        self.rrxml = rrxml
        self.settings = settings
        self.blocks = self.rrxml.blocks
        self.parcels = self.rrxml.parcels
        self.reversed_blocks = reverse_coords(self.blocks)
        self.reversed_parcels = reverse_coords(self.parcels)
        self.output_file_path = path.join(
            self.settings.dxf_folder_path,
            self.rrxml.basename_file_path.replace('.xml', '.dxf'))

    def draw_contur(self, dic):
        """ Draws iterables from dictionary to modelspace.
        CAUTION: Use with reversed coordinates"""
        for k, v in dic.items():
            # Creating block with name ~ '21 02 000000'
            block_name = k.replace(':', ' ')
            dxf_block = self.dwg.blocks.new(name=block_name)
            # Getting random color for every block
            color = self.settings.get_next_color()
            # Adding parcels polylines
            for contur in v:
                dxf_block.add_lwpolyline(contur, dxfattribs={'color': color})
            # Adding text description
            text_attrib = get_text_attrib(v)
            if text_attrib:
                text_coords, text_height = text_attrib
                print('Adding text at: %s with height %s ' %
                      (text_coords, text_height))
                dxf_block.add_text(k,
                                   dxfattribs={'height': text_height,
                                               'color': color}).\
                    set_pos((text_coords), align='MIDDLE_CENTER')
            # Adding block to modelspace
            self.msp.add_blockref(block_name, insert=(
                0, 0), dxfattribs={'color': 2})
            print('parcel %s drawed' % (k))

    def draw_conturs(self):
        """ Draws blocks and parcels from dictionary to modelspace.
        Needed for save_dxf function"""
        self.dwg = ezdxf.new('R2000')  # create R2000 drawing
        self.msp = self.dwg.modelspace()  # modelspace for dwg
        self.draw_contur(self.reversed_blocks)
        self.draw_contur(self.reversed_parcels)

    def save_dxf(self):
        """ Draws all items to dxf files """
        self.draw_conturs()
        self.dwg.saveas(self.output_file_path)


def reverse_coords(dic):
    """ Getting reverse coords, need for dxf file """
    reversed_result = {}
    for k, v in dic.items():
        reversed_result[k] = []
        for contur in v:
            reversed_result[k].append([])
            for (x, y) in contur:
                reversed_result[k][-1].append((y, x))
    return reversed_result


def get_text_attrib(v):
    """ Calculating some text_attribs like coordinates and height,
    based on contur coordinates """
    list_of_x = []
    list_of_y = []
    try:
        for contur in v:
            for x, y in contur:
                list_of_x.append(x)
                list_of_y.append(y)
        max_x, max_y = max(list_of_x), max(list_of_y)
        min_x, min_y = min(list_of_x), min(list_of_y)
        mid_x = (max_x - min_x) / 2 + min_x
        mid_y = (max_y - min_y) / 2 + min_y
    except ValueError:
        return None
    average_diff = ((max_x - mid_x) + (max_y - mid_y)) / 2
    height = min(average_diff / 5, 25)
    return (int(mid_x), int(mid_y)), height


def merge_dxfs(settings):
    """ Merging all dxfs from settings.dxf_folder_path into merged.dxf"""
    dxf_list = settings.get_dxf_list()
    # Creating clear dxf file
    dwg = ezdxf.new('R2000')
    merged_path = path.join(settings.dxf_folder_path, 'merged.dxf')
    dwg.saveas(merged_path)
    # Merging
    for dxf in dxf_list:
        source_dwg = ezdxf.readfile(dxf)
        target_dwg = ezdxf.readfile(merged_path)
        importer = ezdxf.Importer(source_dwg, target_dwg)
        importer.import_all()
        target_dwg.save()
        print('%s added' % (dxf))