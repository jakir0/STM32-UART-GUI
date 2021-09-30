# STM32_USART_GUI
## Tkinter based APP for communication with STM32, used for my master's thesis.
It communicates via USB with STM32 NUCLEO – F446RE in order to control color and brightness of light that is displayed at the end of the PMMA optical fibre. The end of the fibre represents the pixel of display which is to be developed in the future. Using a matrix of optical fibres allows to create water and weather resistant display that can be displaced away from a control unit. 

More info about the project and source code for STM32 at: https://github.com/jakir0/stm32-led-rgb-matrix-driver

![GUI_USART_SECTIONS](https://user-images.githubusercontent.com/83252838/135500417-f280c755-5a79-46d6-a3ba-84b3306a1457.png)

## Main screen sections explained:
1. An image representing the color expected at the end of the fiber after sending the data frame to the STM32 NUCLEO-F446RE (pressing the button in area 8).
1. List of available computer serial ports (COM for Windows).
1. Text information about the connection status with STM32 NUCLEO – F446RE.
1. Text and graphic information about the status of the data frame.
1. Editable fields showing 16-bit RGB channel values of the image in area 1.
1. Button that opens the color wizard window. When the color is selected, it will be tantamount to filling in the fields from area 5 and pressing the button from area 7.
1. Button generating a preview image from area 1 and a data frame for STM32 NUCLEO – F446RE.
1. Button sending the created data frame (until the connection with STM32 NUCLEO-F446RE has been made and the data frame is not generated, the button is inactive and its color remains gray)
 
## Video presentation of an app, working with STM32 to control the pixel of display:
https://user-images.githubusercontent.com/83252838/135508797-46dc0c34-2e1c-430d-bb18-5bd77ed13df5.mp4
