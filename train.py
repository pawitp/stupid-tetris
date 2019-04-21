# -*- coding: utf-8 -*-
import gestureCNN as myNN

def main():
    mod = myNN.loadCNN(-1)
    myNN.trainModel(mod)

if __name__ == "__main__":
    main()

