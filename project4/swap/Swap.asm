// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

	@R15
	D=M
	@END
	D;JEQ
	
	@R14
	D=M
	@16383
	D=A
	@max
	M=-D
	@min
	M=D
	
	@R14
	D=M
	@min_add
	M=D
	@max_add
	M=D

	@i
	M=0
	
	
	
(LOOP)
	@i
	D=M
	@R15
	D=M-D
	@SWITCH
	D;JEQ //checks if loop is done
	
	
	@R14
	D=M
	@i
	D=D+M
	A=D
	D=M
	@min
	D=D-M
	@MIN
	D;JLT // if smaller then min changes min
	
	@R14
	D=M
	@i
	D=D+M
	A=D
	D=M
	@max
	D=D-M
	@MAX
	D;JGT // if bigger then max changes max

	@i
	M=M+1 // increases loop index

	@LOOP
	0;JMP // goes back to loop
	
(MIN)
	@R14
	D=M
	@i
	D=D+M
	A=D
	D=M
	@min
	M=D //switches min
	
	@R14
	D=M
	@i
	D=D+M
	@min_add
	M=D // switches min address

	@R14
	D=M
	@i
	D=D+M
	A=D
	D=M
	@max
	D=D-M
	@MAX
	D;JGT // if bigger then max changes max
	
	@i
	M=M+1 // increases loop index

	@LOOP
	0;JMP // goes back to loop


(MAX)	
	@R14
	D=M
	@i
	D=D+M
	A=D
	D=M
	@max
	M=D // switches max
	
	@R14
	D=M
	@i
	D=D+M
	@max_add
	M=D // switches max address

	@i
	M=M+1 // increases loop index

	@LOOP
	0;JMP // goes back to loop


(SWITCH)
	@min
	D=M
	@tmp2
	M=D
	
	@max
	D=M
	@tmp
	M=D

	@tmp
	D=M
	@min_add
	A=M
	M=D
	
	@tmp2
	D=M
	@max_add
	A=M
	M=D

(END)
	@END
	0;JMP