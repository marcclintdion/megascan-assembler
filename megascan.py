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

def printUsage():
    print 'Usage: %s [directories]' % (sys.argv[0])

def main():
    if len(sys.argv) < 2:
        printUsage()
        sys.exit(1)
    for d in sys.argv[1:]:
        handle_directory(d)

if __name__ == '__main__': main()