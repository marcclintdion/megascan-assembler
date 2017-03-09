from PIL import Image
import sys, os

def do_normal_map(directoryPath, familyRoot):
    # pkfg22_4K_Normal.jpg -> pkfg22_4K_n.tga
    jpg_path = os.path.join(directoryPath, familyRoot + "Normal.jpg")
    if not os.path.exists(jpg_path):
        print 'Normal map file is missing: %s' % jpg_path
        sys.exit(1)
    
    tga_path = familyRoot + "n.tga"
    Image.open(jpg_path).save(tga_path)
    print " -> Normal map at %s" % tga_path
    
def do_albedo_displacement(directoryPath, familyRoot):
    # pkfg22_4K_Albedo.jpg (RGB) + pkfg22_4K_Displacement.jpg (A)
    albedo_jpg_path = os.path.join(directoryPath, familyRoot + "Albedo.jpg")
    displacement_jpg_path = os.path.join(directoryPath, familyRoot + "Displacement.jpg")    
    if not os.path.exists(albedo_jpg_path):
        print 'Albedo file is missing: %s' % albedo_jpg_path
        sys.exit(1)
    if not os.path.exists(displacement_jpg_path):
        print 'Displacement map file is missing: %s' % displacement_jpg_path
        sys.exit(1)
        
    output_tga_path = familyRoot + "a_d.tga"
    with Image.open(albedo_jpg_path) as albedo_src:
        with Image.open(displacement_jpg_path) as displacement_src:
            displacement_alpha = displacement_src.split()[0]            
            with Image.new("RGBA", albedo_src.size) as output:
                output.paste(albedo_src)
                output.putalpha(displacement_alpha)
                output.save(output_tga_path)
                print " -> Albedo/Displacement map at %s" % output_tga_path
                
def do_compact_ao(directoryPath, familyRoot):
    # pkfg22_4K_Metallic.jpg (R, optional) +
    # pkfg22_4K_Roughness.jpg (G, mandatory) +
    # pkfg22_4K_Cavity.jpg (B, mandatory) +
    # pkfg22_4K_AO.jpg (A, mandatory) +
    metallic_jpg_path = os.path.join(directoryPath, familyRoot + "Metallic.jpg")
    roughness_jpg_path = os.path.join(directoryPath, familyRoot + "Roughness.jpg")
    cavity_jpg_path = os.path.join(directoryPath, familyRoot + "Cavity.jpg")
    ao_jpg_path = os.path.join(directoryPath, familyRoot + "AO.jpg")
    if not os.path.exists(roughness_jpg_path): print 'Roughness map is missing: %s' % roughness_jpg_path; sys.exit(1)
    if not os.path.exists(cavity_jpg_path): print 'Cavity map is missing: %s' % cavity_jpg_path; sys.exit(1)
    if not os.path.exists(ao_jpg_path): print 'AO map is missing: %s' % ao_jpg_path; sys.exit(1)
    with Image.open(ao_jpg_path) as ao_src:
        ao_pixels = ao_src.load()
        with Image.open(cavity_jpg_path) as cavity_src:
            cavity_pixels = cavity_src.load()
            with Image.open(roughness_jpg_path) as roughness_src:
                roughness_pixels = roughness_src.load()
                if os.path.exists(metallic_jpg_path):
                    # this set has a metallic
                    metallic_src = Image.open(metallic_jpg_path)
                else:
                    # no metallic, use a stub black one
                    metallic_src = Image.new('RGBA', ao_src.size)
                metallic_pixels = metallic_src.load()
                
                with Image.new('RGBA', ao_src.size) as output:
                    output_pixels = output.load()
                    # fill in R, G, B... and A
                    for i in range(output.size[0]):
                        for j in range(output.size[1]):
                            r = metallic_pixels[i, j][0]
                            g = roughness_pixels[i, j][0]
                            b = cavity_pixels[i, j][0]
                            a = ao_pixels[i, j][0]
                            output_pixels[i, j] = (r, g, b, a)
                    # save
                    output_tga_path = familyRoot + "s_r_c_ao.tga"
                    output.save(output_tga_path)
                    print " -> S/R/C/AO map at %s" % output_tga_path
                metallic_src.close()

def get_family_root(directoryPath):
    # figure out who the albedo is
    albedo_path = next(f for f in os.listdir(directoryPath) if "albedo" in f.lower())
    if albedo_path == None:
        print 'Could not find an albedo file in directory %s. Aborting.' % directoryPath
    albedo_idx = albedo_path.lower().find("albedo")
    return albedo_path[:albedo_idx]

def handle_directory(directoryPath):
    if not os.path.isdir(directoryPath):
        print 'Directory %s does not exist. Aborting.' % (directoryPath)
        sys.exit(1)
    family_root = get_family_root(directoryPath)
    print 'Handling family at %s' % family_root
    do_normal_map(directoryPath, family_root)
    do_albedo_displacement(directoryPath, family_root)
    do_compact_ao(directoryPath, family_root)

def printUsage():
    print 'Usage: %s [directories]' % (sys.argv[0])

def main():
    if len(sys.argv) < 2:
        printUsage()
        sys.exit(1)
    for d in sys.argv[1:]:
        handle_directory(d)

if __name__ == '__main__': main()