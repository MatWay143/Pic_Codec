from function_manager import func_manager

def enc_func (path1, properties):
    cycle = True
    while cycle:
        stereo_image = input("Is the image a stereo picture?\n1)Yes 2)No\n3)Exit\n")
        if stereo_image == "1":
            path2 = input("Specify the address/ URL of the second image:\n").strip()
            if(int(properties["num_of_channels"]) == 1):
                if(int(properties["depth_per_channel"]) == 1):
                    func_manager(path1, path2, properties, 111)
                else:
                    func_manager(path1, path2, properties, 112)
            elif(int(properties["num_of_channels"]) > 1):
                func_manager(path1, path2, properties, 113)
            break
        elif stereo_image == "2":
            if((int(properties["num_of_channels"])) == 1):
                if(int(properties["depth_per_channel"]) == 1):
                    func_manager(path1, "", properties, 121)
                else:
                    func_manager(path1, "", properties, 122)
            elif(int(properties["num_of_channels"]) > 1):
                func_manager(path1, "", properties, 123)
            break
        elif stereo_image == "3":
            print("Exiting the encoding menu.")
            cycle = False
        else:
            print("Invalid option.\n")