using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static bool F(string text, string character) {
        return character.ToLower().Equals(character) && text.ToLower().Equals(text);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abc"), ("e")) == (true));
    }

}
