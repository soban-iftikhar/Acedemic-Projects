INCLUDE Irvine32.inc

.data
    ; Game title and menu
    titleMsg BYTE "========================================", 0dh, 0ah
             BYTE "  ROCK PAPER SCISSORS GAME", 0dh, 0ah
             BYTE "========================================", 0dh, 0ah, 0
    
    ; Added game mode selection menu
    modeMsg BYTE 0dh, 0ah, "Select Game Mode:", 0dh, 0ah
            BYTE "1 - Best of 3", 0dh, 0ah
            BYTE "2 - Best of 5", 0dh, 0ah
            BYTE "3 - Unlimited Mode", 0dh, 0ah
            BYTE "Enter your choice: ", 0
    
    menuMsg BYTE 0dh, 0ah, "Choose your move:", 0dh, 0ah
            BYTE "1 - Rock", 0dh, 0ah
            BYTE "2 - Paper", 0dh, 0ah
            BYTE "3 - Scissors", 0dh, 0ah
            BYTE "Enter your choice: ", 0
    
    ; Choice display messages
    yourChoice BYTE "Your choice: ", 0
    compChoice BYTE "Computer choice: ", 0
    
    ; Move names
    rockStr BYTE "Rock", 0
    paperStr BYTE "Paper", 0
    scissorsStr BYTE "Scissors", 0
    
    ; Result messages
    winMsg BYTE 0dh, 0ah, "*** YOU WIN! ***", 0dh, 0ah, 0
    loseMsg BYTE 0dh, 0ah, "*** YOU LOSE! ***", 0dh, 0ah, 0
    drawMsg BYTE 0dh, 0ah, "*** IT'S A DRAW! ***", 0dh, 0ah, 0
    
    ; Added match winner messages
    matchWinMsg BYTE 0dh, 0ah, 0dh, 0ah, "========================================", 0dh, 0ah
                BYTE "  YOU WON THE MATCH!", 0dh, 0ah
                BYTE "========================================", 0dh, 0ah, 0

    matchLoseMsg BYTE 0dh, 0ah, 0dh, 0ah, "========================================", 0dh, 0ah
                 BYTE "  COMPUTER WON THE MATCH!", 0dh, 0ah
                 BYTE "========================================", 0dh, 0ah, 0
    
    ; Score messages
    scoreMsg BYTE 0dh, 0ah, "CURRENT SCORE:", 0dh, 0ah
             BYTE "Player: ", 0
    computerScoreMsg BYTE " | Computer: ", 0
    roundsMsg BYTE " | Rounds to Win: ", 0
    
    ; Play again prompt
    playAgainMsg BYTE 0dh, 0ah, 0dh, 0ah, "Do you want to play again? (1=Yes, 0=No): ", 0
    
    ; Final score
    finalScoreMsg BYTE 0dh, 0ah, 0dh, 0ah, "========================================", 0dh, 0ah
                  BYTE "  FINAL SCORE", 0dh, 0ah
                  BYTE "========================================", 0dh, 0ah
                  BYTE "Player: ", 0
    thanksMsg BYTE 0dh, 0ah, "Thanks for playing!", 0dh, 0ah, 0
    
    ; Error messages
    invalidMsg BYTE "Invalid input! Please enter a valid option.", 0dh, 0ah, 0
    
    ; color constants 
    COLOR_WHITE = 15
    COLOR_CYAN = 11
    COLOR_YELLOW = 14
    COLOR_GREEN = 10
    COLOR_RED = 12
    COLOR_MAGENTA = 13
    COLOR_LIGHT_BLUE = 9
    
    ; Game variables
    playerScore DWORD 0
    computerScore DWORD 0
    playerMove DWORD ?
    computerMove DWORD ?
    gameMode DWORD ?          ; 1=Best of 3, 2=Best of 5, 3=Unlimited
    roundsToWin DWORD ?       ; Rounds needed to win the match

.code
main PROC
    ; Set title color to cyan
    mov eax, COLOR_CYAN
    call SetTextColor
    
    ; Display title
    mov edx, OFFSET titleMsg
    call WriteString
    
    ; change color to white
    mov eax, COLOR_WHITE
    call SetTextColor
    
    ; Initialize random number generator
    call Randomize
    
    ; Get game mode selection
    call SelectGameMode
    mov gameMode, eax
    
    ; Set rounds to win based on mode
    cmp eax, 1
    je SetBest3
    cmp eax, 2
    je SetBest5
    mov roundsToWin, 999      ; Unlimited mode (high number)
    jmp GameLoop
    
