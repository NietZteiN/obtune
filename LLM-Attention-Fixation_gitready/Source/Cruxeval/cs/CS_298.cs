using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        char[] new_text = text.ToCharArray();
        for (int i = 0; i < new_text.Length; i++)
        {
            char character = new_text[i];
            char new_character = char.IsLower(character) ? char.ToUpper(character) : char.ToLower(character);
            new_text[i] = new_character;
        }
        return new string(new_text);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dst vavf n dmv dfvm gamcu dgcvb.")).Equals(("DST VAVF N DMV DFVM GAMCU DGCVB.")));
    }

}
