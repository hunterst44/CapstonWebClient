import ux


#Will train a model based on sensor data stored in a folder. Puts model.model in the directory chosen.

def main():

    myUx = ux.UX()

    myUx.trainLoggedData('data/test')

if __name__ == "__main__": main()