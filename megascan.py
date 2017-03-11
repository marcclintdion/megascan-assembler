from PIL import Image
import sys, os
import zipfile

def do_normal_map(directoryPath, familyRoot):
    # pkfg22_4K_Normal.jpg -> pkfg22_4K_n.tga
    jpg_path = os.path.join(directoryPath, familyRoot + "Normal.jpg")
    if not os.path.exists(jpg_path):
        print('Normal map file is missing: %s' % jpg_path)
        sys.exit(1)

    tga_path = familyRoot + "n.tga"
    Image.open(jpg_path).save(tga_path)
    print(" -> Normal map at %s" % tga_path)
    return tga_path

def do_albedo_displacement(directoryPath, familyRoot):
    # pkfg22_4K_Albedo.jpg (RGB) + pkfg22_4K_Displacement.jpg (A)
    albedo_jpg_path = os.path.join(directoryPath, familyRoot + "Albedo.jpg")
    displacement_jpg_path = os.path.join(directoryPath, familyRoot + "Displacement.jpg")
    if not os.path.exists(albedo_jpg_path):
        print('Albedo file is missing: %s' % albedo_jpg_path)
        sys.exit(1)
    if not os.path.exists(displacement_jpg_path):
        print('Displacement map file is missing: %s' % displacement_jpg_path)
        sys.exit(1)

    output_tga_path = familyRoot + "a_d.tga"
    with Image.open(albedo_jpg_path) as albedo_src:
        with Image.open(displacement_jpg_path) as displacement_src:
            displacement_alpha = displacement_src.split()[0]
            with Image.new("RGBA", albedo_src.size) as output:
                output.paste(albedo_src)
                output.putalpha(displacement_alpha)
                output.save(output_tga_path)
                print(" -> Albedo/Displacement map at %s" % output_tga_path)
    return output_tga_path

def do_compact_ao(directoryPath, familyRoot):
    # pkfg22_4K_Metallic.jpg (R, optional) +
    # pkfg22_4K_Roughness.jpg (G, mandatory) +
    # pkfg22_4K_Cavity.jpg (B, mandatory) +
    # pkfg22_4K_AO.jpg (A, mandatory) +
    metallic_jpg_path = os.path.join(directoryPath, familyRoot + "Metallic.jpg")
    roughness_jpg_path = os.path.join(directoryPath, familyRoot + "Roughness.jpg")
    cavity_jpg_path = os.path.join(directoryPath, familyRoot + "Cavity.jpg")
    ao_jpg_path = os.path.join(directoryPath, familyRoot + "AO.jpg")
    if not os.path.exists(roughness_jpg_path): print('Roughness map is missing: %s' % roughness_jpg_path); sys.exit(1)
    if not os.path.exists(cavity_jpg_path): print('Cavity map is missing: %s' % cavity_jpg_path); sys.exit(1)
    if not os.path.exists(ao_jpg_path): print('AO map is missing: %s' % ao_jpg_path); sys.exit(1)

    output_tga_path = familyRoot + "m_r_c_ao.tga"

    with Image.open(ao_jpg_path) as ao_src:
        with Image.open(cavity_jpg_path) as cavity_src:
            with Image.open(roughness_jpg_path) as roughness_src:
                if os.path.exists(metallic_jpg_path):
                    # this set has a metallic
                    metallic_src = Image.open(metallic_jpg_path)
                else:
                    # no metallic, use a stub black one
                    metallic_src = Image.new('RGBA', ao_src.size)

                output = Image.merge("RGBA", (metallic_src.split()[0], roughness_src.split()[0], cavity_src.split()[0], ao_src.split()[0]))
                output.save(output_tga_path)
                print(" -> M/R/C/AO map at %s" % output_tga_path)

                metallic_src.close()
    return output_tga_path

def get_family_root(directoryPath):
    # figure out who the albedo is
    albedo_path = next(f for f in os.listdir(directoryPath) if "albedo" in f.lower())
    if albedo_path == None:
        print('Could not find an albedo file in directory %s. Aborting.' % directoryPath)
    albedo_idx = albedo_path.lower().find("albedo")
    return albedo_path[:albedo_idx]

def handle_directory(directoryPath):
    if not os.path.isdir(directoryPath):
        print('Directory %s does not exist. Aborting.' % (directoryPath))
        sys.exit(1)
    family_root = get_family_root(directoryPath)
    print('Handling family at %s' % family_root)
    normal_map_path = do_normal_map(directoryPath, family_root)
    ad_path = do_albedo_displacement(directoryPath, family_root)
    compact_path = do_compact_ao(directoryPath, family_root)
    archive_family(family_root, [normal_map_path, ad_path, compact_path])

def archive_family(family_root, paths):
    zipname = family_root.strip("-_ ") + ".zip"
    with zipfile.ZipFile(zipname, mode = 'w') as z:
        for path in paths:
            z.write(path)
    print(' ~> Generated zip archive of %s called %s' % (family_root, zipname))

def printUsage():
    print('Usage: %s [directories]' % (sys.argv[0]))

def main():
    if len(sys.argv) < 2:
        printUsage()
        sys.exit(1)
    for d in sys.argv[1:]:
        handle_directory(d)

if __name__ == '__main__': main()