SetBest3:
    mov roundsToWin, 2        ; Need 2 wins in Best of 3
    jmp GameLoop
    
SetBest5:
    mov roundsToWin, 3        ; Need 3 wins in Best of 5

GameLoop:
    ; Get player input
    call GetPlayerMove
    mov playerMove, eax
    
    ; Generate computer move
    call GetComputerMove
    mov computerMove, eax
    
    ; Display choices
    call DisplayChoices
    
    ; Determine winner
    call DetermineWinner
    
    ; Display scores
    call DisplayScores
    
    ; Check if match is over (Best of 3/5 mode)
    mov eax, gameMode
    cmp eax, 3
    je AskPlayAgain           ; Unlimited mode, always ask
    
    ; Check if someone won the match
    mov eax, playerScore
    cmp eax, roundsToWin
    jge PlayerWonMatch
    
    mov eax, computerScore
    cmp eax, roundsToWin
    jge ComputerWonMatch
    
    ; Match not over, continue
    jmp GameLoop
    
PlayerWonMatch:
    ; Display match winner in green
    mov eax, COLOR_GREEN
    call SetTextColor
    mov edx, OFFSET matchWinMsg
    call WriteString
    mov eax, COLOR_WHITE
    call SetTextColor
    jmp AskPlayAgain
    
ComputerWonMatch:
    ; Display match loser in red
    mov eax, COLOR_RED
    call SetTextColor
    mov edx, OFFSET matchLoseMsg
    call WriteString
    mov eax, COLOR_WHITE
    call SetTextColor
    
AskPlayAgain:
    ; Ask to play again
    mov edx, OFFSET playAgainMsg
    call WriteString
    call ReadInt
    
    cmp eax, 1
    jne ExitGame
    
    ; Reset scores and get new mode
    mov playerScore, 0
    mov computerScore, 0
    
    ; Set title color to cyan
    mov eax, COLOR_CYAN
    call SetTextColor
    mov edx, OFFSET titleMsg
    call WriteString
    mov eax, COLOR_WHITE
    call SetTextColor
    
    call SelectGameMode
    mov gameMode, eax
    
    cmp eax, 1
    je ResetBest3
    cmp eax, 2
    je ResetBest5
    mov roundsToWin, 999
    jmp GameLoop
    
ResetBest3:
    mov roundsToWin, 2
    jmp GameLoop
    
ResetBest5:
    mov roundsToWin, 3
    jmp GameLoop
    
ExitGame:
    ; Display final scores and exit
    call DisplayFinalScores
    
    exit
main ENDP


; SelectGameMode Procedure
; Displays game mode menu and gets selection
; Returns: EAX = game mode (1-3)

SelectGameMode PROC
    ModeLoop:
        ; Display mode selection in yellow
        mov eax, COLOR_YELLOW
        call SetTextColor
        mov edx, OFFSET modeMsg
        call WriteString
        mov eax, COLOR_WHITE
        call SetTextColor
        
        call ReadInt
        
        ; Validate input (1-3)
        cmp eax, 1
        jl InvalidMode
        cmp eax, 3
        jg InvalidMode
        
        ret
        
    InvalidMode:
        mov eax, COLOR_RED
        call SetTextColor
        mov edx, OFFSET invalidMsg
        call WriteString
        mov eax, COLOR_WHITE
        call SetTextColor
        jmp ModeLoop
        
SelectGameMode ENDP


; GetPlayerMove Procedure
; Gets and validates player input
; Returns: EAX = player move (1-3)

GetPlayerMove PROC
    InputLoop:
        mov edx, OFFSET menuMsg
        call WriteString
        call ReadInt
        
        ; Validate input (1-3)
        cmp eax, 1
        jl InvalidInput
        cmp eax, 3
        jg InvalidInput
        
        ret
        
    InvalidInput:
        ; Display error in red
        mov eax, COLOR_RED
        call SetTextColor
        mov edx, OFFSET invalidMsg
        call WriteString
        mov eax, COLOR_WHITE
        call SetTextColor
        jmp InputLoop
        
GetPlayerMove ENDP


; GetComputerMove Procedure
; Generates random computer move
; Returns: EAX = computer move (1-3)

GetComputerMove PROC
    mov eax, 3          ; Range 0-2
    call RandomRange    ; EAX = 0, 1, or 2
    inc eax             ; Convert to 1-3
    ret
GetComputerMove ENDP


; DisplayChoices Procedure
; Displays player and computer choices

