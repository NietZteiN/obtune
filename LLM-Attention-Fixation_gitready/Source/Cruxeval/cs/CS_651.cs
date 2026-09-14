using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string letter) {
        if (char.IsLower(letter[0]))
        {
            letter = letter.ToUpper();
        }
        StringBuilder new_text = new StringBuilder();
        foreach (char char_ in text)
        {
            new_text.Append(char.ToLower(char_) == letter[0] ? letter : char_.ToString());
        }
        return char.ToUpper(new_text[0]) + new_text.ToString().Substring(1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("E wrestled evil until upperfeat"), ("e")).Equals(("E wrestled evil until upperfeat")));
    }

}
