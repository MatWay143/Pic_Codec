from function_manager import func_manager

def dec_func (path1):
    cycle = True
    while cycle:
        stereo_image = input("Is the image a stereo picture?\n1)Yes 2)No\n3)Exit\n")
        if stereo_image == "1":
            #if(properties["num_of_channels"] == "1"):
            path2 = input("Specify the address/ URL of the second image:\n").strip()
            #     if(properties["depth_per_channel"] == "1"):
            #         func_manager(path1, path2, properties, 211)
            #     elif(properties["depth_per_channel"]):
            #         func_manager(path1, path2, properties, 212)
            # elif(properties["num_of_channels"] > "1"):
            func_manager(path1, path2, "", 213)
            break
        # elif stereo_image == "2":
        #     if(properties["num_of_channels"] == "1"):
        #         if(properties["depth_per_channel"] == "1"):
        #             func_manager(path1, "", properties, 221)
        #         elif(properties["depth_per_channel"]):
        #             func_manager(path1, "", properties, 222)
        #     elif(properties["num_of_channels"] > "1"):
        #         func_manager(path1, "", properties, 223)
        #     break
        elif stereo_image == "3" | stereo_image == "2":
            print("Exiting the decoding menu.")
            cycle = False
        else:
            print("Invalid option.\n")