DisplayChoices PROC
    call Crlf
    
    ; Display player choice in cyan
    mov eax, COLOR_CYAN
    call SetTextColor
    mov edx, OFFSET yourChoice
    call WriteString
    mov eax, playerMove
    call DisplayMoveName
    call Crlf
    
    ; Display computer choice in magenta
    mov eax, COLOR_MAGENTA
    call SetTextColor
    mov edx, OFFSET compChoice
    call WriteString
    mov eax, computerMove
    call DisplayMoveName
    call Crlf
    
    ; Reset color
    mov eax, COLOR_WHITE
    call SetTextColor
    
    ret
DisplayChoices ENDP


; DisplayMoveName Procedure
; Displays the name of a move
; Receives: EAX = move number (1-3)

DisplayMoveName PROC
    cmp eax, 1
    je ShowRock
    cmp eax, 2
    je ShowPaper
    cmp eax, 3
    je ShowScissors
    
ShowRock:
    mov edx, OFFSET rockStr
    jmp DisplayIt
    
ShowPaper:
    mov edx, OFFSET paperStr
    jmp DisplayIt
    
ShowScissors:
    mov edx, OFFSET scissorsStr
    
DisplayIt:
    call WriteString
    ret
DisplayMoveName ENDP


; DetermineWinner Procedure
; Compares moves and updates scores

DetermineWinner PROC
    mov eax, playerMove
    mov ebx, computerMove
    
    ; Check for draw
    cmp eax, ebx
    je IsDraw
    
    ; Check player win conditions
    ; Rock (1) beats Scissors (3)
    cmp eax, 1
    jne CheckPaper
    cmp ebx, 3
    je PlayerWins
    jmp ComputerWins
    
CheckPaper:
    ; Paper (2) beats Rock (1)
    cmp eax, 2
    jne CheckScissors
    cmp ebx, 1
    je PlayerWins
    jmp ComputerWins
    
CheckScissors:
    ; Scissors (3) beats Paper (2)
    cmp eax, 3
    jne ComputerWins
    cmp ebx, 2
    je PlayerWins
    jmp ComputerWins
    
PlayerWins:
    inc playerScore
    ; Display win message in green
    mov eax, COLOR_GREEN
    call SetTextColor
    mov edx, OFFSET winMsg
    call WriteString
    mov eax, COLOR_WHITE
    call SetTextColor
    jmp DoneChecking
    
ComputerWins:
    inc computerScore
    ; Display lose message in red
    mov eax, COLOR_RED
    call SetTextColor
    mov edx, OFFSET loseMsg
    call WriteString
    mov eax, COLOR_WHITE
    call SetTextColor
    jmp DoneChecking
    
IsDraw:
    ; Display draw message in yellow
    mov eax, COLOR_YELLOW
    call SetTextColor
    mov edx, OFFSET drawMsg
    call WriteString
    mov eax, COLOR_WHITE
    call SetTextColor
    
DoneChecking:
    ret
DetermineWinner ENDP

; DisplayScores Procedure
; Displays current scores

DisplayScores PROC
    ; Display scores in gray
    mov eax, COLOR_GRAY
    call SetTextColor
    
    mov edx, OFFSET scoreMsg
    call WriteString
    
    mov eax, playerScore
    call WriteDec
    
    mov edx, OFFSET computerScoreMsg
    call WriteString
    
    mov eax, computerScore
    call WriteDec
    
    ; Display rounds to win if not unlimited
    mov eax, gameMode
    cmp eax, 3
    je SkipRounds
    
    mov edx, OFFSET roundsMsg
    call WriteString
    mov eax, roundsToWin
    call WriteDec
    
SkipRounds:
    call Crlf
    
    ; Reset color
    mov eax, COLOR_WHITE
    call SetTextColor
    
    ret
DisplayScores ENDP


; DisplayFinalScores Procedure
; Displays final scores before exit

DisplayFinalScores PROC
    ; Display final score in cyan
    mov eax, COLOR_CYAN
    call SetTextColor
    
    mov edx, OFFSET finalScoreMsg
    call WriteString
    
    mov eax, playerScore
    call WriteDec
    
    mov edx, OFFSET computerScoreMsg
    call WriteString
    
    mov eax, computerScore
    call WriteDec
    call Crlf
    
    mov edx, OFFSET thanksMsg
    call WriteString
    
    ; Reset color
    mov eax, COLOR_WHITE
    call SetTextColor
    
    ret
DisplayFinalScores ENDP

END main
