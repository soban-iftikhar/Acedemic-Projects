# Rock Paper Scissors Game - x86 Assembly

A console-based Rock Paper Scissors game implemented in x86 Assembly using the Irvine32 library.

## 📋 Requirements

- **Assembler**: MASM (Microsoft Macro Assembler)
- **Library**: Irvine32.lib
- **Platform**: Windows x86
- **IDE**: Visual Studio or MASM615

## 🎮 How to Play

1. Run the program
2. **Select a game mode:**
   - `1` → Best of 3 (first to 2 wins)
   - `2` → Best of 5 (first to 3 wins)
   - `3` → Unlimited Mode (play until you choose to quit)
3. Choose your move:
   - `1` → Rock
   - `2` → Paper
   - `3` → Scissors
4. The computer will randomly choose its move
5. See the result with colorful output and updated scores
6. In Best of 3/5 modes, the match ends when someone wins the required rounds
7. Choose to play again or exit

## 🏆 Game Rules

- **Rock** beats **Scissors**
- **Scissors** beats **Paper**
- **Paper** beats **Rock**

## 🔧 Compilation

### Using Visual Studio:
1. Create a new project
2. Add `rps_game.asm` to the project
3. Link with `Irvine32.lib`
4. Build and run

### Using MASM615:
\`\`\`bash
ml /c /coff rps_game.asm
link /subsystem:console rps_game.obj Irvine32.lib
\`\`\`

## 📊 Features

- ✅ **Three Game Modes**: Best of 3, Best of 5, and Unlimited
- ✅ **Colorful Output**: Different colors for wins, losses, draws, and UI elements
- ✅ **Match Winner Detection**: Automatic winner announcement in Best of 3/5 modes
- ✅ Input validation with colored error messages
- ✅ Random computer moves using proper RNG
- ✅ Score tracking across rounds
- ✅ Multiple rounds and match support
- ✅ Clear game logic with modular design
- ✅ User-friendly colored interface

## 🎨 Color Scheme

The game uses `SetTextColor` from the Irvine32 library to provide visual feedback:

- **Cyan** - Titles, headers, and player choices
- **Magenta** - Computer choices
- **Green** - Win messages and match victories
- **Red** - Lose messages and errors
- **Yellow** - Draw messages and mode selection
- **Gray** - Score displays
- **White** - Default text

## 🧠 Technical Implementation

- Uses x86 registers (EAX, EBX, ECX, EDX)
- Conditional jumps (JE, JNE, JG, JL, JGE)
- Loops for game continuation and match tracking
- Modular procedures for clean code organization
- Irvine32 library procedures (ReadInt, WriteString, RandomRange, SetTextColor)
- Game mode logic with rounds-to-win tracking
- Color-coded output for enhanced user experience

## 📝 Project Structure

- `README.md` - This file with project overview
- `rps_game.asm` - Main game implementation with all features
- `PROJECT_EXPLANATION.md` - Comprehensive technical documentation

## 👨‍💻 Author

Created for COAL (Computer Organization and Assembly Language) course project.
