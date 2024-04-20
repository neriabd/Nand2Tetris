// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
	@i
	M=0
	@SCREEN
	D=A
	@R1
	M=D
	
	@KBD
	D=M
	@BLACK
	D;JGT
	@WHITE
	D;JEQ //if no key pressed color screen white 

(BLACK)
	@R1
	D=M
	@KBD
	D=A-D
	@LOOP
	D;JEQ // checks if done coloring screen
	
	@R1
	D=M
	A=D
	M=-1
	@R1
	M=D+1
	
	@BLACK
    0;JMP // turn pixels black loop
	 
(WHITE) 
	@R1
	D=M
	@KBD
	D=A-D
	@LOOP
	D;JEQ // checks if done coloring screen
	
	@R1
	D=M
	A=D
	M=0
	@R1
	M=D+1
	

	
	@WHITE
    0;JMP // turn pixels white loop		
	
	 
