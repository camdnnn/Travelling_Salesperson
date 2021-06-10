# Travelling_Salesperson

This program finds solutions for the travelling salesperson problem by grouping the points into clusters and ordering those clusters individually
instead of trying to order the entirety of the set of all points all at one

If you are able to get the program running and you are reading this page here are the controls

Left Click - Adds a circle at the mouse's position if it does not overlap with another circle
Right Click - Removes circle if they are at the mouse's location

Space - Generates a new set random set of circles equal to in number to the number of circles currently on screen

1 - Orders the circles randomly 
2 - Orders the circles based on the nearest circle
3 - Goes through the first 1 million permutations
0 - Goes through all possible permutations (will not do anything if there are 10 or more circles but that can be changed by changing MAX_SIZE variable)

Left Shift - If held while pressing one of the number keys specified it will do the clustering method previously described while using the function of the number key pressed
